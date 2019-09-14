from datetime import datetime
import math
import requests
from collections import defaultdict

from .utils import build_date_string, sort_into_tiers
from . import SEND_DATE_TO_POE_NINJA


# We use an explicit list of currencies because poe.ninja is missing some currencies (like Alchemy Shards) and contains
# others we don't want (like Breach Splinters)
ALL_CURRENCY = [
    'Armourer\'s Scrap',
    'Blacksmith\'s Whetstone',
    'Blessed Orb',
    'Cartographer\'s Chisel',
    'Chaos Orb', 'Chaos Shard',
    'Chromatic Orb',
    'Divine Orb',
    'Exalted Orb', 'Exalted Shard',
    'Gemcutter\'s Prism',
    'Glassblower\'s Bauble',
    'Jeweller\'s Orb',
    'Apprentice Cartographer\'s Sextant',
    'Journeyman Cartographer\'s Sextant',
    'Master Cartographer\'s Sextant',
    'Mirror of Kalandra', 'Mirror Shard',
    'Orb of Alchemy', 'Alchemy Shard',
    'Orb of Alteration', 'Alteration Shard',
    'Orb of Augmentation',
    'Orb of Chance',
    'Orb of Fusing',
    'Orb of Regret',
    'Orb of Scouring',
    'Orb of Transmutation', 'Transmutation Shard',
    'Perandus Coin',
    'Portal Scroll',
    'Scroll of Wisdom', 'Scroll Fragment',
    'Regal Orb', 'Regal Shard',
    'Silver Coin',
    'Stacked Deck',
    'Vaal Orb',

    # Harbinger
    'Ancient Orb', 'Ancient Shard',
    'Orb of Annulment', 'Annulment Shard',
    'Orb of Binding', 'Binding Shard',
    'Orb of Horizons', 'Horizon Shard',
    'Engineer\'s Orb', 'Engineer\'s Shard',
    'Harbinger\'s Orb', 'Harbinger\'s Shard'
]

STACK_SIZES = {
    'Armourer\'s Scrap': 40,
    'Blacksmith\'s Whetstone': 20,
    'Blessed Orb': 20,
    'Cartographer\'s Chisel': 20,
    'Chaos Orb': 10, 'Chaos Shard': 20,
    'Chromatic Orb': 20,
    'Divine Orb': 10,
    'Exalted Orb': 10, 'Exalted Shard': 20,
    'Gemcutter\'s Prism': 20,
    'Glassblower\'s Bauble': 20,
    'Jeweller\'s Orb': 20,
    'Apprentice Cartographer\'s Sextant': 10,
    'Journeyman Cartographer\'s Sextant': 10,
    'Master Cartographer\'s Sextant': 10,
    'Mirror of Kalandra': 10, 'Mirror Shard': 20,
    'Orb of Alchemy': 10, 'Alchemy Shard': 20,
    'Orb of Alteration': 20, 'Alteration Shard': 20,
    'Orb of Augmentation': 30,
    'Orb of Chance': 20,
    'Orb of Fusing': 20,
    'Orb of Regret': 40,
    'Orb of Scouring': 30,
    'Orb of Transmutation': 40, 'Transmutation Shard': 20,
    'Perandus Coin': 1000,
    'Portal Scroll': 40,
    'Scroll of Wisdom': 40, 'Scroll Fragment': 5,
    'Regal Orb': 10, 'Regal Shard': 20,
    'Silver Coin': 30,
    'Stacked Deck': 10,
    'Vaal Orb': 10,

    # Harbinger
    'Ancient Orb': 20, 'Ancient Shard': 20,
    'Orb of Annulment': 20, 'Annulment Shard': 20,
    'Orb of Binding': 20, 'Binding Shard': 20,
    'Orb of Horizons': 20, 'Horizon Shard': 20,
    'Engineer\'s Orb': 20, 'Engineer\'s Shard': 20,
    'Harbinger\'s Orb': 20, 'Harbinger\'s Shard': 20
}


def get_currency_tiers(league, thresholds, db):
    prices = get_currency_prices(league, db)
    return sort_into_tiers(prices, thresholds)


def get_currency_prices(league, db):
    return db.prices.find_one({'category': 'currency', 'league': league})['prices']


def get_date(league, db):
    return db.prices.find_one({'category': 'currency', 'league': league})['date']


def update_currency_prices(league, db):
    print("Updating currency prices for", league)
    prices = scrape_currency_prices(league)
    dbentry = {'category': 'currency', 'league': league, 'prices': prices, 'date': datetime.now()}
    db.prices.replace_one({'category': 'currency', 'league': league}, dbentry, upsert=True)


def scrape_currency_prices(league):
    url = "https://poe.ninja/api/data/currencyoverview"
    params = {'league': league, 'type': 'Currency'}
    if SEND_DATE_TO_POE_NINJA:
        params['date'] = build_date_string()
    response = requests.get(url, params=params).json()
    prices = defaultdict(lambda: 0)

    for line in response['lines']:
        name = line['currencyTypeName']
        if line.get('receive') is not None:
            prices[name] = line['receive']['value']
        elif line.get('pay') is not None:
            prices[name] = line['pay']['value']

    # Some currencies may be missing from poe.ninja. If possible, fill them with sensible defaults
    if 'Mirror of Kalandra' not in prices and 'Mirror Shard' in prices:
        prices['Mirror of Kalandra'] = prices['Mirror Shard'] * 20
    if 'Mirror of Kalandra' not in prices:
        prices['Mirror of Kalandra'] = prices['Exalted Orb'] * 150
    if 'Alchemy Shard' not in prices:
        prices['Alchemy Shard'] = prices['Orb of Alchemy'] / 20
    if 'Alteration Shard' not in prices:
        prices['Alteration Shard'] = prices['Orb of Alteration'] / 20
    if 'Ancient Shard' not in prices:
        prices['Ancient Shard'] = prices.get('Ancient Orb', 0) / 20
    if 'Annulment Shard' not in prices:
        prices['Annulment Shard'] = prices.get('Orb of Annulment', 0) / 20
    if 'Binding Shard' not in prices:
        prices['Binding Shard'] = prices.get('Orb of Binding', 0) / 20
    if 'Chaos Orb' not in prices:
        prices['Chaos Orb'] = 1
    if 'Chaos Shard' not in prices:
        prices['Chaos Shard'] = 1 / 20
    if "Engineer's Shard" not in prices:
        prices["Engineer's Shard"] = prices.get("Engineer's Orb", 0) / 20
    if 'Exalted Shard' not in prices:
        prices['Exalted Shard'] = prices['Exalted Orb'] / 20
    if "Harbinger's Shard" not in prices:
        prices["Harbinger's Shard"] = prices.get("Harbinger's Orb", 0) / 20
    if 'Horizon Shard' not in prices:
        prices['Horizon Shard'] = prices.get('Orb of Horizons', 0) / 20
    if 'Mirror Shard' not in prices:
        prices['Mirror Shard'] = prices['Mirror of Kalandra'] / 20
    if 'Regal Shard' not in prices:
        prices['Regal Shard'] = prices['Regal Orb'] / 20
    if 'Scroll of Wisdom' not in prices:
        prices['Scroll of Wisdom'] = 1 / 200
    if 'Portal Scroll' not in prices:
        prices['Portal Scroll'] = 1 / 80
    if 'Scroll Fragment' not in prices:
        prices['Scroll Fragment'] = prices.get('Scroll of Wisdom', 0) / 5
    if 'Transmutation Shard' not in prices:
        prices['Transmutation Shard'] = prices['Orb of Transmutation'] / 20
    if 'Stacked Deck' not in prices:
        prices['Stacked Deck'] = 3

    return {x: prices.get(x, 0) for x in ALL_CURRENCY}


def build_currency_stacks(league, thresholds, blacklist, db):
    """
    Returns list of stacks that exceed the given thresholds.
    For items with a known stack size limit, only generate entries below that limit.

    :param thresholds: User-configured value thresholds
    :param blacklist: List of basetypes that shouldn't have stacks
    :param db: Database connection
    :return: {
        'top_tier': [
            { 'base_type': 'Chaos Orb', 'stack_size': 50 },
            { 'base_type': 'Perandus Coin', 'stack_size': 1247 }
        ],
        'valuable': [...],
        ...
    }
    """
    result = defaultdict(lambda: [])
    prices = get_currency_prices(league=league, db=db)
    for k,v in prices.items():
        if k in blacklist:
            continue
        for tk,tv in thresholds.items():
            tk = threshold_to_stack_name(tk)
            stack_size = math.ceil(tv / v)
            if stack_size > STACK_SIZES.get(k, math.inf):
                continue
            if stack_size <= 1:
                continue
            result[tk].append({
                'base_type': k,
                'stack_size': stack_size
            })
    return result


def threshold_to_stack_name(threshold):
    """
    The thresholds for worthless and hidden are upper bounds, while the other
    thresholds are lower bounds. Therefore, anything above the worthless threshold
    is mediocre, and anything above the hidden threshold is worthless.
    """
    if threshold == 'worthless':
        return 'mediocre'
    if threshold == 'hidden':
        return 'worthless'
    return threshold
