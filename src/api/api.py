import os
import json

from box import Box
from flask import Flask, session, request, g, render_template, send_file
import psycopg2

import lootfilter


app = Flask('api', template_folder='/templates')
app.add_template_filter(lootfilter.templating.format_list_filter, 'names')
app.add_template_filter(lootfilter.templating.setstyle_filter, 'setstyle')


def get_db():
    """Open database connection if it's not already open."""
    if not hasattr(g, 'postgres_db'):
        g.postgres_db = psycopg2.connect(os.environ['FILTERCLOUD_DB'])
    return g.postgres_db


@app.teardown_appcontext
def close_db(error):
    """Close the database at the end of the request."""
    if hasattr(g, 'postgres_db'):
        g.postgres_db.close()


@app.route('/api/filter/ping', methods=['GET'])
def ping():
    return "pong"


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
