import argparse
import lootfilter


def main(args):
    template = lootfilter.load_template(args.template)
    config = lootfilter.load_config(args.config)
    print(lootfilter.render(template, config))


def parse_args(args=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('template', type=str)
    ap.add_argument('config', type=str)
    return ap.parse_args(args)


if __name__ == '__main__':
    main(parse_args())
