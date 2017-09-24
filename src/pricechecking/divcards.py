import requests
from requests_cache import CachedSession


cache = CachedSession(cache_name='divcards', backend='sqlite', expire_after=3600)


def get_divcard_tiers(league, thresholds):
    prices = get_divcard_prices(league)
    return sort_into_tiers(prices, thresholds)


def get_divcard_prices(league):
    prices = dict()
    url = "http://poeninja.azureedge.net/api/Data/GetDivinationCardsOverview"
    response = cache.get(url, params={'league': league}).json()
    for item in response['lines']:
        prices[item['name']] = item['chaosValue']
    return prices


def sort_into_tiers(card_prices, thresholds):
    return {
        'top_tier': [k for k, v in card_prices.items() if v >= thresholds.top_tier],
        'valuable': [k for k, v in card_prices.items() if v >= thresholds.valuable and v < thresholds.top_tier],
        'mediocre': [k for k, v in card_prices.items() if v >= thresholds.worthless and v < thresholds.valuable],
        'worthless': [k for k, v in card_prices.items() if v < thresholds.worthless],
    }