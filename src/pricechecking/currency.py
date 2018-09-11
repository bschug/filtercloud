import requests
from collections import defaultdict

from .utils import build_date_string, sort_into_tiers


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


def get_currency_tiers(league, thresholds, db):
    prices = get_currency_prices(league, db)
    return sort_into_tiers(prices, thresholds)


def get_currency_prices(league, db):
    return db.prices.find_one({'category': 'currency', 'league': league})['prices']


def update_currency_prices(league, db):
    print("Updating currency prices for", league)
    prices = scrape_currency_prices(league)
    dbentry = {'category': 'currency', 'league': league, 'prices': prices}
    db.prices.replace_one({'category': 'currency', 'league': league}, dbentry, upsert=True)


def scrape_currency_prices(league):
    url = "https://poe.ninja/api/data/currencyoverview"
    response = requests.get(url, params={'league': league, 'type': 'Currency', 'date': build_date_string()}).json()
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

