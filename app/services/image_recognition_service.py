"""
Image Recognition Service
Handles currency detection via computer vision and OCR
"""
import base64
import logging
from typing import Optional, Dict, List
from dataclasses import dataclass

import cv2
import numpy as np

from ..ocr_recognition import recognize_currency_ocr, TESSERACT_AVAILABLE

logger = logging.getLogger(__name__)


@dataclass
class DetectionResult:
    """Result of currency detection"""
    currency_code: str
    currency_name: str
    denomination: Optional[int]
    confidence: float
    method: str  # 'roboflow', 'ocr', or 'manual'
    bounding_box: Optional[Dict] = None


class ImageRecognitionService:
    """Service for currency image recognition"""

    # Recognition methods priority
    METHODS = ['roboflow', 'ocr', 'manual']

    def __init__(self, roboflow_model=None):
        """
        Initialize recognition service

        Args:
            roboflow_model: Roboflow model instance (optional)
        """
        self.roboflow_model = roboflow_model
        self.ocr_available = TESSERACT_AVAILABLE

    def detect_currency(
        self,
        image: np.ndarray,
        confidence_threshold: float = 0.4
    ) -> Optional[DetectionResult]:
        """
        Detect currency in image using available methods

        Args:
            image: Image as numpy array
            confidence_threshold: Minimum confidence for Roboflow detection

        Returns:
            DetectionResult or None if no detection
        """
        # Try Roboflow first (highest accuracy)
        if self.roboflow_model:
            result = self._detect_with_roboflow(image, confidence_threshold)
            if result:
                return result

        # Fallback to OCR
        if self.ocr_available:
            result = self._detect_with_ocr(image)
            if result:
                return result

        logger.warning("No detection method succeeded")
        return None

    def _detect_with_roboflow(
        self,
        image: np.ndarray,
        confidence_threshold: float
    ) -> Optional[DetectionResult]:
        """
        Detect currency using Roboflow model

        Args:
            image: Image as numpy array
            confidence_threshold: Minimum confidence threshold

        Returns:
            DetectionResult or None
        """
        try:
            prediction = self.roboflow_model.predict(
                image,
                confidence=int(confidence_threshold * 100),
                overlap=30
            ).json()

            predictions = prediction.get('predictions', [])

            if not predictions:
                logger.debug("No Roboflow predictions found")
                return None

            # Get highest confidence prediction
            best_prediction = max(predictions, key=lambda x: x['confidence'])

            # Parse class name (e.g., "twd_100" -> TWD, 100)
            class_name = best_prediction['class']
            currency_code, denomination = self._parse_class_name(class_name)

            if not currency_code:
                logger.warning(f"Could not parse class name: {class_name}")
                return None

            # Get bounding box
            bbox = {
                'x': int(best_prediction['x'] - best_prediction['width'] / 2),
                'y': int(best_prediction['y'] - best_prediction['height'] / 2),
                'width': int(best_prediction['width']),
                'height': int(best_prediction['height'])
            }

            return DetectionResult(
                currency_code=currency_code,
                currency_name=self._get_currency_name(currency_code),
                denomination=denomination,
                confidence=best_prediction['confidence'],
                method='roboflow',
                bounding_box=bbox
            )

        except Exception as e:
            logger.error(f"Roboflow detection error: {e}", exc_info=True)
            return None

    def _detect_with_ocr(self, image: np.ndarray) -> Optional[DetectionResult]:
        """
        Detect currency using OCR

        Args:
            image: Image as numpy array

        Returns:
            DetectionResult or None
        """
        try:
            result = recognize_currency_ocr(image)

            if not result:
                logger.debug("OCR detection failed")
                return None

            return DetectionResult(
                currency_code=result['currency_code'],
                currency_name=result['currency_name'],
                denomination=result.get('denomination'),
                confidence=result['confidence'],
                method='ocr'
            )

        except Exception as e:
            logger.error(f"OCR detection error: {e}", exc_info=True)
            return None

    def annotate_image(
        self,
        image: np.ndarray,
        detection: DetectionResult
    ) -> np.ndarray:
        """
        Draw detection annotations on image

        Args:
            image: Original image
            detection: Detection result

        Returns:
            Annotated image
        """
        annotated = image.copy()

        try:
            # Draw bounding box if available
            if detection.bounding_box:
                bbox = detection.bounding_box
                cv2.rectangle(
                    annotated,
                    (bbox['x'], bbox['y']),
                    (bbox['x'] + bbox['width'], bbox['y'] + bbox['height']),
                    (0, 255, 0),
                    2
                )

            # Add label
            label_parts = [detection.currency_code]
            if detection.denomination:
                label_parts.append(str(detection.denomination))
            label_parts.append(f"({detection.confidence:.2%})")

            label = " ".join(label_parts)

            # Position label
            if detection.bounding_box:
                x = detection.bounding_box['x']
                y = max(detection.bounding_box['y'] - 10, 20)
            else:
                x, y = 10, 30

            # Draw label background
            (text_width, text_height), _ = cv2.getTextSize(
                label,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                2
            )
            cv2.rectangle(
                annotated,
                (x, y - text_height - 5),
                (x + text_width + 10, y + 5),
                (0, 255, 0),
                -1
            )

            # Draw label text
            cv2.putText(
                annotated,
                label,
                (x + 5, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 0),
                2
            )

            return annotated

        except Exception as e:
            logger.error(f"Error annotating image: {e}")
            return image

    def image_to_base64(self, image: np.ndarray) -> str:
        """
        Convert image to base64 string

        Args:
            image: Image as numpy array

        Returns:
            Base64 encoded string
        """
        _, buffer = cv2.imencode('.jpg', image)
        return base64.b64encode(buffer).decode('utf-8')

    @staticmethod
    def _parse_class_name(class_name: str) -> tuple:
        """
        Parse Roboflow class name to extract currency and denomination

        Args:
            class_name: Class name like "twd_100" or "jpy-1000"

        Returns:
            Tuple of (currency_code, denomination)
        """
        try:
            # Normalize separators
            class_name = class_name.replace('-', '_').upper()

            # Split by underscore
            parts = class_name.split('_')

            if len(parts) >= 2:
                currency = parts[0]
                denomination = int(''.join(filter(str.isdigit, parts[1])))
                return currency, denomination
            elif len(parts) == 1:
                # Try to extract numbers
                currency = ''.join(filter(str.isalpha, parts[0]))
                numbers = ''.join(filter(str.isdigit, parts[0]))
                denomination = int(numbers) if numbers else None
                return currency, denomination

        except Exception as e:
            logger.warning(f"Error parsing class name '{class_name}': {e}")

        return None, None

    @staticmethod
    def _get_currency_name(currency_code: str) -> str:
        """
        Get full currency name from code

        Args:
            currency_code: Currency code like "TWD"

        Returns:
            Full currency name
        """
        from ..currencies import get_currency_info

        info = get_currency_info(currency_code)
        return info['name'] if info else currency_code


class BatchImageProcessor:
    """Process multiple images in batch"""

    def __init__(self, recognition_service: ImageRecognitionService):
        """
        Initialize batch processor

        Args:
            recognition_service: ImageRecognitionService instance
        """
        self.service = recognition_service

    def process_batch(
        self,
        images: List[np.ndarray],
        annotate: bool = False
    ) -> List[Optional[Dict]]:
        """
        Process multiple images

        Args:
            images: List of images as numpy arrays
            annotate: Whether to annotate images

        Returns:
            List of detection results
        """
        results = []

        for i, image in enumerate(images):
            try:
                detection = self.service.detect_currency(image)

                if detection:
                    result = {
                        'index': i,
                        'currency_code': detection.currency_code,
                        'currency_name': detection.currency_name,
                        'denomination': detection.denomination,
                        'confidence': detection.confidence,
                        'method': detection.method
                    }

                    if annotate:
                        annotated = self.service.annotate_image(image, detection)
                        result['image_base64'] = self.service.image_to_base64(annotated)

                    results.append(result)
                else:
                    results.append(None)

            except Exception as e:
                logger.error(f"Error processing image {i}: {e}")
                results.append(None)

        return results
