import json
from datetime import datetime

from box import Box

import pricechecking
from lootfilter.style import StyleCollection, ItemStyle, parse_color, parse_sound


def load_config(settings, style):
    return {
        'date': datetime.now(),
        'include_leveling_rules': bool(settings.include_leveling_rules),
        'include_endgame_rules': bool(settings.include_endgame_rules),
        'crafting': settings.get('crafting'),
        'currency': build_currency_config(settings),
        'rares': settings.get('rares'),
        'maps': settings.get('maps'),
        'uniques': build_unique_config(settings),
        'divcards': build_divcards_config(settings),
        'gems': settings.get('gems'),
        'jewels': settings.get('jewels'),
        'leveling': settings.get('leveling'),
        'style': style,
    }


def load_style(settings):
    return build_styles_config(settings)


def load_settings(filename):
    with open(filename) as fp:
        return json.load(fp)


def build_currency_config(settings):
    league = settings.league
    thresholds = settings.currency.thresholds
    config = pricechecking.get_currency_tiers(league, thresholds)
    apply_overrides(config, settings.currency.overrides)
    return {**settings.currency, **config}


def build_unique_config(settings):
    league = settings.league
    thresholds = settings.uniques.thresholds
    config = pricechecking.get_unique_tiers(league=league, thresholds=thresholds)
    apply_overrides(config, settings.uniques.overrides)
    return config


def build_divcards_config(settings):
    league = settings.league
    thresholds = settings.divcards.thresholds
    config = pricechecking.get_divcard_tiers(league=league, thresholds=thresholds)
    apply_overrides(config, settings.divcards.overrides)
    return config


def apply_overrides(config, overrides):
    for item, category in overrides.items():
        for k in config.keys():
            config[k] = [x for x in config[k] if x != item]
        config[category].append(item)
    return config


def build_styles_config(settings):
    return {
        'ultra_rare': build_style_collection(settings.ultra_rare),
        'strong_highlight': build_style_collection(settings.strong_highlight),
        'highlight': build_style_collection(settings.highlight),
        'normal': build_style_collection(settings.normal),
        'smaller': build_style_collection(settings.smaller),
        'hidden': build_style_collection(settings.hidden),
        'leveling': build_style_collection(settings.leveling),
        'map': build_style_collection(settings.map),
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


def build_style_collection(settings):
    default = build_style(settings.default, ItemStyle())
    styles = dict()
    for name, config in settings.items():
        styles[name] = build_style(config, default)
    return StyleCollection(default, styles)

