"""
Validation utilities for CashScanExplorer
"""
from typing import Optional, Tuple
from .currencies import CURRENCY_CODES


class ValidationError(Exception):
    """Custom validation error"""
    pass


class CurrencyValidator:
    """Validate currency-related inputs"""

    @staticmethod
    def validate_currency_code(code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate currency code

        Args:
            code: Currency code to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not code:
            return False, "Currency code is required"

        code_upper = code.upper()

        if code_upper not in CURRENCY_CODES:
            return False, f"Invalid currency code: {code}. Supported currencies: {', '.join(CURRENCY_CODES)}"

        return True, None

    @staticmethod
    def validate_amount(amount: any) -> Tuple[bool, Optional[str]]:
        """
        Validate currency amount

        Args:
            amount: Amount to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            amount_float = float(amount)

            if amount_float <= 0:
                return False, "Amount must be greater than 0"

            if amount_float > 1e15:  # Reasonable upper limit
                return False, "Amount is too large"

            return True, None

        except (ValueError, TypeError):
            return False, "Invalid amount format. Must be a number"

    @staticmethod
    def validate_conversion_request(
        amount: any,
        from_currency: str,
        to_currency: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate complete currency conversion request

        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate amount
        is_valid, error = CurrencyValidator.validate_amount(amount)
        if not is_valid:
            return False, error

        # Validate from_currency
        is_valid, error = CurrencyValidator.validate_currency_code(from_currency)
        if not is_valid:
            return False, f"Source currency error: {error}"

        # Validate to_currency
        is_valid, error = CurrencyValidator.validate_currency_code(to_currency)
        if not is_valid:
            return False, f"Target currency error: {error}"

        return True, None


class ImageValidator:
    """Validate image-related inputs"""

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_FORMATS = ['jpg', 'jpeg', 'png']

    @staticmethod
    def validate_image_file(file) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded image file

        Args:
            file: Uploaded file object

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file:
            return False, "No image file provided"

        # Check file size
        if hasattr(file, 'size'):
            if file.size > ImageValidator.MAX_FILE_SIZE:
                return False, f"File size exceeds maximum ({ImageValidator.MAX_FILE_SIZE / 1024 / 1024}MB)"

        # Check file extension
        if hasattr(file, 'name'):
            ext = file.name.split('.')[-1].lower()
            if ext not in ImageValidator.ALLOWED_FORMATS:
                return False, f"Invalid file format. Allowed: {', '.join(ImageValidator.ALLOWED_FORMATS)}"

        return True, None

    @staticmethod
    def validate_image_data(data: bytes) -> Tuple[bool, Optional[str]]:
        """
        Validate raw image data

        Args:
            data: Image data as bytes

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not data:
            return False, "Empty image data"

        if len(data) > ImageValidator.MAX_FILE_SIZE:
            return False, "Image data too large"

        return True, None


class QuizValidator:
    """Validate quiz-related inputs"""

    VALID_QUESTION_TYPES = [
        'symbol_to_name',
        'name_to_symbol',
        'country_to_currency',
        'currency_to_country',
        'denomination',
        'fun_fact',
        'random'
    ]

    @staticmethod
    def validate_question_type(question_type: str) -> Tuple[bool, Optional[str]]:
        """
        Validate quiz question type

        Args:
            question_type: Question type to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not question_type:
            return False, "Question type is required"

        if question_type not in QuizValidator.VALID_QUESTION_TYPES:
            return False, f"Invalid question type. Valid types: {', '.join(QuizValidator.VALID_QUESTION_TYPES)}"

        return True, None

    @staticmethod
    def validate_answer(answer: str) -> Tuple[bool, Optional[str]]:
        """
        Validate quiz answer

        Args:
            answer: Answer to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not answer or not answer.strip():
            return False, "Answer cannot be empty"

        if len(answer) > 500:
            return False, "Answer is too long"

        return True, None


def validate_required_fields(data: dict, required_fields: list) -> Tuple[bool, Optional[str]]:
    """
    Validate that all required fields are present in data

    Args:
        data: Dictionary to check
        required_fields: List of required field names

    Returns:
        Tuple of (is_valid, error_message)
    """
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"

    return True, None


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input text

    Args:
        text: Text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Strip whitespace
    text = text.strip()

    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]

    # Remove null bytes
    text = text.replace('\x00', '')

    return text
