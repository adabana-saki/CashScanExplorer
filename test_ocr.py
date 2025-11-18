#!/usr/bin/env python
"""
OCR Currency Recognition Test Script

Tests the OCR-based currency recognition system.
Checks Tesseract installation and demonstrates usage.

Usage:
    python test_ocr.py
    python test_ocr.py --image path/to/banknote.jpg
"""

import sys
import os
import argparse

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CSE_Project.settings')
import django
django.setup()

from app.ocr_recognition import check_tesseract_installation, TESSERACT_AVAILABLE

def test_installation():
    """Test if Tesseract OCR is properly installed"""
    print("=" * 60)
    print("OCR Currency Recognition - Installation Test")
    print("=" * 60)
    print()

    if not TESSERACT_AVAILABLE:
        print("❌ ERROR: Tesseract OCR dependencies not installed")
        print()
        print("To install:")
        print("  pip install pytesseract pillow")
        print()
        print("Then install Tesseract OCR:")
        print("  Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        print("  macOS: brew install tesseract")
        print("  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        print()
        return False

    print("✓ Tesseract dependencies are installed")
    print()

    if check_tesseract_installation():
        print("✓ Tesseract OCR is properly installed and working")
        print()
        return True
    else:
        print("❌ ERROR: Tesseract OCR is not properly configured")
        print()
        print("Please install Tesseract OCR system package:")
        print("  Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        print("  macOS: brew install tesseract")
        print("  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        print()
        return False


def test_with_sample_text():
    """Test OCR with sample text (without real image)"""
    print("=" * 60)
    print("OCR Text Recognition - Sample Test")
    print("=" * 60)
    print()

    from app.ocr_recognition import CurrencyOCR

    try:
        ocr = CurrencyOCR()

        # Test currency detection from sample texts
        test_cases = [
            ("人民币 100 CHINA", "CNY"),
            ("BANK OF KOREA 1000 원", "KRW"),
            ("THAILAND BAHT 500", "THB"),
            ("SWISS FRANCS 50", "CHF"),
            ("100 台幣 TAIWAN NT$", "TWD"),
            ("日本銀行 1000 円", "JPY"),
        ]

        print("Testing currency detection from text samples...")
        print()

        passed = 0
        for text, expected_currency in test_cases:
            result = ocr.detect_currency(text)
            if result:
                detected_currency, confidence = result
                status = "✓" if detected_currency == expected_currency else "✗"
                print(f"{status} Text: '{text[:30]}...'")
                print(f"   Expected: {expected_currency}, Detected: {detected_currency} (confidence: {confidence:.2%})")
                if detected_currency == expected_currency:
                    passed += 1
            else:
                print(f"✗ Text: '{text[:30]}...'")
                print(f"   Expected: {expected_currency}, Detected: None")
            print()

        print(f"Results: {passed}/{len(test_cases)} tests passed")
        print()
        return passed == len(test_cases)

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_image(image_path):
    """Test OCR with actual banknote image"""
    print("=" * 60)
    print("OCR Currency Recognition - Image Test")
    print("=" * 60)
    print()

    if not os.path.exists(image_path):
        print(f"❌ ERROR: Image file not found: {image_path}")
        return False

    from app.ocr_recognition import recognize_currency_ocr
    import cv2

    try:
        print(f"Loading image: {image_path}")
        image = cv2.imread(image_path)

        if image is None:
            print("❌ ERROR: Could not load image")
            return False

        print(f"Image size: {image.shape[1]}x{image.shape[0]}")
        print()
        print("Running OCR recognition...")
        print()

        result = recognize_currency_ocr(image)

        if result:
            print("✓ Currency recognized successfully!")
            print()
            print(f"Currency: {result['currency_name']} ({result['currency_code']})")
            if result['denomination']:
                print(f"Denomination: {result['denomination']}")
            print(f"Confidence: {result['confidence']:.2%}")
            print(f"Method: {result['method']}")
            print()
            print("Extracted text sample:")
            print(f"  {result['extracted_text'][:150]}...")
            print()
            return True
        else:
            print("❌ Could not recognize currency from image")
            print()
            print("Tips:")
            print("  - Ensure the image is clear and well-lit")
            print("  - Make sure the banknote text is visible")
            print("  - Try with different banknote images")
            print()
            return False

    except Exception as e:
        print(f"❌ Error during image recognition: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_supported_currencies():
    """Print list of supported currencies for OCR"""
    from app.ocr_recognition import CurrencyOCR

    print("=" * 60)
    print("Supported Currencies for OCR Recognition")
    print("=" * 60)
    print()

    ocr = CurrencyOCR()
    currencies = ocr.CURRENCY_KEYWORDS

    for code, data in currencies.items():
        print(f"{code} - {data['name']}")
        print(f"  Keywords: {', '.join(data['keywords'][:3])}")
        print(f"  Symbols: {', '.join(data['symbols'])}")
        print()


def main():
    """Main test function"""
    parser = argparse.ArgumentParser(description='Test OCR currency recognition')
    parser.add_argument('--image', type=str, help='Path to banknote image to test')
    parser.add_argument('--list', action='store_true', help='List supported currencies')
    args = parser.parse_args()

    if args.list:
        print_supported_currencies()
        return

    # Test installation
    if not test_installation():
        sys.exit(1)

    # Test with sample text
    print()
    if not test_with_sample_text():
        print("⚠ Warning: Some text detection tests failed")
        print()

    # Test with image if provided
    if args.image:
        print()
        if test_with_image(args.image):
            print("✓ All tests passed!")
        else:
            print("✗ Image test failed")
            sys.exit(1)
    else:
        print()
        print("=" * 60)
        print("To test with an actual banknote image:")
        print("  python test_ocr.py --image path/to/banknote.jpg")
        print()
        print("To see supported currencies:")
        print("  python test_ocr.py --list")
        print("=" * 60)


if __name__ == '__main__':
    main()
