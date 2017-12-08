import json

from bson.json_util import dumps

from .constants import *


class WikiCache(object):
    def __init__(self, db):
        self.db = db

    def get_game_constants_json(self):
        """
        Returns the game constants as serialized JSON.
        Must exist in the database already, i.e. you must have run the WikiScraper before.
        """
        return self.db.game_constants.find_one({}, projection={'json': True})['json']

    def get_game_constants(self):
        """Return game constants as json-compatible dict."""
        return self.db.game_constants.find_one({}, projection={'data':True, '_id':False})['data']

    def get_selector(self, name, mask):
        """Return selector for given item category and attributes"""
        return self.db.selectors.find({'name':name, **mask})
