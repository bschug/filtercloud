import json
from datetime import datetime

import logging
logger = logging.getLogger("filtercloud.lootfilter")

import pricechecking
from lootfilter.style import StyleCollection, ItemStyle, parse_color, parse_sound, parse_map_icon, parse_beam


def load_config(settings, style, league_uniques, db):
    settings = upgrade_config(settings)
    return {
        'date': datetime.now(),
        'misc': settings.get('misc'),
        'crafting': settings.get('crafting'),
        'currency': build_currency_config(settings, db),
        'rares': settings.get('rares'),
        'maps': settings.get('maps'),
        'uniques': build_unique_config(settings, league_uniques, db),
        'divcards': build_divcards_config(settings, db),
        'prophecies': build_prophecies_config(settings, db),
        'gems': settings.get('gems'),
        'jewels': settings.get('jewels'),
        'flasks': settings.get('flasks'),
        'leveling': settings.get('leveling'),
        'style': style,
        'meta': settings.get('meta'),
        'build': settings.get('build'),
        'fossils': build_fossils_config(settings, db),
        'resonators': build_resonators_config(settings, db),
        'explicit_mods': settings.get('explicit_mods'),
        'sockets': settings.get('sockets')
    }


def load_style(settings):
    settings = upgrade_style(settings)
    return build_styles_config(settings)


def build_currency_config(settings, db):
    league = settings.league
    thresholds = settings.currency.thresholds
    config = pricechecking.get_currency_tiers(league=league, thresholds=thresholds, db=db)
    apply_overrides(config, settings.currency.overrides)
    return {**settings.currency, **config}


def build_unique_config(settings, league_uniques, db):
    league = settings.league
    thresholds = settings.uniques.thresholds
    whitelisted_leagues = settings.uniques.leagues
    blacklist = pricechecking.build_blacklist(league_uniques, whitelisted_leagues)
    config = pricechecking.get_unique_tiers(
        league=league, thresholds=thresholds, blacklist=blacklist, db=db)
    apply_overrides(config, settings.uniques.overrides)
    return config


def build_divcards_config(settings, db):
    league = settings.league
    thresholds = settings.divcards.thresholds
    config = pricechecking.get_divcard_tiers(league=league, thresholds=thresholds, db=db)
    apply_overrides(config, settings.divcards.overrides)
    return config


def build_prophecies_config(settings, db):
    league = settings.league
    thresholds = settings.prophecies.thresholds
    config = pricechecking.get_prophecy_tiers(league=league, thresholds=thresholds, db=db)
    apply_overrides(config, settings.prophecies.overrides)
    return config


def build_fossils_config(settings, db):
    league = settings.league
    thresholds = settings.fossils.thresholds
    config = pricechecking.get_fossil_tiers(league=league, thresholds=thresholds, db=db)
    apply_overrides(config, settings.fossils.overrides)
    return config


def build_resonators_config(settings, db):
    league = settings.league
    thresholds = settings.resonators.thresholds
    config = pricechecking.get_resonator_tiers(league=league, thresholds=thresholds, db=db)
    apply_overrides(config, settings.resonators.overrides)
    return config


def apply_overrides(config, overrides):
    for category, items in overrides.items():
        # Remove override items from all other categories
        for k in config.keys():
            config[k] = [x for x in config[k] if x not in items]
        config[category].extend(items)
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
        'quest': build_style_collection(settings.quest),
        'animate_weapon': build_style_collection(settings.animate_weapon),
        'veiled': build_style_collection(settings.veiled)
    }


def build_style(cfg, default):
    textcolor = parse_color(cfg.get('textcolor'))
    background = parse_color(cfg.get('background'))
    border = parse_color(cfg.get('border'))
    fontsize = cfg.get('fontsize')
    sound = parse_sound(cfg.get('sound'))
    disable_drop_sound = cfg.get('disable_drop_sound')
    map_icon = parse_map_icon(cfg.get('map_icon'))
    beam = parse_beam(cfg.get('beam'))

    style = ItemStyle(
        textcolor=textcolor,
        background=background,
        border=border,
        fontsize=fontsize,
        sound=sound,
        disable_drop_sound=disable_drop_sound,
        map_icon=map_icon,
        beam=beam)
    style.fill_with(default)
    return style


def build_style_collection(settings):
    default = build_style(settings.default, ItemStyle())
    styles = dict()
    for name, config in settings.items():
        styles[name] = build_style(config, default)
    return StyleCollection(default, styles)


def upgrade_config(settings):
    """
    If config settings are older, upgrade them to the latest version.
    If config settings are multiple versions behind, applies all conversion operations in order between the given one
    and the latest.
    """
    if settings.version < 2:
        for k, v in settings.get('crafting', {}).items():
            v['ilvl'] = int(v.get('ilvl', 0))
            v['links'] = int(v.get('links', 0))

    default_thresholds = {
        'thresholds': {'hidden': 0, 'worthless': 0.2, 'valuable': 1, 'top_tier': 20},
        'overrides': {'hidden': [], 'worthless': [], 'valuable': [], 'top_tier': []}
    }

    settings.rares['breach_ring_explicit'] = settings.rares.get('breach_ring_explicit', [])
    settings.build['animate_weapon'] = settings.build.get('animate_weapon', False)
    settings['fossils'] = settings.get('fossils', default_thresholds)
    settings['resonators'] = settings.get('resonators', default_thresholds)
    settings['build']['socket_count'] = settings.build.get('socket_count', {'itemtype':'none', 'offset': 5})
    settings['maps']['hide_offset'] = settings.maps.get('hide_offset', 10)
    settings['sockets'] = settings.get('sockets', {'sixlink':{'show':True,'style':'strong'},'fivelink':{'show':False,'style':'normal'},'sixsocket':{'show':True,'style':'normal'}})

    if settings.version != 2:
        logger.debug("Upgraded config settings from {} to 2".format(settings.version))
        settings.version = 2
    return settings


def upgrade_style(settings):
    """
    If style settings are older, upgrade them to the latest version.
    If style settings are multiple versions behind, applies all conversion operations in order between the given one
    and the latest.
    """
    settings.hidden.default['disable_drop_sound'] = settings.hidden.default.get('disable_drop_sound', True)
    settings['quest'] = settings.get('quest', {'default': {
        "fontsize": "48",
        "textcolor": "74 230 58",
        "border": "74 230 58",
        "background": "255 255 255",
        "sound": "1 300"
    }})
    settings['animate_weapon'] = settings.get('animate_weapon', {'default': {
        'border': '180 60 60'
    }})
    settings['veiled'] = settings.get('veiled', settings['highlight'])

    if settings.version != 3:
        logger.debug("Upgraded style settings from {} to 3".format(settings.version))
        settings.version = 3
    return settings
