import json

from box import Box

import argparse
import lootfilter


def main(args):
    template = lootfilter.load_template(args.template)
    style = lootfilter.load_style(load_settings(args.style))
    config = lootfilter.load_config(load_settings(args.config), style)
    print(lootfilter.render(template, config))


def parse_args(args=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('template', type=str)
    ap.add_argument('config', type=str)
    ap.add_argument('style', type=str)
    return ap.parse_args(args)


def load_settings(filename):
    with open(filename) as fp:
        return Box(json.load(fp))


if __name__ == '__main__':
    main(parse_args())
