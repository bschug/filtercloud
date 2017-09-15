from datetime import timedelta
import json

import mwclient
from box import Box

from functioncache import JsonCache, cached
from .constants import *

# Load cache for wiki requests
WikiCache = JsonCache('wiki', timeout=timedelta(days=3))


class WikiScraper(object):
    def __init__(self):
        self.site = mwclient.Site('pathofexile.gamepedia.com', path='/', clients_useragent="poe.gg")

    def get_game_constants_json(self):
        return WikiCache.get_json_with_key('game_constants', self.get_game_constants)

    def get_game_constants(self):
        """Return game constants as json-compatible dict."""
        result = Box({
            'itemCategories': {
                'weapons': WEAPON_ITEM_CLASSES,
                'armour': ARMOUR_ITEM_CLASSES,
                'jewelry': JEWELRY_ITEM_CLASSES,
                'gems': GEM_ITEM_CLASSES,
                'flasks': FLASK_ITEM_CLASSES,
                'other': OTHER_ITEM_CLASSES
            },
            'itemClasses': dict()
        })
        for item_class in ALL_ITEM_CLASSES:
            result['itemClasses'][item_class] = self.scrape_item_class(item_class)
        return result

    def get_item_class_json(self, item_class):
        """Returns a json-serialized list of item names. Read from cache if available."""
        return WikiCache.get_json_with_key("item_class " + item_class, self.scrape_item_class, item_class)

    def get_item_class(self, item_class):
        return WikiCache.get_with_key("item_class " + item_class, self.scrape_item_class, item_class)

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

    def get_itembox_html(self, name):
        return WikiCache.get_with_key("itembox " + name, self.scrape_itembox_html, name)

    def scrape_itembox_html(self, name):
        response = self.site.get('browsebysubject', subject=name)
        return [x['dataitem'] for x in response['query']['data'] if 'Has_infobox_HTML' in x['property']][0][0]['item']
