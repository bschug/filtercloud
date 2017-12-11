from datetime import timedelta
import json
import itertools

import mwclient
from box import Box

from functioncache import JsonCache, cached
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
        self.site = mwclient.Site('pathofexile.gamepedia.com', path='/', clients_useragent="poe.gg")
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
            result['itemClasses'][item_class] = dict()
            for basetype in self.scrape_item_class(item_class):
                print("    Scraping", basetype)
                result['itemClasses'][item_class][basetype] = self.scrape_basetype(basetype, item_class)
        self.db.game_constants.replace_one({}, {'data': result, 'json': json.dumps(result)}, upsert=True)

    def scrape_item_class(self, item_class):
        query = '|'.join([
            '[[Has item class::{item_class}]]'.format(item_class=item_class),
            '[[Has rarity::Normal]]',
            '?Has drop level'
        ])

        def generate_results():
            for answer in self.site.ask(query):
                for title, data in answer.items():
                    yield {'name': title, 'level': data['printouts']['Has drop level']}
        results = list(generate_results())
        results.sort(key=lambda x: x['level'])
        return [x['name'] for x in results]

    def scrape_basetype(self, basetype, itemclass):
        response = self.site.api('browsebysubject', subject=basetype)
        return WikiItem(response['query']['data'], itemclass, basetype).to_dict()

    def scrape_itembox_html(self, name):
        response = self.site.get('browsebysubject', subject=name)
        return [x['dataitem'] for x in response['query']['data'] if 'Has_infobox_HTML' in x['property']][0][0]['item']


class WikiItem(object):
    def __init__(self, data, itemclass, basetype):
        self.rawdata = data
        self.itemclass = itemclass
        self.basetype = basetype

    def to_dict(self):
        keys = ['itemclass', 'basetype', 'droplevel', 'armour', 'evasion', 'energy_shield',
                'req_str', 'req_dex', 'req_int']
        return {k: getattr(self, k) for k in keys}

    def get_property(self, name, default=0):
        try:
            dataitem = [x['dataitem'] for x in self.rawdata if x['property'] == name][0]
            return [x['item'] for x in dataitem][0]
        except KeyError:
            return default
        except IndexError:
            return default

    @property
    def droplevel(self):
        return self.get_property('Has_level_requirement_range_average')

    @property
    def req_str(self):
        return self.get_property('Has_strength_requirement_range_average')

    @property
    def req_dex(self):
        return self.get_property('Has_dexterity_requirement_range_average')

    @property
    def req_int(self):
        return self.get_property('Has_intelligence_requirement_range_average')

    @property
    def armour(self):
        return self.get_property('Has_armour_range_average')

    @property
    def evasion(self):
        return self.get_property('Has_evasion_range_average')

    @property
    def energy_shield(self):
        return self.get_property('Has_energy_shield_average')

