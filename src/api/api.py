import os
import json

from concurrent.futures import ThreadPoolExecutor

from box import Box
from flask import Flask, session, request, g, render_template, send_file, jsonify, Response
from pymongo import MongoClient

import lootfilter
from wiki import WikiCache, scrape_wiki
import pricechecking


app = Flask('api', template_folder='/templates')
app.add_template_filter(lootfilter.templating.format_list_filter, 'names')
app.add_template_filter(lootfilter.templating.setstyle_filter, 'setstyle')


executor = ThreadPoolExecutor(2)


def get_db():
    """Open database connection if it's not already open."""
    if not hasattr(g, 'mongo_db'):
        g.mongo_db = MongoClient('db')
    return g.mongo_db.filterforge


@app.teardown_appcontext
def close_db(error):
    """Close the database at the end of the request."""
    if hasattr(g, 'postgres_db'):
        g.postgres_db.close()


@app.route('/api/filter/helloworld', methods=['GET'])
def get_helloworld():
    return "Hello yourself!"


@app.route('/api/scraper/scrape-wiki', methods=['POST'])
def post_scrape_wiki():
    executor.submit(scrape_wiki, get_db())
    return "Wiki Scraper started"


@app.route('/api/filter/game-constants', methods=['GET'])
def get_game_constants():
    response = Response(WikiCache(get_db()).get_game_constants_json())
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/api/filter/prices/<league>', methods=['GET'])
def get_prices(league):
    return jsonify({
        'currency': pricechecking.get_currency_prices(league),
        'divcards': pricechecking.get_divcard_prices(league),
        'uniques': pricechecking.get_unique_prices(league)
    })


@app.route('/api/filter/build', methods=['POST'])
def build():
    try:
        style = lootfilter.load_style(settings_from_post('style'))
        config = lootfilter.load_config(settings_from_post('config'), style)
        filtercode = render_template('main.template', **config)
        response = Response(filtercode)
        response.headers['Content-Disposition'] = 'attachment;filename=gg.filter'
        response.headers['Content-Type'] = 'text/plain'
        return response

    except Exception as ex:
        app.logger.exception("/filter/api/build failed -- payload was: " + json.dumps(request.form))
        return str(ex)


@app.route('/api/filter/style/<id>', methods=['GET'])
def style_instance(id):
    filename = os.path.join(app.template_folder, 'style.json')
    app.logger.info('Trying to return file %s' % filename)
    return send_file(filename)


@app.route('/api/filter/config/<id>', methods=['GET'])
def config_instance(id):
    if id == 'endgame' or id == 'leveling':
        filename = os.path.join(app.template_folder, id + '.json')
        return send_file(filename)


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

