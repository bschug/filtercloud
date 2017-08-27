import requests


def get_divcard_categories(league, thresholds):
    prices = get_divcard_prices(league)
    return sort_into_categories(prices, thresholds)


def get_divcard_prices(league):
    prices = dict()
    url = "http://poeninja.azureedge.net/api/Data/GetDivinationCardsOverview"
    response = requests.get(url, {'league': league}).json()
    for item in response['lines']:
        prices[item['name']] = item['chaosValue']
    return prices


def sort_into_categories(card_prices, thresholds):
    return {
        'top_tier': [k for k, v in card_prices.items() if v >= thresholds.top_tier],
        'valuable': [k for k, v in card_prices.items() if v >= thresholds.valuable],
        'mediocre': [k for k, v in card_prices.items() if v >= thresholds.worthless],
        'worthless': [k for k, v in card_prices.items() if v < thresholds.worthless],
    }