import json

from box import Box
from flask import Flask, request, render_template

import lootfilter


app = Flask('api', template_folder='/templates')
app.add_template_filter(lootfilter.templating.format_list_filter, 'names')
app.add_template_filter(lootfilter.templating.setstyle_filter, 'setstyle')


@app.route('/filter/api/build', methods=['POST'])
def build_filter():
    try:
        style = lootfilter.load_style(get_settings('style'))
        config = lootfilter.load_config(get_settings('config'), style)
        return render_template('main.template', **config)
    except Exception as ex:
        app.logger.exception("/filter/api/build failed")
        return str(ex)


def get_settings(key):
    text = request.form[key]
    obj = json.loads(text)
    return Box(obj)