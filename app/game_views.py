"""
Currency learning games and educational features
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import random
import logging

from .currencies import (
    SUPPORTED_CURRENCIES, CURRENCY_CODES, REGIONS,
    get_currency_info, get_currency_symbol, get_all_fun_facts
)
from .models import LearningProgress

logger = logging.getLogger(__name__)


def currency_quiz(request):
    """
    Interactive currency quiz game
    Test knowledge about different currencies
    """
    context = {
        'currencies': SUPPORTED_CURRENCIES,
        'regions': REGIONS,
    }
    return render(request, 'app/games/currency_quiz.html', context)


@require_http_methods(["GET"])
def generate_quiz_question(request):
    """
    Generate a random quiz question
    Returns JSON with question and answer options
    """
    try:
        question_type = request.GET.get('type', 'random')

        # Question types
        question_types = [
            'symbol_to_name',
            'name_to_symbol',
            'country_to_currency',
            'currency_to_country',
            'denomination',
            'fun_fact'
        ]

        if question_type == 'random':
            question_type = random.choice(question_types)

        # Generate question based on type
        if question_type == 'symbol_to_name':
            question_data = _generate_symbol_to_name_question()
        elif question_type == 'name_to_symbol':
            question_data = _generate_name_to_symbol_question()
        elif question_type == 'country_to_currency':
            question_data = _generate_country_to_currency_question()
        elif question_type == 'currency_to_country':
            question_data = _generate_currency_to_country_question()
        elif question_type == 'denomination':
            question_data = _generate_denomination_question()
        elif question_type == 'fun_fact':
            question_data = _generate_fun_fact_question()
        else:
            question_data = _generate_symbol_to_name_question()

        return JsonResponse({
            'success': True,
            'question': question_data
        })

    except Exception as e:
        logger.error(f"Error generating quiz question: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _generate_symbol_to_name_question():
    """Generate a question: What currency uses this symbol?"""
    correct_code = random.choice(CURRENCY_CODES)
    correct_info = get_currency_info(correct_code)

    # Generate wrong answers
    wrong_codes = random.sample([c for c in CURRENCY_CODES if c != correct_code], 3)
    options = [correct_info['name']] + [get_currency_info(c)['name'] for c in wrong_codes]
    random.shuffle(options)

    return {
        'type': 'symbol_to_name',
        'question': f'Which currency uses the symbol "{correct_info["symbol"]}"?',
        'options': options,
        'correct_answer': correct_info['name'],
        'hint': f'{correct_info["flag"]} This currency is from {correct_info["country"]}',
        'explanation': f'The {correct_info["symbol"]} symbol represents the {correct_info["name"]} from {correct_info["country"]}.'
    }


def _generate_name_to_symbol_question():
    """Generate a question: What is the symbol for this currency?"""
    correct_code = random.choice(CURRENCY_CODES)
    correct_info = get_currency_info(correct_code)

    # Generate wrong answers (other symbols)
    wrong_codes = random.sample([c for c in CURRENCY_CODES if c != correct_code], 3)
    options = [correct_info['symbol']] + [get_currency_info(c)['symbol'] for c in wrong_codes]
    random.shuffle(options)

    return {
        'type': 'name_to_symbol',
        'question': f'What is the symbol for {correct_info["name"]}?',
        'options': options,
        'correct_answer': correct_info['symbol'],
        'hint': f'{correct_info["flag"]} From {correct_info["country"]}',
        'explanation': f'The {correct_info["name"]} uses the symbol {correct_info["symbol"]}.'
    }


def _generate_country_to_currency_question():
    """Generate a question: What currency does this country use?"""
    correct_code = random.choice(CURRENCY_CODES)
    correct_info = get_currency_info(correct_code)

    # Generate wrong answers
    wrong_codes = random.sample([c for c in CURRENCY_CODES if c != correct_code], 3)
    options = [correct_info['name']] + [get_currency_info(c)['name'] for c in wrong_codes]
    random.shuffle(options)

    return {
        'type': 'country_to_currency',
        'question': f'{correct_info["flag"]} What currency is used in {correct_info["country"]}?',
        'options': options,
        'correct_answer': correct_info['name'],
        'hint': f'The symbol is {correct_info["symbol"]}',
        'explanation': f'{correct_info["country"]} uses the {correct_info["name"]} ({correct_code}).'
    }


def _generate_currency_to_country_question():
    """Generate a question: Which country uses this currency?"""
    correct_code = random.choice(CURRENCY_CODES)
    correct_info = get_currency_info(correct_code)

    # Generate wrong answers
    wrong_codes = random.sample([c for c in CURRENCY_CODES if c != correct_code], 3)
    options = [correct_info['country']] + [get_currency_info(c)['country'] for c in wrong_codes]
    random.shuffle(options)

    return {
        'type': 'currency_to_country',
        'question': f'Which country uses the {correct_info["name"]}?',
        'options': options,
        'correct_answer': correct_info['country'],
        'hint': f'{correct_info["flag"]} Symbol: {correct_info["symbol"]}',
        'explanation': f'The {correct_info["name"]} is the currency of {correct_info["country"]}.'
    }


def _generate_denomination_question():
    """Generate a question about denominations"""
    correct_code = random.choice([c for c in CURRENCY_CODES if 'denominations' in get_currency_info(c)])
    correct_info = get_currency_info(correct_code)

    # Check if has bills
    if 'bills' in correct_info['denominations'] and correct_info['denominations']['bills']:
        bills = correct_info['denominations']['bills']
        correct_bill = random.choice(bills)

        # Generate wrong answers
        all_bills = []
        for code in CURRENCY_CODES:
            info = get_currency_info(code)
            if 'denominations' in info and 'bills' in info['denominations']:
                all_bills.extend(info['denominations']['bills'])

        wrong_bills = random.sample([b for b in set(all_bills) if b != correct_bill], 3)
        options = [f'{correct_info["symbol"]}{correct_bill}'] + \
                  [f'{get_currency_symbol(random.choice(CURRENCY_CODES))}{b}' for b in wrong_bills]
        random.shuffle(options)

        return {
            'type': 'denomination',
            'question': f'Which of these is a real banknote denomination for {correct_info["name"]}?',
            'options': options,
            'correct_answer': f'{correct_info["symbol"]}{correct_bill}',
            'hint': f'{correct_info["flag"]} From {correct_info["country"]}',
            'explanation': f'The {correct_info["name"]} has a {correct_info["symbol"]}{correct_bill} banknote.'
        }
    else:
        # Fallback to another question type
        return _generate_symbol_to_name_question()


def _generate_fun_fact_question():
    """Generate a question based on fun facts"""
    # Find currencies with fun facts
    currencies_with_facts = [c for c in CURRENCY_CODES if get_all_fun_facts(c)]

    if not currencies_with_facts:
        return _generate_symbol_to_name_question()

    correct_code = random.choice(currencies_with_facts)
    correct_info = get_currency_info(correct_code)
    facts = get_all_fun_facts(correct_code)

    if not facts:
        return _generate_symbol_to_name_question()

    fact = random.choice(facts)

    # Generate wrong answers
    wrong_codes = random.sample([c for c in CURRENCY_CODES if c != correct_code], 3)
    options = [correct_info['name']] + [get_currency_info(c)['name'] for c in wrong_codes]
    random.shuffle(options)

    return {
        'type': 'fun_fact',
        'question': f'Which currency has this interesting fact: "{fact}"?',
        'options': options,
        'correct_answer': correct_info['name'],
        'hint': f'{correct_info["flag"]}',
        'explanation': f'This fun fact is about the {correct_info["name"]} from {correct_info["country"]}.'
    }


@require_http_methods(["POST"])
def submit_quiz_answer(request):
    """
    Check quiz answer and award points
    """
    try:
        import json
        data = json.loads(request.body)

        is_correct = data.get('is_correct', False)
        question_type = data.get('question_type', 'unknown')

        # Award points for correct answers
        points = 10 if is_correct else 2  # 10 for correct, 2 for participation

        # Track learning progress if user is authenticated
        if request.user.is_authenticated:
            LearningProgress.objects.create(
                user=request.user,
                activity_type='quiz_completed',
                details={
                    'question_type': question_type,
                    'is_correct': is_correct
                },
                points_earned=points
            )

        return JsonResponse({
            'success': True,
            'points_earned': points,
            'message': 'Correct! Great job!' if is_correct else 'Good try! Keep learning!'
        })

    except Exception as e:
        logger.error(f"Error submitting quiz answer: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def currency_comparison(request):
    """
    Compare multiple currencies side by side
    """
    # Get currency codes from query params
    codes = request.GET.getlist('codes')

    # Default to JPY, USD, EUR if none selected
    if not codes:
        codes = ['JPY', 'USD', 'EUR']

    # Validate and limit to 4 currencies
    codes = [c.upper() for c in codes if c.upper() in CURRENCY_CODES][:4]

    # Get currency information
    currencies = [get_currency_info(code) for code in codes]

    context = {
        'selected_currencies': currencies,
        'selected_codes': codes,
        'all_currencies': SUPPORTED_CURRENCIES,
        'currency_codes': CURRENCY_CODES,
    }

    return render(request, 'app/games/currency_comparison.html', context)


def travel_budget_game(request):
    """
    Travel budget simulator game
    Learn about currency exchange through virtual travel
    """
    context = {
        'currencies': SUPPORTED_CURRENCIES,
        'currency_codes': CURRENCY_CODES,
        'regions': REGIONS,
    }
    return render(request, 'app/games/travel_budget.html', context)
