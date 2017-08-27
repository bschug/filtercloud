import os
import sys

from jinja2 import Template, Environment, FileSystemLoader


def load_template(filename):
    """Load template from file"""
    env = Environment(
        loader=FileSystemLoader(os.path.dirname(filename)),
        autoescape=False,
    )
    env.filters['names'] = format_list_filter
    print("Looking for {} in {}".format(os.path.basename(filename), os.path.dirname(filename)), file=sys.stderr)
    return env.get_template(os.path.basename(filename))


def render(template, config):
    from datetime import datetime
    return template.render(date=datetime.now())


def format_list_filter(values, force_quote=True):
    values = [quote(x) if must_quote(x) or force_quote else x for x in values]
    return ' '.join(values)


def quote(value):
    value = value.strip('" ')
    return '"' + value + '"'


def must_quote(value):
    return ' ' in value
