from collections import defaultdict

import requests
from requests_cache import CachedSession


cache = CachedSession(cache_name='uniques', backend='sqlite', expire_after=3600)


# Some Uniques can only be acquired from prophecies / breachstones, not dropped by enemies.
# We should not take those into account for highlighting purposes.
BLACKLIST = {
    # Prophecy Uniques
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
    'Voidheart',

    # Breach Uniques
    "Xoph's Nurture",
    "The Formless Inferno",
    "Xoph's Blood",
    "Tulfall",
    "The Perfect Form",
    "The Pandemonius",
    "Hand of Wisdom and Action",
    "Esh's Visage",
    "Choir of the Storm",
    "Uul-Netol's Embrace",
    "The Red Trail",
    "The Surrender",
    "United in Dream",
    "Skin of the Lords",
    "The Red Nightmare",
    "The Green Nightmare",
    "The Blue Nightmare",
}


def get_unique_tiers(league, thresholds):
    """Sort uniques into classes by value (top tier, decent, mediocre, worthless)"""
    unique_prices = get_unique_prices(league)
    return sort_into_tiers(unique_prices, thresholds)


def get_unique_prices(league):
    unique_prices = defaultdict(lambda: 0)
    get_unique_prices_from_url('http://poe.ninja/api/Data/GetUniqueWeaponOverview', league, unique_prices)
    get_unique_prices_from_url('http://poe.ninja/api/Data/GetUniqueArmourOverview', league, unique_prices)
    get_unique_prices_from_url('http://poe.ninja/api/Data/GetUniqueAccessoryOverview', league, unique_prices)
    get_unique_prices_from_url('http://poe.ninja/api/Data/GetUniqueFlaskOverview', league, unique_prices)
    return unique_prices


def get_unique_prices_from_url(url, league, unique_prices):
    response = cache.get(url, params={'league': league}).json()
    for item in response['lines']:
        # Fated uniques are created by prophecies, not dropped.
        if item['name'] in BLACKLIST:
            continue
        # All six-linkable items have 3 entries: regular, 5link and 6link. We only want regular.
        if item['links'] >= 5:
            continue
        unique_prices[item['baseType']] = max(unique_prices[item['baseType']], item['chaosValue'])


def sort_into_tiers(unique_prices, thresholds):
    return {
        'top_tier': [k for k, v in unique_prices.items() if v >= thresholds.top_tier],
        'valuable': [k for k, v in unique_prices.items() if v >= thresholds.valuable and v < thresholds.top_tier],
        'mediocre': [k for k, v in unique_prices.items() if v > thresholds.worthless and v < thresholds.valuable],
        'worthless': [k for k, v in unique_prices.items() if v > thresholds.hidden and v <= thresholds.worthless],
        'hidden': [k for k, v in unique_prices.items() if v < thresholds.hidden],
    }