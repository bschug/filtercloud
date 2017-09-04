import os
import sys

from jinja2 import Template, Environment, FileSystemLoader

from lootfilter.style import ItemStyle, parse_color, parse_sound


def load_template(filename):
    """Load template from file"""
    env = Environment(
        loader=FileSystemLoader(os.path.dirname(filename)),
        autoescape=False,
    )
    env.filters['names'] = format_list_filter
    env.filters['setstyle'] = setstyle_filter
    return env.get_template(os.path.basename(filename))


def render(template, config):
    return template.render(config)


def format_list_filter(values, force_quote=True):
    values = [quote(x) if must_quote(x) or force_quote else x for x in values]
    return ' '.join(values)


def quote(value):
    value = value.strip('" ')
    return '"' + value + '"'


def must_quote(value):
    return ' ' in value


def setstyle_filter(style, *args, fontsize=None, textcolor=None, background=None, border=None, sound=None):
    textcolor = parse_color(textcolor)
    background = parse_color(background)
    border = parse_color(border)
    sound = parse_sound(sound)

    newstyle = ItemStyle(fontsize=fontsize, textcolor=textcolor, background=background, border=border, sound=sound)

    for arg in args:
        newstyle.fill_with(arg)

    newstyle.fill_with(style)
    return newstyle


