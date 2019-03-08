import os

from jinja2 import Environment, FileSystemLoader

from lootfilter.style import ItemStyle, parse_color, parse_sound


def load_template(filename):
    """Load template from file"""
    env = Environment(
        loader=FileSystemLoader(os.path.dirname(filename)),
        autoescape=False,
    )
    env.filters['names'] = format_list_filter
    env.filters['setstyle'] = setstyle_filter
    env.filters['butonly'] = butonly_filter
    env.filters['butnot'] = butnot_filter
    env.filters['any_true'] = any_true_filter
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


def butonly_filter(style, *args, fontsize=False, textcolor=False, background=False, border=False, sound=False, disable_drop_sound=False, map_icon=False, beam=False):
    newstyle = ItemStyle(
        fontsize=style.fontsize if fontsize else None,
        textcolor=style.textcolor if textcolor else None,
        background=style.background if background else None,
        border=style.border if border else None,
        sound=style.sound if sound else None,
        disable_drop_sound=style.disable_drop_sound if disable_drop_sound else None,
        map_icon=style.map_icon if map_icon else None,
        beam=style.beam if beam else None)

    return newstyle


def butnot_filter(style,  *args, fontsize=True, textcolor=True, background=True, border=True, sound=True, disable_drop_sound=True, map_icon=True, beam=True):
    return butonly_filter(style,
                          fontsize=fontsize,
                          textcolor=textcolor,
                          background=background,
                          border=border,
                          sound=sound,
                          disable_drop_sound=disable_drop_sound,
                          map_icon=map_icon,
                          beam=beam)


def any_true_filter(obj):
    return any(obj.values())
