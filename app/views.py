from typing import Tuple, Optional, List, Dict
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import base64
import io
import os
import pytz
import cv2
import json
import numpy as np

from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.conf import settings
from dotenv import load_dotenv

from .utils import DifyAPI
from .models import ExchangeRate, UsageStatistics, LearningProgress
from .middlewares import check_feature_access, increment_feature_usage
from .currencies import SUPPORTED_CURRENCIES, CURRENCY_CODES, get_currency_info, get_currency_symbol
from .services.exchange_rate_service import ExchangeRateService, GraphService
from .services.image_recognition_service import ImageRecognitionService
from .validators import CurrencyValidator, ImageValidator

load_dotenv()

# Initialize the DifyAPI for AI chat functionality
dify_api = DifyAPI()

# Set up logging to track errors and debug information
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize image recognition service
image_recognition_service = ImageRecognitionService()

def home(request):
    """
    Main view function for the homepage.
    Displays the exchange rate graph and latest rate.
    """
    try:
        plt.clf()
        plt.close('all')
        
        # Get exchange rate data
        rates = ExchangeRateService.get_exchange_rate_data()
        if not rates:
            context = {
                'error_message': 'Failed to fetch data.',
                'graph_data': None
            }
            return render(request, 'app/home.html', context)

        # Generate the graph
        graph_data, latest_rate, last_updated = GraphService.generate_graph(rates)
        if not graph_data:
            context = {
                'error_message': 'Failed to generate graph.',
                'graph_data': None
            }
            return render(request, 'app/home.html', context)

        # Prepare data for the template
        context = {
            'graph_data': graph_data,
            'latest_rate': latest_rate,
            'last_updated': last_updated,
            'error_message': None
        }
        
        return render(request, 'app/home.html', context)
    
    except Exception as e:
        logger.error(f"Error in home view: {e}")
        context = {
            'error_message': 'An unexpected error occurred.',
            'graph_data': None
        }
        return render(request, 'app/home.html', context)

@never_cache
def get_updated_graph(request):
    """
    AJAX endpoint to update the exchange rate graph without reloading the page.
    Returns JSON containing the new graph data, latest rate, and timestamp.
    """
    try:
        rates = ExchangeRateService.get_exchange_rate_data()
        if not rates:
            return JsonResponse({'error': 'Failed to fetch data'}, status=400)

        graph_data, latest_rate, last_updated = GraphService.generate_graph(rates)
        if not graph_data:
            return JsonResponse({'error': 'Failed to generate graph'}, status=400)

        return JsonResponse({
            'graph_data': graph_data,
            'latest_rate': latest_rate,
            'last_updated': last_updated
        })
    except Exception as e:
        logger.error(f"Error updating graph: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def image_recognition(request):
    """
    View for the image recognition page.
    CSRF exempt to allow image uploads from the frontend.
    """
    return render(request, 'app/image_recognition.html')

@csrf_exempt
def start_camera(request):
    """
    Endpoint to initialize camera access for image recognition.
    Returns success/error status to the frontend.
    """
    try:
        logger.info("Camera access requested")
        return JsonResponse({"status": "success", "message": "Camera access granted"})
    except Exception as e:
        logger.error(f"Error in start_camera: {e}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@csrf_exempt
def video_feed(request, stream_id):
    """
    Process video frames and image uploads for object detection.
    Handles both camera stream and image file uploads.
    """
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "GET method not supported"}, status=405)

    # Check usage limits for authenticated users
    if request.user.is_authenticated:
        has_access, remaining, limit, message = check_feature_access(request.user, 'image_recognition')

        if not has_access:
            return JsonResponse({
                'status': 'error',
                'error': message,
                'code': 'LIMIT_REACHED',
                'limit': limit,
                'upgrade_url': '/app/pricing/'
            }, status=429)

    try:
        # Determine input type and get frame data
        if 'image' in request.FILES:
            # Handle image file upload
            image_file = request.FILES['image']

            # Validate image file
            is_valid, error_msg = ImageValidator.validate_image_file(image_file)
            if not is_valid:
                return JsonResponse({
                    "status": "error",
                    "message": error_msg,
                    "type": "validation_error"
                }, status=400)

            image_data = image_file.read()
            nparr = np.frombuffer(image_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            source_type = 'image'
        else:
            # Handle video frame data
            frame_data = request.body

            # Validate image data
            is_valid, error_msg = ImageValidator.validate_image_data(frame_data)
            if not is_valid:
                return JsonResponse({
                    "status": "error",
                    "message": error_msg,
                    "type": "validation_error"
                }, status=400)

            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            source_type = 'camera'

        if frame is None:
            raise ValueError("Invalid frame data")

        # Use image recognition service to detect currency
        detection_result = image_recognition_service.detect_currency(frame, confidence_threshold=0.4)

        if not detection_result:
            return JsonResponse({
                "status": "success",
                "predictions": [],
                "image": base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode('utf-8'),
                "source_type": source_type,
                "message": "No currency detected"
            })

        # Annotate the image with detection results
        annotated_frame = image_recognition_service.annotate_image(frame, detection_result)

        # Convert detection result to the expected format
        processed_predictions = [{
            "class": detection_result.currency_code or "unknown",
            "confidence": detection_result.confidence,
            "x": detection_result.bbox[0] if detection_result.bbox else 0,
            "y": detection_result.bbox[1] if detection_result.bbox else 0,
            "width": detection_result.bbox[2] if detection_result.bbox else 0,
            "height": detection_result.bbox[3] if detection_result.bbox else 0,
            "source": source_type,
            "denomination": detection_result.denomination,
            "method": detection_result.detection_method
        }]

        # Convert annotated frame to base64
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        image_base64 = base64.b64encode(buffer).decode('utf-8')

        # Increment usage counter and track learning progress for authenticated users
        if request.user.is_authenticated:
            increment_feature_usage(request.user, 'image_recognition')

            # Track learning progress
            LearningProgress.objects.create(
                user=request.user,
                activity_type='image_recognized',
                details={
                    'predictions': len(processed_predictions),
                    'currency': detection_result.currency_code,
                    'method': detection_result.detection_method
                },
                points_earned=3
            )

        response_data = {
            "status": "success",
            "predictions": processed_predictions,
            "image": image_base64,
            "source_type": source_type
        }

        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"Error processing {source_type if 'source_type' in locals() else 'frame'}: {e}", exc_info=True)
        return JsonResponse({
            "status": "error",
            "message": str(e),
            "type": "processing_error"
        }, status=500)

def exchange_rate(request):
    """
    View for the exchange rate calculator page.
    Now supports 15+ major currencies.
    """
    context = {
        'currencies': SUPPORTED_CURRENCIES,
        'currency_codes': CURRENCY_CODES,
    }
    return render(request, 'app/exchange_rate.html', context)

@require_http_methods(["POST"])
def convert_currency(request):
    """
    Currency conversion endpoint that handles POST requests
    Parameters:
        amount: float - Amount to convert
        from_currency: str - Source currency code
        to_currency: str - Target currency code
    Returns:
        JsonResponse with converted amount, exchange rate and formatted strings
    """
    try:
        # Extract parameters
        amount = request.POST.get('amount')
        from_currency = request.POST.get('from_currency')
        to_currency = request.POST.get('to_currency')

        # Validate conversion request
        is_valid, error_msg = CurrencyValidator.validate_conversion_request(
            amount, from_currency, to_currency
        )
        if not is_valid:
            return JsonResponse({'error': error_msg}, status=400)

        # Convert to proper types
        amount = float(amount)
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        logger.info(f"Converting {amount} {from_currency} to {to_currency}")

        # If converting same currency, return original amount with rate of 1
        if from_currency == to_currency:
            current_time = datetime.now(pytz.timezone('Asia/Taipei')).strftime("%Y-%m-%d %H:%M:%S")
            return JsonResponse({
                'result': amount,
                'rate': 1.0,
                'formatted_result': f"{amount:,.2f} {to_currency}",
                'formatted_rate': f"1 {from_currency} = 1.0000 {to_currency}",
                'conversion_time': current_time
            })

        # Use exchange rate service to perform conversion
        conversion_result = ExchangeRateService.convert_currency(
            amount, from_currency, to_currency
        )

        if not conversion_result:
            return JsonResponse({
                'error': 'Failed to fetch exchange rate. Please try again.'
            }, status=400)

        # Get current time in Taipei timezone
        current_time = datetime.now(pytz.timezone('Asia/Taipei')).strftime("%Y-%m-%d %H:%M:%S")

        return JsonResponse({
            'result': conversion_result['result'],
            'rate': conversion_result['rate'],
            'formatted_result': f"{amount:,.2f} {from_currency} = {conversion_result['result']:,.2f} {to_currency}",
            'formatted_rate': f"1 {from_currency} = {conversion_result['rate']:.4f} {to_currency}",
            'conversion_time': current_time
        })

    except Exception as e:
        logger.error(f"Conversion error: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': 'An unexpected error occurred'
        }, status=500)

def money(request):
    """
    View for displaying currency information page.
    Shows comprehensive information for all supported currencies.
    """
    # Get selected currency from query params, default to JPY
    selected_currency = request.GET.get('currency', 'JPY').upper()

    # Validate currency code using validator
    is_valid, error_msg = CurrencyValidator.validate_currency_code(selected_currency)
    if not is_valid:
        logger.warning(f"Invalid currency code requested: {selected_currency}, defaulting to JPY")
        selected_currency = 'JPY'

    context = {
        'currencies': SUPPORTED_CURRENCIES,
        'currency_codes': CURRENCY_CODES,
        'selected_currency': selected_currency,
        'selected_info': get_currency_info(selected_currency),
    }

    return render(request, 'app/money.html', context)

def financing_ai_chat(request):
    """
    View for AI chat interface focused on financial topics.
    Provides initial welcome message and example questions.
    """
    context = {
        'initial_message': (
            "Hello! I'm Financing AI Chat 💬✨!\n"
            "Feel free to enter your concerns or matters you wish to investigate.\n\n"
            "What I can do:\n"
            "- Analyze specific stocks (U.S. listed stocks)\n"
            "- Provide financial knowledge and literacy\n"
            "- Diagnosis of investment style\n"
            "- Chatting with you\n\n"
            "Sample Questions:\n"
            "- I would like to know if TSMC's share price was undervalued in 2020.\n"
            "- I want to know which investment method is right for me.\n"
            "- What is the difference between assets and liabilities?"
        )
    }
    return render(request, 'app/financing_ai_chat.html', context)

@require_http_methods(["POST"])
def ask(request):
    """
    AI Chat endpoint that handles POST requests for message processing.
    Takes user message and returns AI response as a stream.
    """
    try:
        # Check usage limits for authenticated users
        if request.user.is_authenticated:
            has_access, remaining, limit, message = check_feature_access(request.user, 'ai_chat')

            if not has_access:
                return JsonResponse({
                    'error': message,
                    'code': 'LIMIT_REACHED',
                    'limit': limit,
                    'upgrade_url': '/app/pricing/'
                }, status=429)

        # Parse JSON request body
        data = json.loads(request.body)
        user_message = data.get('message')
        conversation_id = data.get('conversation_id')
        user_id = data.get('user', 'default_user')

        # Validate message exists
        if not user_message:
            logger.error("No message provided in request")
            return JsonResponse({'error': 'No message provided'}, status=400)

        logger.info(f"Processing message from user {user_id}: {user_message[:50]}...")

        try:
            # Send message to Dify API and get streaming response
            response = dify_api.send_message(
                query=user_message,
                conversation_id=conversation_id,
                user=user_id,
                stream=True
            )

            # Increment usage counter for authenticated users
            if request.user.is_authenticated:
                increment_feature_usage(request.user, 'ai_chat')

                # Track learning progress
                LearningProgress.objects.create(
                    user=request.user,
                    activity_type='ai_chat_completed',
                    details={'message': user_message[:100]},
                    points_earned=5
                )

            def generate():
                """Generator function to stream API response"""
                try:
                    for line in response.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8')
                            logger.debug(f"Streaming response line: {decoded_line[:50]}...")
                            yield f"data: {decoded_line}\n\n"
                except Exception as e:
                    logger.error(f"Error in stream generation: {e}")
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"

            return StreamingHttpResponse(
                generate(),
                content_type='text/event-stream'
            )

        except Exception as e:
            logger.error(f"Error in Dify API communication: {e}")
            return JsonResponse({
                'error': 'Failed to communicate with AI service',
                'details': str(e)
            }, status=503)

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request: {e}")
        return JsonResponse({
            'error': 'Invalid JSON format',
            'details': str(e)
        }, status=400)

    except Exception as e:
        logger.error(f"Unexpected error in ask endpoint: {e}")
        return JsonResponse({
            'error': 'An unexpected error occurred',
            'details': str(e)
        }, status=500)

def reference(request):
    return render(request, 'app/reference.html')

def get_exchange_rates(request):
    """
    Get current exchange rates for multiple currency pairs
    Returns:
        JsonResponse with current rates and timestamp
    """
    try:
        # Download rates for multiple currency pairs
        currency_pairs = ['TWDJPY=X', 'JPYTWD=X', 'USDJPY=X', 'USDTWD=X']
        rates = {}
        
        for pair in currency_pairs:
            data = yf.download(pair, period='1d')
            if not data.empty:
                rates[pair.replace('=X', '')] = float(data['Close'].iloc[-1])

        if not rates:
            return JsonResponse({'error': 'Failed to fetch exchange rates'}, status=400)

        # Get current time in Taiwan timezone
        tst = pytz.timezone('Asia/Taipei')
        current_time = datetime.now(tst).strftime("%Y-%m-%d %H:%M:%S")

        response_data = {
            'rates': {
                'JPY_TWD': rates.get('JPYTWD', 0),
                'TWD_JPY': rates.get('TWDJPY', 0),
                'USD_JPY': rates.get('USDJPY', 0),
                'USD_TWD': rates.get('USDTWD', 0)
            },
            'last_updated': current_time
        }

        logger.info(f"Exchange rates fetched successfully: {response_data}")
        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"Error fetching exchange rates: {str(e)}")
        return JsonResponse({
            'error': 'Failed to fetch exchange rates',
            'details': str(e)
        }, status=500)