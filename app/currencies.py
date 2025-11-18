"""
Centralized currency definitions and utilities
Supports 15+ major global currencies
"""

# Major world currencies with comprehensive metadata
SUPPORTED_CURRENCIES = {
    # Asia-Pacific
    'JPY': {
        'name': 'Japanese Yen',
        'name_ja': '日本円',
        'symbol': '¥',
        'flag': '🇯🇵',
        'country': 'Japan',
        'region': 'Asia',
        'denominations': {
            'coins': [1, 5, 10, 50, 100, 500],
            'bills': [1000, 2000, 5000, 10000]
        },
        'has_image_recognition': True,
        'fun_facts': [
            'The yen is the third most traded currency in the world',
            'Japanese coins have holes in the center for some denominations',
            'The ¥10,000 note features Yukichi Fukuzawa, a famous educator'
        ]
    },
    'TWD': {
        'name': 'Taiwan Dollar',
        'name_local': '新台幣',
        'symbol': 'NT$',
        'flag': '🇹🇼',
        'country': 'Taiwan',
        'region': 'Asia',
        'denominations': {
            'coins': [1, 5, 10, 50],
            'bills': [100, 200, 500, 1000, 2000]
        },
        'has_image_recognition': True,
        'fun_facts': [
            'TWD stands for "Taiwan Dollar"',
            'The NT$2000 note is relatively rare',
            'Taiwanese coins feature beautiful orchid designs'
        ]
    },
    'CNY': {
        'name': 'Chinese Yuan',
        'name_local': '人民币',
        'symbol': '¥',
        'flag': '🇨🇳',
        'country': 'China',
        'region': 'Asia',
        'denominations': {
            'coins': [1, 5],
            'bills': [1, 5, 10, 20, 50, 100]
        },
        'has_image_recognition': False,
        'fun_facts': [
            'Also called "Renminbi" (RMB)',
            'The yuan is one of the IMF Special Drawing Rights currencies',
            'Chinese currency features famous Chinese leaders'
        ]
    },
    'KRW': {
        'name': 'South Korean Won',
        'name_local': '대한민국 원',
        'symbol': '₩',
        'flag': '🇰🇷',
        'country': 'South Korea',
        'region': 'Asia',
        'denominations': {
            'coins': [10, 50, 100, 500],
            'bills': [1000, 5000, 10000, 50000]
        },
        'has_image_recognition': False,
        'fun_facts': [
            'Won means "round" in Korean',
            'The ₩50,000 note features the first female scholar Shin Saimdang',
            'Korean won has no decimal subdivisions'
        ]
    },
    'SGD': {
        'name': 'Singapore Dollar',
        'symbol': 'S$',
        'flag': '🇸🇬',
        'country': 'Singapore',
        'region': 'Asia',
        'denominations': {
            'coins': [0.05, 0.10, 0.20, 0.50, 1],
            'bills': [2, 5, 10, 50, 100, 1000]
        },
        'has_image_recognition': False,
        'fun_facts': [
            'Singapore has polymer (plastic) banknotes',
            'The currency is managed by the Monetary Authority of Singapore',
            'S$1000 notes are rarely seen in daily transactions'
        ]
    },
    'THB': {
        'name': 'Thai Baht',
        'name_local': 'บาท',
        'symbol': '฿',
        'flag': '🇹🇭',
        'country': 'Thailand',
        'region': 'Asia',
        'denominations': {
            'coins': [1, 2, 5, 10],
            'bills': [20, 50, 100, 500, 1000]
        },
        'has_image_recognition': False,
        'fun_facts': [
            'Thai baht is one of the strongest currencies in Southeast Asia',
            'All banknotes feature the Thai King',
            'The word "baht" also means a unit of weight for gold'
        ]
    },
    'INR': {
        'name': 'Indian Rupee',
        'name_local': '₹',
        'symbol': '₹',
        'flag': '🇮🇳',
        'country': 'India',
        'region': 'Asia',
        'denominations': {
            'coins': [1, 2, 5, 10, 20],
            'bills': [10, 20, 50, 100, 200, 500, 2000]
        },
        'has_image_recognition': False,
        'fun_facts': [
            'The ₹ symbol was officially adopted in 2010',
            'India has 22 official languages on its currency',
            'Indian rupees come in many vibrant colors'
        ]
    },

    # Americas
    'USD': {
        'name': 'US Dollar',
        'symbol': '$',
        'flag': '🇺🇸',
        'country': 'United States',
        'region': 'Americas',
        'denominations': {
            'coins': [0.01, 0.05, 0.10, 0.25, 0.50, 1],
            'bills': [1, 2, 5, 10, 20, 50, 100]
        },
        'has_image_recognition': False,
        'fun_facts': [
            'Most traded currency in the world',
            'The dollar sign $ may have originated from the Spanish peso',
            'US currency features famous American presidents'
        ]
    },
    'CAD': {
        'name': 'Canadian Dollar',
        'symbol': 'C$',
        'flag': '🇨🇦',
        'country': 'Canada',
        'region': 'Americas',
        'denominations': {
            'coins': [0.05, 0.10, 0.25, 1, 2],
            'bills': [5, 10, 20, 50, 100]
        },
        'has_image_recognition': False,
        'fun_facts': [
            'Canadian dollars are called "loonies" (C$1) and "toonies" (C$2)',
            'Canadian banknotes are made of polymer',
            'Canada stopped producing pennies in 2012'
        ]
    },
    'MXN': {
        'name': 'Mexican Peso',
        'symbol': 'MX$',
        'flag': '🇲🇽',
        'country': 'Mexico',
        'region': 'Americas',
        'denominations': {
            'coins': [0.50, 1, 2, 5, 10, 20],
            'bills': [20, 50, 100, 200, 500, 1000]
        },
        'has_image_recognition': False,
        'fun_facts': [
            'The peso is one of the oldest currencies in the Americas',
            'Mexican pesos feature important historical figures',
            'The $ symbol originated from the Mexican peso'
        ]
    },

    # Europe
    'EUR': {
        'name': 'Euro',
        'symbol': '€',
        'flag': '🇪🇺',
        'country': 'European Union',
        'region': 'Europe',
        'denominations': {
            'coins': [0.01, 0.02, 0.05, 0.10, 0.20, 0.50, 1, 2],
            'bills': [5, 10, 20, 50, 100, 200, 500]
        },
        'has_image_recognition': False,
        'fun_facts': [
            'Used by 19 European Union countries',
            'Second most traded currency globally',
            'Euro coins have a common European side and a national side'
        ]
    },
    'GBP': {
        'name': 'British Pound',
        'symbol': '£',
        'flag': '🇬🇧',
        'country': 'United Kingdom',
        'region': 'Europe',
        'denominations': {
            'coins': [0.01, 0.02, 0.05, 0.10, 0.20, 0.50, 1, 2],
            'bills': [5, 10, 20, 50]
        },
        'has_image_recognition': False,
        'fun_facts': [
            'Oldest currency still in use',
            'The pound is nicknamed "quid" or "sterling"',
            'UK banknotes are now made of polymer'
        ]
    },
    'CHF': {
        'name': 'Swiss Franc',
        'symbol': 'CHF',
        'flag': '🇨🇭',
        'country': 'Switzerland',
        'region': 'Europe',
        'denominations': {
            'coins': [0.05, 0.10, 0.20, 0.50, 1, 2, 5],
            'bills': [10, 20, 50, 100, 200, 1000]
        },
        'has_image_recognition': False,
        'fun_facts': [
            'Known for stability and used as a safe haven',
            'Swiss franc notes are known for their security features',
            'Switzerland has some of the most beautiful currency designs'
        ]
    },

    # Oceania
    'AUD': {
        'name': 'Australian Dollar',
        'symbol': 'A$',
        'flag': '🇦🇺',
        'country': 'Australia',
        'region': 'Oceania',
        'denominations': {
            'coins': [0.05, 0.10, 0.20, 0.50, 1, 2],
            'bills': [5, 10, 20, 50, 100]
        },
        'has_image_recognition': False,
        'fun_facts': [
            'First country to use polymer banknotes (1988)',
            'Australian coins feature native animals',
            'The A$5 note has a clear window for security'
        ]
    },
    'NZD': {
        'name': 'New Zealand Dollar',
        'symbol': 'NZ$',
        'flag': '🇳🇿',
        'country': 'New Zealand',
        'region': 'Oceania',
        'denominations': {
            'coins': [0.10, 0.20, 0.50, 1, 2],
            'bills': [5, 10, 20, 50, 100]
        },
        'has_image_recognition': False,
        'fun_facts': [
            'Also called the "Kiwi" dollar',
            'All NZ banknotes are polymer',
            'Features famous New Zealanders and native birds'
        ]
    },
}

# Quick lookup lists
CURRENCY_CODES = list(SUPPORTED_CURRENCIES.keys())
IMAGE_RECOGNITION_SUPPORTED = [code for code, data in SUPPORTED_CURRENCIES.items() if data.get('has_image_recognition', False)]

# Region groupings
REGIONS = {
    'Asia': ['JPY', 'TWD', 'CNY', 'KRW', 'SGD', 'THB', 'INR'],
    'Americas': ['USD', 'CAD', 'MXN'],
    'Europe': ['EUR', 'GBP', 'CHF'],
    'Oceania': ['AUD', 'NZD'],
}


def get_currency_info(code):
    """Get currency information by code"""
    return SUPPORTED_CURRENCIES.get(code.upper())


def get_currency_symbol(code):
    """Get currency symbol"""
    info = get_currency_info(code)
    return info['symbol'] if info else code


def get_currency_name(code):
    """Get currency full name"""
    info = get_currency_info(code)
    return info['name'] if info else code


def get_currencies_by_region(region):
    """Get all currencies in a region"""
    return REGIONS.get(region, [])


def has_image_recognition(code):
    """Check if currency has image recognition support"""
    info = get_currency_info(code)
    return info.get('has_image_recognition', False) if info else False


def get_fun_fact(code, index=0):
    """Get a fun fact about the currency"""
    info = get_currency_info(code)
    if info and 'fun_facts' in info:
        facts = info['fun_facts']
        if facts and 0 <= index < len(facts):
            return facts[index]
    return None


def get_all_fun_facts(code):
    """Get all fun facts about the currency"""
    info = get_currency_info(code)
    return info.get('fun_facts', []) if info else []
