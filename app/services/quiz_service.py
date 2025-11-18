"""
Quiz Service
Handles quiz question generation and answer validation
"""
import random
import logging
from typing import Optional, Dict, List
from collections import Counter

from ..currencies import (
    SUPPORTED_CURRENCIES, CURRENCY_CODES,
    get_currency_info, get_all_fun_facts
)

logger = logging.getLogger(__name__)


class QuizService:
    """Service for generating and managing quiz questions"""

    QUESTION_TYPES = [
        'symbol_to_name',
        'name_to_symbol',
        'country_to_currency',
        'currency_to_country',
        'denomination',
        'fun_fact'
    ]

    NUM_OPTIONS = 4  # Number of multiple choice options

    @classmethod
    def generate_question(cls, question_type: str = 'random') -> Optional[Dict]:
        """
        Generate a quiz question

        Args:
            question_type: Type of question to generate or 'random'

        Returns:
            Dictionary containing question data or None if failed
        """
        try:
            # Select question type
            if question_type == 'random':
                question_type = random.choice(cls.QUESTION_TYPES)

            # Generate question based on type
            generators = {
                'symbol_to_name': cls._generate_symbol_to_name,
                'name_to_symbol': cls._generate_name_to_symbol,
                'country_to_currency': cls._generate_country_to_currency,
                'currency_to_country': cls._generate_currency_to_country,
                'denomination': cls._generate_denomination,
                'fun_fact': cls._generate_fun_fact
            }

            generator = generators.get(question_type)
            if not generator:
                logger.error(f"Unknown question type: {question_type}")
                return None

            return generator()

        except Exception as e:
            logger.error(f"Error generating question: {e}", exc_info=True)
            return None

    @classmethod
    def _generate_symbol_to_name(cls) -> Dict:
        """Generate: What currency uses this symbol?"""
        correct_code = random.choice(CURRENCY_CODES)
        correct_info = get_currency_info(correct_code)

        # Generate wrong answers
        wrong_codes = random.sample(
            [c for c in CURRENCY_CODES if c != correct_code],
            cls.NUM_OPTIONS - 1
        )
        options = [correct_info['name']] + [
            get_currency_info(c)['name'] for c in wrong_codes
        ]
        random.shuffle(options)

        return {
            'type': 'symbol_to_name',
            'question': f'Which currency uses the symbol "{correct_info["symbol"]}"?',
            'options': options,
            'correct_answer': correct_info['name'],
            'hint': f'{correct_info["flag"]} From {correct_info["country"]}',
            'explanation': f'The {correct_info["symbol"]} symbol represents the {correct_info["name"]} from {correct_info["country"]}.'
        }

    @classmethod
    def _generate_name_to_symbol(cls) -> Dict:
        """Generate: What is the symbol for this currency?"""
        correct_code = random.choice(CURRENCY_CODES)
        correct_info = get_currency_info(correct_code)

        # Generate wrong answers (other symbols)
        wrong_codes = random.sample(
            [c for c in CURRENCY_CODES if c != correct_code],
            cls.NUM_OPTIONS - 1
        )
        options = [correct_info['symbol']] + [
            get_currency_info(c)['symbol'] for c in wrong_codes
        ]
        random.shuffle(options)

        return {
            'type': 'name_to_symbol',
            'question': f'What is the symbol for {correct_info["name"]}?',
            'options': options,
            'correct_answer': correct_info['symbol'],
            'hint': f'{correct_info["flag"]} From {correct_info["country"]}',
            'explanation': f'The {correct_info["name"]} uses the symbol {correct_info["symbol"]}.'
        }

    @classmethod
    def _generate_country_to_currency(cls) -> Dict:
        """Generate: What currency does this country use?"""
        correct_code = random.choice(CURRENCY_CODES)
        correct_info = get_currency_info(correct_code)

        # Generate wrong answers
        wrong_codes = random.sample(
            [c for c in CURRENCY_CODES if c != correct_code],
            cls.NUM_OPTIONS - 1
        )
        options = [correct_info['name']] + [
            get_currency_info(c)['name'] for c in wrong_codes
        ]
        random.shuffle(options)

        return {
            'type': 'country_to_currency',
            'question': f'{correct_info["flag"]} What currency is used in {correct_info["country"]}?',
            'options': options,
            'correct_answer': correct_info['name'],
            'hint': f'The symbol is {correct_info["symbol"]}',
            'explanation': f'{correct_info["country"]} uses the {correct_info["name"]} ({correct_code}).'
        }

    @classmethod
    def _generate_currency_to_country(cls) -> Dict:
        """Generate: Which country uses this currency?"""
        correct_code = random.choice(CURRENCY_CODES)
        correct_info = get_currency_info(correct_code)

        # Generate wrong answers
        wrong_codes = random.sample(
            [c for c in CURRENCY_CODES if c != correct_code],
            cls.NUM_OPTIONS - 1
        )
        options = [correct_info['country']] + [
            get_currency_info(c)['country'] for c in wrong_codes
        ]
        random.shuffle(options)

        return {
            'type': 'currency_to_country',
            'question': f'Which country uses the {correct_info["name"]}?',
            'options': options,
            'correct_answer': correct_info['country'],
            'hint': f'{correct_info["flag"]} Symbol: {correct_info["symbol"]}',
            'explanation': f'The {correct_info["name"]} is the currency of {correct_info["country"]}.'
        }

    @classmethod
    def _generate_denomination(cls) -> Dict:
        """Generate: Which is a real denomination?"""
        # Select currency with denominations
        currencies_with_denom = [
            c for c in CURRENCY_CODES
            if 'denominations' in get_currency_info(c)
            and get_currency_info(c)['denominations'].get('bills')
        ]

        if not currencies_with_denom:
            # Fallback to another question type
            return cls._generate_symbol_to_name()

        correct_code = random.choice(currencies_with_denom)
        correct_info = get_currency_info(correct_code)
        bills = correct_info['denominations']['bills']

        correct_bill = random.choice(bills)

        # Generate wrong answers
        all_bills = []
        for code in CURRENCY_CODES:
            info = get_currency_info(code)
            if 'denominations' in info and 'bills' in info['denominations']:
                all_bills.extend(info['denominations']['bills'])

        wrong_bills = random.sample(
            [b for b in set(all_bills) if b != correct_bill],
            cls.NUM_OPTIONS - 1
        )

        options = [f'{correct_info["symbol"]}{correct_bill}'] + [
            f'{correct_info["symbol"]}{b}' for b in wrong_bills
        ]
        random.shuffle(options)

        return {
            'type': 'denomination',
            'question': f'Which is a real banknote denomination for {correct_info["name"]}?',
            'options': options,
            'correct_answer': f'{correct_info["symbol"]}{correct_bill}',
            'hint': f'{correct_info["flag"]} From {correct_info["country"]}',
            'explanation': f'The {correct_info["name"]} has a {correct_info["symbol"]}{correct_bill} banknote.'
        }

    @classmethod
    def _generate_fun_fact(cls) -> Dict:
        """Generate: Which currency has this fun fact?"""
        # Find currencies with fun facts
        currencies_with_facts = [
            c for c in CURRENCY_CODES
            if get_all_fun_facts(c)
        ]

        if not currencies_with_facts:
            # Fallback
            return cls._generate_symbol_to_name()

        correct_code = random.choice(currencies_with_facts)
        correct_info = get_currency_info(correct_code)
        facts = get_all_fun_facts(correct_code)

        fact = random.choice(facts)

        # Generate wrong answers
        wrong_codes = random.sample(
            [c for c in CURRENCY_CODES if c != correct_code],
            cls.NUM_OPTIONS - 1
        )
        options = [correct_info['name']] + [
            get_currency_info(c)['name'] for c in wrong_codes
        ]
        random.shuffle(options)

        return {
            'type': 'fun_fact',
            'question': f'Which currency has this fact: "{fact}"?',
            'options': options,
            'correct_answer': correct_info['name'],
            'hint': f'{correct_info["flag"]}',
            'explanation': f'This is about the {correct_info["name"]} from {correct_info["country"]}.'
        }

    @staticmethod
    def calculate_points(is_correct: bool, streak: int = 0) -> int:
        """
        Calculate points earned for an answer

        Args:
            is_correct: Whether answer was correct
            streak: Current streak count

        Returns:
            Points earned
        """
        if not is_correct:
            return 2  # Participation points

        # Base points for correct answer
        points = 10

        # Bonus for streak
        if streak >= 5:
            points += 5  # Hot streak bonus
        elif streak >= 3:
            points += 2  # Good streak bonus

        return points
