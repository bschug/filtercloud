from collections import defaultdict
import requests

from .utils import build_date_string, sort_into_tiers


def get_resonator_tiers(league, thresholds, db):
    prices = get_resonator_prices(league, db)
    return sort_into_tiers(prices, thresholds)


def get_resonator_prices(league, db):
    dbentry = db.prices.find_one({'category': 'resonators', 'league': league})
    if dbentry is None or 'prices' not in dbentry:
        return {}
    return dbentry['prices']


def update_resonator_prices(league, db):
    print("Updating resonator prices for", league)
    prices = scrape_resonator_prices(league)
    dbentry = {'category': 'resonators', 'league': league, 'prices': prices}
    db.prices.replace_one({'category': 'resonators', 'league': league}, dbentry, upsert=True)


def scrape_resonator_prices(league):
    url = 'https://poe.ninja/api/data/itemoverview'
    params = {'league': league, 'type': 'Resonator', 'date': build_date_string()}
    response = requests.get(url, params).json()
    prices = defaultdict(lambda: 0)
    for line in response['lines']:
        name = line['name']
        prices[name] = line['chaosValue']
    return prices
