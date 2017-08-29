import json
from datetime import datetime

from box import Box

import pricechecking
from lootfilter.style import ItemStyle, parse_color, parse_sound


def load_config(filename):
    settings = load_settings(filename)
    return {
        'date': datetime.now(),
        'include_leveling_rules': bool(settings.include_leveling_rules),
        'include_endgame_rules': bool(settings.include_endgame_rules),
        'currency': settings.get('currency'),
        'rares': settings.get('rares'),
        'uniques': build_unique_config(settings),
        'divcards': build_divcards_config(settings),
        'gems': settings.get('gems'),
        'style': build_styles_config(settings),
    }


def load_settings(filename):
    with open(filename) as fp:
        return Box(json.load(fp))


def build_unique_config(settings):
    league = settings.league
    thresholds = settings.uniques.thresholds
    return pricechecking.get_unique_classes(league=league, thresholds=thresholds)


def build_divcards_config(settings):
    league = settings.league
    thresholds = settings.divcards.thresholds
    config = pricechecking.get_divcard_categories(league=league, thresholds=thresholds)

    # Apply overrides
    for card, category in settings.divcards.overrides.items():
        for k in config.keys():
            config[k] = [x for x in config[k] if x != card]
        config[category].append(card)

    return config


def build_styles_config(settings):
    return {
        'ultra_rare': StyleCollection(settings.style.ultra_rare),
        'strong_highlight': StyleCollection(settings.style.strong_highlight),
        'highlight': StyleCollection(settings.style.highlight),
        'normal': StyleCollection(settings.style.normal),
        'smaller': StyleCollection(settings.style.smaller),
        'hidden': StyleCollection(settings.style.hidden)
    }


def build_style(cfg, default):
    textcolor = parse_color(cfg.get('textcolor'))
    background = parse_color(cfg.get('background'))
    border = parse_color(cfg.get('border'))
    fontsize = cfg.get('fontsize')
    sound = parse_sound(cfg.get('sound'))

    style = ItemStyle(textcolor=textcolor, background=background, border=border, fontsize=fontsize, sound=sound)
    style.fill_with(default)
    return style


class StyleCollection(object):
    def __init__(self, settings):
        self._default = build_style(settings.default, ItemStyle())
        self._styles = dict()
        for name, config in settings.items():
            self._styles[name] = build_style(config, self._default)

    def __getattr__(self, name):
        #styles = super().__getattr__('_styles')
        return self._styles.get(name, self._default)
