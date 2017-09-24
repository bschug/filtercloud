import os
import json

from box import Box
from flask import Flask, session, request, g, render_template, send_file, jsonify, Response
import psycopg2

import lootfilter
from wiki import WikiScraper, constants
import pricechecking


app = Flask('api', template_folder='/templates')
app.add_template_filter(lootfilter.templating.format_list_filter, 'names')
app.add_template_filter(lootfilter.templating.setstyle_filter, 'setstyle')


def get_db():
    """Open database connection if it's not already open."""
    if not hasattr(g, 'postgres_db'):
        g.postgres_db = psycopg2.connect(os.environ['FILTERCLOUD_DB'])
    return g.postgres_db


def get_wiki():
    if not hasattr(g, 'wiki'):
        g.wiki = WikiScraper()
    return g.wiki


@app.teardown_appcontext
def close_db(error):
    """Close the database at the end of the request."""
    if hasattr(g, 'postgres_db'):
        g.postgres_db.close()


@app.route('/api/filter/game-constants', methods=['GET'])
def get_game_constants():
    response = Response(get_wiki().get_game_constants_json())
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/api/filter/prices/<league>', methods=['GET'])
def get_prices(league):
    return jsonify({
        'currency': pricechecking.get_currency_prices(league),
        'divcards': pricechecking.get_divcard_prices(league),
        'uniques': pricechecking.get_unique_prices(league)
    })


@app.route('/api/filter/itembox/<item>', methods=['GET'])
def get_itembox(item):
    if item not in get_wiki().get_game_constants():
        raise ApiException('Item not found', status_code=404, data=item)
    response = Response(get_wiki().get_itembox_html(item))
    response.headers['Content-Type'] = 'text/html'
    return response


@app.route('/api/filter/build', methods=['POST'])
def build():
    try:
        style = lootfilter.load_style(settings_from_post('style'))
        config = lootfilter.load_config(settings_from_post('config'), style)
        return render_template('main.template', **config)
    except Exception as ex:
        app.logger.exception("/filter/api/build failed")
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


