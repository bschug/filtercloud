from requests_cache import CachedSession


cache = CachedSession(cache_name='currency', backend='sqlite', expire_after=3600)

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


def get_currency_tiers(league, thresholds):
    prices = get_currency_prices(league)
    return sort_into_tiers(prices, thresholds)


def get_currency_prices(league):
    url = "http://poeninja.azureedge.net/api/Data/GetCurrencyOverview"
    response = cache.get(url, params={'league': league}).json()
    prices = {x['currencyTypeName']: x['receive']['value'] for x in response['lines']}

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
    if 'Scroll Fragment' not in prices:
        prices['Scroll Fragment'] = prices.get('Scroll of Wisdom', 0) / 5
    if 'Transmutation Shard' not in prices:
        prices['Transmutation Shard'] = prices['Orb of Transmutation'] / 20
    if 'Stacked Deck' not in prices:
        prices['Stacked Deck'] = 3

    return {x: prices.get(x, 0) for x in ALL_CURRENCY}


def sort_into_tiers(currency_prices, thresholds):
    return {
        'top_tier': [k for k, v in currency_prices.items() if v >= thresholds.top_tier],
        'valuable': [k for k, v in currency_prices.items() if v >= thresholds.valuable and v < thresholds.top_tier],
        'mediocre': [k for k, v in currency_prices.items() if v >= thresholds.worthless and v < thresholds.valuable],
        'worthless': [k for k, v in currency_prices.items() if v < thresholds.worthless],
    }
