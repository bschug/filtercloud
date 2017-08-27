import json
from datetime import datetime

from box import Box

import pricechecking


def load_config(filename):
    settings = load_settings(filename)
    return {
        'date': datetime.now(),
        'uniques': build_unique_config(settings)
    }


def load_settings(filename):
    with open(filename) as fp:
        return Box(json.load(fp))


def build_unique_config(settings):
    league = settings.league
    thresholds = settings.uniques.thresholds
    return pricechecking.get_unique_classes(league=league, thresholds=thresholds)
