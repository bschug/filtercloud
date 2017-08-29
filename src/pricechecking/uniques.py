from collections import defaultdict
import requests


# Fated Uniques can only be acquired from prophecies, not dropped by enemies.
# We should not take those into account for highlighting purposes.
FATED_UNIQUES = {
    'Amplification Rod',
    'Cragfall',
    'Death\'s Opus',
    'Deidbellow',
    'Doomfletch\'s Prism',
    'Ezomyte Hold',
    'Hrimburn',
    'Hrimnor\'s Dirge',
    'Kaltensoul',
    'Kaom\'s Way',
    'Karui Charge',
    'Martyr\'s Crown',
    'Ngamahu Tiki',
    'Queen\'s Escape',
    'Realm Ender',
    'Shavronne\'s Gambit',
    'Silverbough',
    'The Cauteriser',
    'The Gryphon',
    'The Oak',
    'The Signal Fire',
    'The Tempest',
    'Thirst for Horrors',
    'Wall of Brambles',
    'Voidheart'
}


def get_unique_classes(league, thresholds):
    """Sort uniques into classes by value (top tier, decent, mediocre, worthless)"""
    unique_prices = get_unique_prices(league)
    return sort_by_value(unique_prices, thresholds)


def get_unique_prices(league):
    unique_prices = defaultdict(lambda: 0)
    get_unique_prices_from_url('http://cdn.poe.ninja/api/Data/GetUniqueWeaponOverview', league, unique_prices)
    get_unique_prices_from_url('http://cdn.poe.ninja/api/Data/GetUniqueArmourOverview', league, unique_prices)
    get_unique_prices_from_url('http://cdn.poe.ninja/api/Data/GetUniqueAccessoryOverview', league, unique_prices)
    get_unique_prices_from_url('http://cdn.poe.ninja/api/Data/GetUniqueFlaskOverview', league, unique_prices)
    return unique_prices


def get_unique_prices_from_url(url, league, unique_prices):
    response = requests.get(url, {'league': league}).json()
    for item in response['lines']:
        if item['name'] in FATED_UNIQUES:
            continue
        unique_prices[item['baseType']] = max(unique_prices[item['baseType']], item['chaosValue'])


def sort_by_value(unique_prices, thresholds):
    return {
        'top_tier': [k for k, v in unique_prices.items() if v >= thresholds.top_tier],
        'valuable': [k for k, v in unique_prices.items() if v >= thresholds.valuable and v < thresholds.top_tier],
        'mediocre': [k for k, v in unique_prices.items() if v >= thresholds.worthless and v < thresholds.valuable],
        'worthless': [k for k, v in unique_prices.items() if v < thresholds.worthless],
    }