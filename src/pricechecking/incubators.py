from datetime import datetime
import math
import requests
from collections import defaultdict

from .utils import build_date_string, sort_into_tiers
from . import SEND_DATE_TO_POE_NINJA


def get_incubator_tiers(league, thresholds, db):
    prices = get_incubator_prices(league, db)
    return sort_into_tiers(prices, thresholds)


def get_incubator_prices(league, db):
    return db.prices.find_one({'category': 'incubator', 'league': league})['prices']


def update_incubator_prices(league, db):
    print("Updating incubator prices for", league)
    prices = scrape_incubator_prices(league)
    dbentry = {'category': 'incubator', 'league': league, 'prices': prices, 'date': datetime.now()}
    db.prices.replace_one({'category': 'incubator', 'league': league}, dbentry, upsert=True)


def scrape_incubator_prices(league):
    prices = dict()
    url = "http://poe.ninja/api/data/itemoverview"
    params = {'league': league, 'type': 'Incubator'}
    if SEND_DATE_TO_POE_NINJA:
        params['date'] = build_date_string()
    response = requests.get(url, params=params).json()
    for item in response['lines']:
        prices[item['name']] = item['chaosValue']
    return prices