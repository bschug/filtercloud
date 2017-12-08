import requests


def get_divcard_tiers(league, thresholds, db):
    prices = get_divcard_prices(league, db)
    return sort_into_tiers(prices, thresholds)


def get_divcard_prices(league, db):
    return db.prices.find_one({'category': 'divcards', 'league': league})['prices']


def update_divcard_prices(league, db):
    print("Updating divcard prices for", league)
    prices = scrape_divcard_prices(league)
    dbentry = {'category': 'divcards', 'league': league, 'prices': prices}
    db.prices.replace_one({'category': 'divcards', 'league': league}, dbentry, upsert=True)


def scrape_divcard_prices(league):
    prices = dict()
    url = "http://poe.ninja/api/Data/GetDivinationCardsOverview"
    response = requests.get(url, params={'league': league}).json()
    for item in response['lines']:
        prices[item['name']] = item['chaosValue']
    return prices


def sort_into_tiers(card_prices, thresholds):
    return {
        'top_tier': [k for k, v in card_prices.items() if v >= thresholds.top_tier],
        'valuable': [k for k, v in card_prices.items() if v >= thresholds.valuable and v < thresholds.top_tier],
        'mediocre': [k for k, v in card_prices.items() if v > thresholds.worthless and v < thresholds.valuable],
        'worthless': [k for k, v in card_prices.items() if v > thresholds.hidden and v <= thresholds.worthless],
        'hidden': [k for k, v in card_prices.items() if v < thresholds.hidden],
    }