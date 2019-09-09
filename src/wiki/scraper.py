import json
import requests

from .constants import *
from .selector import update_selectors


def scrape_wiki(db):
    """Runs the wiki scraper and rebuilds the selectors. For use with concurrent.futures."""
    scraper = WikiScraper(db)
    scraper.scrape_items()
    update_selectors(db)
    print("Wiki Scraper has finished")


class WikiScraper(object):
    def __init__(self, db):
        self.api_url = 'https://pathofexile.gamepedia.com/api.php'
        self.db = db

    def scrape_items(self):
        result = {
            'itemCategories': {
                'weapons': WEAPON_ITEM_CLASSES,
                'armour': ARMOUR_ITEM_CLASSES,
                'jewelry': JEWELRY_ITEM_CLASSES,
                'gems': GEM_ITEM_CLASSES,
                'flasks': FLASK_ITEM_CLASSES,
                'currency': CURRENCY_ITEM_CLASSES,
                'other': OTHER_ITEM_CLASSES
            },
            'itemClasses': dict()
        }
        for item_class in ALL_ITEM_CLASSES:
            print("Scraping", item_class)
            if item_class in ARMOUR_ITEM_CLASSES:
                result['itemClasses'][item_class] = self.scrape_armour_class(item_class)
            else:
                result['itemClasses'][item_class] = self.scrape_item_class(item_class)

        self.db.game_constants.replace_one({}, {'data': result, 'json': json.dumps(result)}, upsert=True)

    def _cargoquery(self, **kwargs):
        """
        Generic wiki api query. Performs a cargo query with the given parameters.
        Automatically adds the action=cargoquery and format=json that are always needed.
        """
        params = dict(action='cargoquery', format='json', limit=500, **kwargs)
        headers = {'User-agent': 'poe.gg'}
        response = requests.get(self.api_url, params=params, headers=headers)
        if response.status_code != 200:
            print("ERROR: wiki api returned ", response.status_code, response.text)
            raise Exception("API Error")

        try:
            return json.loads(response.text)['cargoquery']
        except:
            print("ERROR")
            print(response.text)
            raise Exception("API Error")

    def scrape_item_class(self, item_class, tables=(), fields=(), join_on=None, where=''):
        tables = ','.join(['items'] + list(tables))
        default_fields = ['name', 'drop_level', 'required_strength', 'required_dexterity', 'required_intelligence']
        fields = ','.join(default_fields + list(fields))
        if len(where) > 0:
            where += ' AND '
        where += 'class="{}" AND drop_enabled AND NOT is_fated AND rarity="Normal"'.format(item_class)

        def generate_results():
            response = self._cargoquery(tables=tables, join_on=join_on, fields=fields, where=where)
            for obj in response:
                item = obj['title']
                yield {
                    'itemclass': item_class,
                    'basetype': item['name'],
                    'droplevel': int_or_0(item['drop level']),
                    'req_str': int_or_0(item['required strength']),
                    'req_dex': int_or_0(item['required dexterity']),
                    'req_int': int_or_0(item['required intelligence']),
                    'armour': int_or_0(item.get('armour', 0)),
                    'evasion': int_or_0(item.get('evasion', 0)),
                    'energy_shield': int_or_0(item.get('energy shield', 0))
                }

        results = list(generate_results())
        results.sort(key=lambda x: x['droplevel'])
        return results

    def scrape_armour_class(self, armour_class):
        return self.scrape_item_class(
            armour_class,
            tables=['armours'],
            join_on='items._pageName = armours._pageName',
            fields=['armour', 'evasion', 'energy_shield'])


def int_or_0(txt):
    try:
        return int(txt)
    except:
        return 0