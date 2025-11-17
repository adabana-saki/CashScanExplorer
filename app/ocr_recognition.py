"""
OCR-based currency recognition fallback
For currencies without image recognition datasets
"""
import re
import logging
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)

# Try to import pytesseract (optional dependency)
try:
    import pytesseract
    from PIL import Image
    import cv2
    import numpy as np
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("Tesseract OCR not available. Install with: pip install pytesseract pillow")


class CurrencyOCR:
    """
    OCR-based currency recognition for currencies without image recognition
    Uses Tesseract OCR to detect text and numbers on banknotes
    """

    # Currency detection keywords (multi-language support)
    CURRENCY_KEYWORDS = {
        'CNY': {
            'keywords': ['人民币', 'YUAN', 'RMB', 'CHINA', '中国人民银行', 'RENMINBI'],
            'symbols': ['¥', '￥'],
            'name': 'Chinese Yuan'
        },
        'KRW': {
            'keywords': ['원', 'WON', 'KOREA', 'BANK OF KOREA', '한국은행', '대한민국'],
            'symbols': ['₩'],
            'name': 'Korean Won'
        },
        'THB': {
            'keywords': ['บาท', 'BAHT', 'THAILAND', 'ไทย'],
            'symbols': ['฿'],
            'name': 'Thai Baht'
        },
        'CHF': {
            'keywords': ['FRANKEN', 'FRANCS', 'SWISS', 'SCHWEIZ', 'SUISSE', 'SVIZZERA'],
            'symbols': ['CHF', 'Fr'],
            'name': 'Swiss Franc'
        },
        'TWD': {
            'keywords': ['台幣', 'NT$', 'TAIWAN', 'DOLLAR', '臺灣銀行', '新台幣'],
            'symbols': ['NT$', 'TWD'],
            'name': 'Taiwan Dollar'
        },
        'JPY': {
            'keywords': ['円', 'YEN', 'JAPAN', '日本銀行', 'NIPPON'],
            'symbols': ['¥', '￥'],
            'name': 'Japanese Yen'
        },
        'USD': {
            'keywords': ['DOLLAR', 'USA', 'UNITED STATES', 'AMERICA', 'FEDERAL RESERVE'],
            'symbols': ['$', 'USD'],
            'name': 'US Dollar'
        },
        'EUR': {
            'keywords': ['EURO', 'EUROPEAN', 'BCE', 'ECB', 'EZB'],
            'symbols': ['€', 'EUR'],
            'name': 'Euro'
        },
        'GBP': {
            'keywords': ['POUND', 'STERLING', 'ENGLAND', 'BANK OF ENGLAND', 'BRITAIN'],
            'symbols': ['£', 'GBP'],
            'name': 'British Pound'
        },
    }

    # Common denomination patterns
    DENOMINATION_PATTERNS = [
        r'\b(1|2|5|10|20|50|100|200|500|1000|2000|5000|10000|50000)\b',
    ]

    def __init__(self):
        """Initialize OCR service"""
        if not TESSERACT_AVAILABLE:
            raise ImportError(
                "Tesseract OCR dependencies not installed. "
                "Install with: pip install pytesseract pillow"
            )

    def preprocess_image(self, image_array: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy
        """
        # Convert to grayscale
        if len(image_array.shape) == 3:
            gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_array

        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Noise removal
        denoised = cv2.fastNlMeansDenoising(thresh)

        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        return enhanced

    def extract_text(self, image_array: np.ndarray, lang: str = 'eng+jpn+chi_sim+chi_tra+kor+tha') -> str:
        """
        Extract text from image using Tesseract OCR
        Supports multiple languages
        """
        try:
            # Preprocess image
            preprocessed = self.preprocess_image(image_array)

            # Convert to PIL Image
            pil_image = Image.fromarray(preprocessed)

            # Perform OCR
            text = pytesseract.image_to_string(
                pil_image,
                lang=lang,
                config='--psm 6'  # Assume uniform block of text
            )

            logger.debug(f"OCR extracted text: {text[:200]}")
            return text

        except Exception as e:
            logger.error(f"Error in OCR text extraction: {e}")
            return ""

    def detect_denomination(self, text: str) -> Optional[int]:
        """
        Detect currency denomination from text
        Returns the detected number
        """
        for pattern in self.DENOMINATION_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Get all matching numbers
                numbers = [int(m) for m in matches]

                # Return most common or largest (likely the denomination)
                # Filter out very small numbers (likely not denominations)
                valid_numbers = [n for n in numbers if n >= 1]

                if valid_numbers:
                    # Return the most frequent number, or largest if tie
                    from collections import Counter
                    counter = Counter(valid_numbers)
                    most_common = counter.most_common(1)[0][0]
                    return most_common

        return None

    def detect_currency(self, text: str) -> Optional[Tuple[str, float]]:
        """
        Detect currency type from text
        Returns (currency_code, confidence_score)
        """
        text_upper = text.upper()

        # Score each currency
        scores = {}

        for currency_code, data in self.CURRENCY_KEYWORDS.items():
            score = 0

            # Check keywords
            for keyword in data['keywords']:
                if keyword.upper() in text_upper or keyword in text:
                    score += 2  # Keywords worth 2 points

            # Check symbols
            for symbol in data['symbols']:
                if symbol in text:
                    score += 3  # Symbols worth 3 points

            if score > 0:
                scores[currency_code] = score

        if not scores:
            return None

        # Get currency with highest score
        best_currency = max(scores, key=scores.get)
        max_score = scores[best_currency]

        # Calculate confidence (normalize to 0-1)
        confidence = min(max_score / 5.0, 1.0)  # 5 points = 100% confidence

        return (best_currency, confidence)

    def recognize_currency(self, image_array: np.ndarray) -> Optional[Dict]:
        """
        Main method to recognize currency from image
        Returns dictionary with currency code, denomination, and confidence
        """
        try:
            # Extract text
            text = self.extract_text(image_array)

            if not text or len(text.strip()) < 3:
                logger.warning("Insufficient text extracted from image")
                return None

            # Detect currency
            currency_result = self.detect_currency(text)
            if not currency_result:
                logger.warning("Could not detect currency from text")
                return None

            currency_code, currency_confidence = currency_result

            # Detect denomination
            denomination = self.detect_denomination(text)

            # Overall confidence
            overall_confidence = currency_confidence

            if denomination:
                overall_confidence *= 1.2  # Boost confidence if denomination found
                overall_confidence = min(overall_confidence, 1.0)

            result = {
                'currency_code': currency_code,
                'currency_name': self.CURRENCY_KEYWORDS[currency_code]['name'],
                'denomination': denomination,
                'confidence': overall_confidence,
                'method': 'ocr',
                'extracted_text': text[:200]  # First 200 chars for debugging
            }

            logger.info(f"OCR recognition result: {result}")
            return result

        except Exception as e:
            logger.error(f"Error in currency recognition: {e}", exc_info=True)
            return None


# Convenience function
def recognize_currency_ocr(image_array: np.ndarray) -> Optional[Dict]:
    """
    Convenience function to recognize currency using OCR
    """
    if not TESSERACT_AVAILABLE:
        logger.error("Tesseract OCR not available")
        return None

    try:
        ocr = CurrencyOCR()
        return ocr.recognize_currency(image_array)
    except Exception as e:
        logger.error(f"OCR recognition failed: {e}")
        return None


# Check if Tesseract is properly installed
def check_tesseract_installation() -> bool:
    """
    Check if Tesseract OCR is properly installed and accessible
    """
    if not TESSERACT_AVAILABLE:
        return False

    try:
        version = pytesseract.get_tesseract_version()
        logger.info(f"Tesseract version: {version}")
        return True
    except Exception as e:
        logger.error(f"Tesseract not properly installed: {e}")
        return False
