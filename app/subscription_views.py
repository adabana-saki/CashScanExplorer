"""
Subscription management and payment processing views
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import stripe
import logging
import json

from .models import Subscription, SubscriptionPlan, UserProfile

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY if hasattr(settings, 'STRIPE_SECRET_KEY') else None


def pricing_view(request):
    """Display pricing plans"""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')

    # Get current user's subscription if logged in
    current_plan = None
    if request.user.is_authenticated:
        try:
            subscription = request.user.subscription
            current_plan = subscription.plan.plan_type
        except Subscription.DoesNotExist:
            pass

    context = {
        'plans': plans,
        'current_plan': current_plan,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY if hasattr(settings, 'STRIPE_PUBLIC_KEY') else '',
    }

    return render(request, 'app/subscription/pricing.html', context)


@login_required
@require_http_methods(["POST"])
def create_checkout_session(request):
    """Create Stripe checkout session for subscription"""

    if not stripe.api_key:
        return JsonResponse({
            'error': 'Payment system not configured'
        }, status=500)

    try:
        data = json.loads(request.body)
        plan_type = data.get('plan_type')

        # Get the plan
        plan = SubscriptionPlan.objects.get(plan_type=plan_type, is_active=True)

        # Create or get Stripe customer
        user = request.user
        try:
            subscription = user.subscription
            stripe_customer_id = subscription.stripe_customer_id
        except Subscription.DoesNotExist:
            stripe_customer_id = None

        if not stripe_customer_id:
            # Create new Stripe customer
            customer = stripe.Customer.create(
                email=user.email,
                metadata={
                    'user_id': user.id,
                    'username': user.username
                }
            )
            stripe_customer_id = customer.id

        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': plan.name,
                        'description': f'Monthly subscription to {plan.name}',
                    },
                    'unit_amount': int(plan.price * 100),  # Convert to cents
                    'recurring': {
                        'interval': 'month',
                    },
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.build_absolute_uri(reverse('app:payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('app:payment_cancel')),
            metadata={
                'user_id': user.id,
                'plan_type': plan_type,
            }
        )

        return JsonResponse({
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        })

    except SubscriptionPlan.DoesNotExist:
        return JsonResponse({'error': 'Invalid plan'}, status=400)
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        return JsonResponse({'error': 'An error occurred'}, status=500)


@login_required
def payment_success(request):
    """Handle successful payment"""
    session_id = request.GET.get('session_id')

    if not session_id:
        return render(request, 'app/subscription/payment_result.html', {
            'success': False,
            'message': 'Invalid session'
        })

    try:
        # Retrieve the session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)

        # Update user subscription
        user = request.user
        plan_type = session.metadata.get('plan_type')
        plan = SubscriptionPlan.objects.get(plan_type=plan_type)

        # Update or create subscription
        subscription, created = Subscription.objects.update_or_create(
            user=user,
            defaults={
                'plan': plan,
                'status': 'active',
                'stripe_customer_id': session.customer,
                'stripe_subscription_id': session.subscription,
                'current_period_start': timezone.now(),
                'current_period_end': timezone.now() + timedelta(days=30),
            }
        )

        return render(request, 'app/subscription/payment_result.html', {
            'success': True,
            'message': f'Successfully subscribed to {plan.name}!',
            'plan': plan
        })

    except Exception as e:
        logger.error(f"Error processing payment success: {e}")
        return render(request, 'app/subscription/payment_result.html', {
            'success': False,
            'message': 'An error occurred processing your payment'
        })


@login_required
def payment_cancel(request):
    """Handle cancelled payment"""
    return render(request, 'app/subscription/payment_result.html', {
        'success': False,
        'message': 'Payment was cancelled. You can try again anytime.',
        'cancelled': True
    })


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """Handle Stripe webhook events"""

    if not stripe.api_key:
        return HttpResponse(status=400)

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET if hasattr(settings, 'STRIPE_WEBHOOK_SECRET') else None

    if not webhook_secret:
        logger.warning("Stripe webhook secret not configured")
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        logger.info(f"Checkout session completed: {session['id']}")

    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        logger.info(f"Subscription updated: {subscription['id']}")
        _handle_subscription_update(subscription)

    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        logger.info(f"Subscription deleted: {subscription['id']}")
        _handle_subscription_cancelled(subscription)

    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        logger.info(f"Invoice payment succeeded: {invoice['id']}")
        _handle_invoice_paid(invoice)

    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        logger.info(f"Invoice payment failed: {invoice['id']}")
        _handle_invoice_failed(invoice)

    return HttpResponse(status=200)


def _handle_subscription_update(stripe_subscription):
    """Handle subscription update from Stripe"""
    try:
        subscription = Subscription.objects.get(
            stripe_subscription_id=stripe_subscription['id']
        )
        subscription.status = stripe_subscription['status']
        subscription.current_period_end = timezone.datetime.fromtimestamp(
            stripe_subscription['current_period_end'],
            tz=timezone.utc
        )
        subscription.save()
    except Subscription.DoesNotExist:
        logger.error(f"Subscription not found: {stripe_subscription['id']}")


def _handle_subscription_cancelled(stripe_subscription):
    """Handle subscription cancellation from Stripe"""
    try:
        subscription = Subscription.objects.get(
            stripe_subscription_id=stripe_subscription['id']
        )
        subscription.status = 'cancelled'
        subscription.save()
    except Subscription.DoesNotExist:
        logger.error(f"Subscription not found: {stripe_subscription['id']}")


def _handle_invoice_paid(stripe_invoice):
    """Handle successful invoice payment from Stripe"""
    try:
        subscription = Subscription.objects.get(
            stripe_subscription_id=stripe_invoice['subscription']
        )
        subscription.status = 'active'
        subscription.save()
    except Subscription.DoesNotExist:
        logger.error(f"Subscription not found for invoice: {stripe_invoice['id']}")


def _handle_invoice_failed(stripe_invoice):
    """Handle failed invoice payment from Stripe"""
    try:
        subscription = Subscription.objects.get(
            stripe_subscription_id=stripe_invoice['subscription']
        )
        # Mark subscription as having payment issues
        # You might want to send an email notification here
        logger.warning(f"Payment failed for subscription: {subscription.id}")
    except Subscription.DoesNotExist:
        logger.error(f"Subscription not found for invoice: {stripe_invoice['id']}")


@login_required
@require_http_methods(["POST"])
def cancel_subscription(request):
    """Cancel user subscription"""
    try:
        subscription = request.user.subscription

        if subscription.stripe_subscription_id and stripe.api_key:
            # Cancel in Stripe
            stripe.Subscription.delete(subscription.stripe_subscription_id)

        # Downgrade to free plan
        free_plan = SubscriptionPlan.objects.get(plan_type='free')
        subscription.plan = free_plan
        subscription.status = 'cancelled'
        subscription.stripe_subscription_id = None
        subscription.save()

        return JsonResponse({
            'success': True,
            'message': 'Subscription cancelled successfully'
        })

    except Subscription.DoesNotExist:
        return JsonResponse({
            'error': 'No active subscription found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error cancelling subscription: {e}")
        return JsonResponse({
            'error': 'An error occurred'
        }, status=500)
