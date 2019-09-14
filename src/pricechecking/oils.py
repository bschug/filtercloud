from collections import defaultdict
from datetime import datetime
import requests

from .utils import build_date_string, sort_into_tiers
from . import SEND_DATE_TO_POE_NINJA


def get_oil_tiers(league, thresholds, db):
    prices = get_oil_prices(league, db)
    return sort_into_tiers(prices, thresholds)


def get_oil_prices(league, db):
    return db.prices.find_one({'category': 'oils', 'league': league})['prices']


def update_oil_prices(league, db):
    print("Updating oil prices for", league)
    prices = scrape_oil_prices(league)
    dbentry = {'category': 'oils', 'league': league, 'prices': prices, 'date': datetime.now()}
    db.prices.replace_one({'category': 'oils', 'league': league}, dbentry, upsert=True)


def scrape_oil_prices(league):
    url = 'https://poe.ninja/api/data/itemoverview'
    params = {'league': league, 'type': 'Oil'}
    if SEND_DATE_TO_POE_NINJA:
        params['date'] = build_date_string()
    response = requests.get(url, params).json()
    prices = defaultdict(lambda: 0)
    for line in response['lines']:
        name = line['name']
        prices[name] = line['chaosValue']
    return prices
