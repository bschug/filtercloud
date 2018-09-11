from collections import defaultdict
import requests

from .utils import build_date_string, sort_into_tiers


def get_fossil_tiers(league, thresholds, db):
    prices = get_fossil_prices(league, db)
    return sort_into_tiers(prices, thresholds)


def get_fossil_prices(league, db):
    return db.prices.find_one({'category': 'fossils', 'league': league})['prices']


def update_fossil_prices(league, db):
    print("Updating fossil prices for", league)
    prices = scrape_fossil_prices(league)
    dbentry = {'category': 'fossils', 'league': league, 'prices': prices}
    db.prices.replace_one({'category': 'fossils', 'league': league}, dbentry, upsert=True)


def scrape_fossil_prices(league):
    url = "https://poe.ninja/api/data/itemoverview"
    params = {'league': league, 'type': 'Fossil', 'date': build_date_string()}
    response = requests.get(url, params).json()
    prices = defaultdict(lambda: 0)
    for line in response['lines']:
        name = line['name']
        prices[name] = line['chaosValue']
    return prices

