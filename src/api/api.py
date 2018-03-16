import os
import json
import logging

from concurrent.futures import ThreadPoolExecutor

from box import Box
from flask import Flask, session, request, g, render_template, send_file, jsonify, Response
import pymongo
import pymongo.errors

import lootfilter
from wiki import WikiCache, scrape_wiki, update_selectors
import pricechecking
import users


def get_db():
    """Open database connection if it's not already open."""
    if not hasattr(g, 'mongo_db'):
        g.mongo_db = pymongo.MongoClient('db')
    return g.mongo_db.filterforge


def get_selector(name, mask):
    wiki = WikiCache(get_db())
    return wiki.get_selector(name, mask)


logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

app = Flask('api', template_folder='/templates')
app.add_template_filter(lootfilter.templating.format_list_filter, 'names')
app.add_template_filter(lootfilter.templating.setstyle_filter, 'setstyle')
app.add_template_filter(lootfilter.templating.any_true_filter, 'any_true')
app.add_template_global(get_selector, 'selector')

app.config.update(
    SESSION_COOKIE_PATH='/',
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
)

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
    for league in ['Bestiary', 'Hardcore Bestiary', 'Standard', 'Hardcore']:
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
    return jsonify(['Standard', 'Hardcore', 'Bestiary', 'Hardcore Bestiary'])


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
        raise ApiException("Building Filter Failed", status_code=500, data=str(ex))


@app.route('/api/filter/style/', defaults={'username': None, 'stylename': None}, methods=['GET'])
@app.route('/api/filter/style/<username>/<stylename>', methods=['GET'])
def download_style(username, stylename):
    if username is None:
        filename = os.path.join(app.template_folder, 'style.json')
        return send_file(filename)
    style = users.load_style(username, stylename, get_db())
    if style is None:
        raise ApiException("style not found: '{}'".format(id), status_code=404, data=id)
    return jsonify(style)


@app.route('/api/filter/config/', defaults={'username': None, 'configname': None}, methods=['GET'])
@app.route('/api/filter/config/<username>/<configname>', methods=['GET'])
def config_instance(username, configname):
    if username is None:
        filename = os.path.join(app.template_folder, 'config.json')
        return send_file(filename)
    config = users.load_config(username, configname, get_db())
    if config is None:
        raise ApiException("config not found: '{}'".format(id), status_code=404, data=id)
    return jsonify(config)


@app.route('/api/filter/style/<username>/<stylename>', methods=['POST'])
def upload_style(username, stylename):
    user = load_user(request.form['token'])
    if user.name != username:
        raise ApiException("You don't own that style", status_code=403)

    style = json.loads(request.form['data'])
    users.store_style(user.name, stylename, style, get_db())
    return jsonify(load_user(request.form['token']).styles)


@app.route('/api/filter/config/<username>/<configname>', methods=['POST'])
def upload_config(username, configname):
    user = load_user(request.form['token'])
    if user.name != username:
        raise ApiException("You don't own that config", status_code=403)

    config = json.loads(request.form['data'])
    users.store_config(user.name, configname, config, get_db())
    return jsonify(load_user(request.form['token']).configs)


@app.route('/api/filter/user/', methods=['POST'])
def login_or_register():
    """
    Login or register the user.
    When called with a valid token for a registered user, login that user.
    Otherwise you need to also provide a valid, unused name.
    :return: User object
    """
    try:
        token = request.json['token']
        name = request.json.get('name')
        user = load_user(token)

        # Try to register the user with the given name if it's not already registered
        # This will raise an exception if it fails for any reason.
        if not user.is_active:
            user = users.create(token, name, get_db())

        return jsonify(user.to_dict())

    except users.AuthenticationError as ex:
        raise ApiException('Registration failed: Authentication error', status_code=401, data={'reason': ex.reason})

    except pymongo.errors.DuplicateKeyError as ex:
        raise ApiException('Name is already taken', status_code=409)

    except Exception as ex:
        logger.error(ex)
        raise ApiException('Internal Server Error', status_code=500)


def load_user(token):
    return users.load(token, get_db())


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
    logger.exception(ex)
    return response

