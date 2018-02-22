import os
import json
import logging

from concurrent.futures import ThreadPoolExecutor

from box import Box
from flask import Flask, session, request, g, render_template, send_file, jsonify, Response
from pymongo import MongoClient
import bson

import lootfilter
from wiki import WikiCache, scrape_wiki, update_selectors
import pricechecking


def get_db():
    """Open database connection if it's not already open."""
    if not hasattr(g, 'mongo_db'):
        g.mongo_db = MongoClient('db')
    return g.mongo_db.filterforge


def get_selector(name, mask):
    wiki = WikiCache(get_db())
    return wiki.get_selector(name, mask)


logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

app = Flask('api', template_folder='/templates')
app.add_template_filter(lootfilter.templating.format_list_filter, 'names')
app.add_template_filter(lootfilter.templating.setstyle_filter, 'setstyle')
app.add_template_filter(lootfilter.templating.any_true_filter, 'any_true')
app.add_template_global(get_selector, 'selector')

executor = ThreadPoolExecutor(2)


@app.teardown_appcontext
def close_db(error):
    """Close the database at the end of the request."""
    if hasattr(g, 'mongo_db'):
        g.mongo_db.close()


@app.route('/api/filter/helloworld', methods=['GET'])
def get_helloworld():
    return "Hello yourself!"


@app.route('/api/scraper/scrape-wiki', methods=['POST'])
def post_scrape_wiki():
    executor.submit(scrape_wiki, get_db())
    return "Wiki Scraper started"


@app.route('/api/scraper/update-prices', methods=['POST'])
def post_update_prices():
    for league in ['Abyss', 'Hardcore Abyss', 'Standard', 'Hardcore']:
        pricechecking.update_currency_prices(league, get_db())
        pricechecking.update_divcard_prices(league, get_db())
        pricechecking.update_unique_prices(league, get_db())
    return "Update Complete"


# Selectors are rebuilt automatically after each wiki update.
# You shouldn't ever need to call this manually unless you change the selector generator code.
@app.route('/api/scraper/update-selectors', methods=['POST'])
def post_update_selectors():
    executor.submit(update_selectors, get_db())
    return "Selector update started"


@app.route('/api/filter/leagues', methods=['GET'])
def get_leagues():
    return jsonify(['Standard', 'Hardcore', 'Abyss', 'Hardcore Abyss'])


@app.route('/api/filter/game-constants', methods=['GET'])
def get_game_constants():
    response = Response(WikiCache(get_db()).get_game_constants_json())
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/api/filter/prices/<league>', methods=['GET'])
def get_prices(league):
    return jsonify({
        'currency': pricechecking.get_currency_prices(league, get_db()),
        'divcards': pricechecking.get_divcard_prices(league, get_db()),
        'uniques': pricechecking.get_unique_prices(league, get_db())
    })


@app.route('/api/filter/build', methods=['POST'])
def build():
    try:
        print("START BUILDING FILTER")
        style = lootfilter.load_style(settings_from_post('style'))
        config = lootfilter.load_config(settings_from_post('config'), style, get_db())
        filtercode = render_template('main.template', **config)
        print("DONE BUILDING FILTER")
        response = Response(filtercode)
        response.headers['Content-Disposition'] = 'attachment;filename=gg.filter'
        response.headers['Content-Type'] = 'text/plain'
        return response

    except Exception as ex:
        app.logger.exception("/filter/api/build failed -- payload was: " + json.dumps(request.form))
        return str(ex)


@app.route('/api/filter/style/<id>', methods=['GET'])
def style_instance(id):
    if id == 'default':
        filename = os.path.join(app.template_folder, 'style.json')
        return send_file(filename)
    raise ApiException("style not found: '{}'".format(id), status_code=404, data=id)


@app.route('/api/filter/config/<id>', methods=['GET'])
def config_instance(id):
    if id == 'default':
        filename = os.path.join(app.template_folder, 'config.json')
        return send_file(filename)
    raise ApiException("config not found: '{}'".format(id), status_code=404, data=id)


def settings_from_post(key):
    text = request.form[key]
    obj = json.loads(text)
    return Box(obj)


class ApiException(Exception):
    def __init__(self, message, status_code=400, data=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.data = data

    def to_dict(self):
        rv = dict()
        rv['data'] = self.data
        rv['message'] = self.message
        return rv


@app.errorhandler(ApiException)
def handle_api_error(ex):
    response = jsonify(ex.to_dict())
    response.status_code = ex.status_code
    return response

