from collections import defaultdict
from datetime import datetime
import requests

from .utils import build_date_string
from . import SEND_DATE_TO_POE_NINJA


# Some Uniques can only be acquired from prophecies / breachstones, not dropped by enemies.
# We should not take those into account for highlighting purposes.
BLACKLIST = {
    # FATED UNIQUES
    # These can only be obtained by carrying their un-fated version in your inventory while completing the respective
    # prophecy.
    "Amplification Rod",
    "Asenath's Chant",
    "Atziri's Reflection",
    "Cameria's Avarice",
    "Cragfall",
    "Crystal Vault",
    "Death's Opus",
    "Deidbellow",
    "Doedre's Malevolence",
    "Doomfletch's Prism",
    "Dreadbeak",
    "Dreadsurge",
    "Duskblight",
    "Ezomyte Hold",
    "Fox's Fortune",
    "Frostferno",
    "Geofri's Devotion",
    "Greedtrap",
    "Hrimburn",
    "Hrimnor's Dirge",
    "Hyrri's Demise",
    "Kaltensoul",
    "Kaom's Way",
    "Karui Charge",
    "Malachai's Awakening",
    "Martyr's Crown",
    "Ngamahu Tiki",
    "Panquetzaliztli",
    "Queen's Escape",
    "Realm Ender",
    "Sanguine Gambol",
    "Shavronne's Gambit",
    "Silverbough",
    "The Cauteriser",
    "The Dancing Duo",
    "The Effigon",
    "The Gryphon",
    "The Nomad",
    "The Oak",
    "The Signal Fire",
    "The Stormwall",
    "The Tactician",
    "The Tempest",
    "Thirst for Horrors",
    "Timetwist",
    "Voidheart",
    "Wall of Brambles",
    "Wildwrap",
    "Windshriek",
    "Winterweave",

    # BREACH UNIQUES
    # These can only be obtained by applying a Breachlord's Blessing on their respective un-upgraded counterpart.
    "Choir of the Storm",
    "Esh's Visage",
    "Hand of Wisdom and Action",
    "Presence of Chayula",
    "Skin of the Lords",
    "The Blue Nightmare",
    "The Formless Inferno",
    "The Green Nightmare",
    "The Pandemonius",
    "The Perfect Form",
    "The Red Nightmare",
    "The Red Trail",
    "The Surrender",
    "Tulfall",
    "United in Dream",
    "Uul-Netol's Embrace",
    "Xoph's Blood",
    "Xoph's Nurture",

    # VENDOR RECIPE UNIQUES
    # These can only be obtained by handing in a certain combination of items to a vendor.
    "Arborix",
    "Duskdawn",
    "Kingmaker",
    "Magna Eclipsis",
    "Star of Wraeclast",
    "The Anima Stone",
    "The Goddess Scorned",
    "The Goddess Unleashed",
    "The Retch",
    "The Taming",
    "The Vinktar Square",

    # INCURSION UPGRADES
    # These can only be obtained by upgrading an item on the Altar of Sacrifice
    "Apep's Supremacy",
    "Coward's Legacy",
    "Fate of the Vaal",
    "Mask of the Stitched Demon",
    "Omeyocan",
    "Shadowstitch",
    "Slavedriver's Hand",
    "Soul Ripper",
    "Transcendent Flesh",
    "Transcendent Mind",
    "Transcendent Spirit",
    "Zerphi's Heart",

    # Perandus Manor is only obtainable from Cadiro
    "The Perandus Manor",
}



def get_unique_tiers(league, thresholds, blacklist, db):
    """Sort uniques into classes by value (top tier, decent, mediocre, worthless)"""
    basetype_prices = get_basetype_prices(league, blacklist, db)
    return sort_into_tiers(basetype_prices, thresholds)


def get_unique_prices(league, db):
    return db.prices.find_one({'category': 'uniques', 'league': league})['prices']


def get_basetype_prices(league, blacklist, db):
    unique_prices = get_unique_prices(league, db)
    return get_price_per_basetype(unique_prices, blacklist)


def update_unique_prices(league, db):
    print("Updating unique prices for", league)
    prices = scrape_unique_prices(league)
    dbentry = {'category': 'uniques', 'league': league, 'prices': prices, 'date': datetime.now()}
    db.prices.replace_one({'category': 'uniques', 'league': league}, dbentry, upsert=True)


def scrape_unique_prices(league):
    unique_prices = []
    scrape_unique_prices_from_url('http://poe.ninja/api/Data/itemoverview', 'UniqueWeapon', league, unique_prices)
    scrape_unique_prices_from_url('http://poe.ninja/api/Data/itemoverview', 'UniqueArmour', league, unique_prices)
    scrape_unique_prices_from_url('http://poe.ninja/api/Data/itemoverview', 'UniqueAccessory', league, unique_prices)
    scrape_unique_prices_from_url('http://poe.ninja/api/Data/itemoverview', 'UniqueFlask', league, unique_prices)
    scrape_unique_prices_from_url('http://poe.ninja/api/Data/itemoverview', 'UniqueJewel', league, unique_prices)
    return unique_prices


def scrape_unique_prices_from_url(url, itype, league, unique_prices):
    date = build_date_string()
    params = {'type': itype, 'league': league}
    if SEND_DATE_TO_POE_NINJA:
        params['date'] = build_date_string()
    response = requests.get(url, params=params).json()
    for item in response['lines']:
        # poe.ninja also contains prices for 5/6-linked versions of the items
        # We only care about the base price without links
        if item['links'] >= 5:
            continue

        # We also don't care about shiny legacy items
        if item['itemClass'] == 9:
            continue

        unique_prices.append({
            'name': item['name'],
            'baseType': item['baseType'],
            'chaosValue': item['chaosValue']
        })


def get_price_per_basetype(unique_prices, blacklist):
    basetype_prices = defaultdict(lambda: 0)
    for item in unique_prices:
        # Don't let blacklisted uniques affect the price
        if item['name'] in blacklist:
            continue
        basetype_prices[item['baseType']] = max(basetype_prices[item['baseType']], item['chaosValue'])
    return basetype_prices


def build_blacklist(league_uniques, whitelisted_leagues):
    """
    Build a blacklist by combining the global blacklist with all league-specific items,
    except those that can drop in leagues that are whitelisted.

    :param league_uniques: Dict of league name -> Set of unique names
    :param whitelisted_leagues: List of leagues whose uniques should not be blacklisted
    """
    # Start with all league-specific uniques in the blacklist
    blacklist = set().union(*league_uniques.values())

    # Then remove those items from the blacklist that can drop in whitelisted leagues
    # (need to do it in this order because some items appear in more than one league)
    for league in whitelisted_leagues:
        blacklist -= league_uniques[league]

    return blacklist


def sort_into_tiers(basetype_prices, thresholds):
    return {
        'top_tier': [k for k, v in basetype_prices.items() if v >= thresholds.top_tier],
        'valuable': [k for k, v in basetype_prices.items() if v >= thresholds.valuable and v < thresholds.top_tier],
        'mediocre': [k for k, v in basetype_prices.items() if v > thresholds.worthless and v < thresholds.valuable],
        'worthless': [k for k, v in basetype_prices.items() if v > thresholds.hidden and v <= thresholds.worthless],
        'hidden': [k for k, v in basetype_prices.items() if v < thresholds.hidden],
    }