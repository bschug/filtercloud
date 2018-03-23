from collections import defaultdict
import requests


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
}


def get_unique_tiers(league, thresholds, db):
    """Sort uniques into classes by value (top tier, decent, mediocre, worthless)"""
    unique_prices = get_unique_prices(league, db)
    return sort_into_tiers(unique_prices, thresholds)


def get_unique_prices(league, db):
    return db.prices.find_one({'category': 'uniques', 'league': league})['prices']


def update_unique_prices(league, db):
    print("Updating unique prices for", league)
    prices = scrape_unique_prices(league)
    dbentry = {'category': 'uniques', 'league': league, 'prices': prices}
    db.prices.replace_one({'category': 'uniques', 'league': league}, dbentry, upsert=True)


def scrape_unique_prices(league):
    unique_prices = defaultdict(lambda: 0)
    scrape_unique_prices_from_url('http://poe.ninja/api/Data/GetUniqueWeaponOverview', league, unique_prices)
    scrape_unique_prices_from_url('http://poe.ninja/api/Data/GetUniqueArmourOverview', league, unique_prices)
    scrape_unique_prices_from_url('http://poe.ninja/api/Data/GetUniqueAccessoryOverview', league, unique_prices)
    scrape_unique_prices_from_url('http://poe.ninja/api/Data/GetUniqueFlaskOverview', league, unique_prices)
    return unique_prices


def scrape_unique_prices_from_url(url, league, unique_prices):
    response = requests.get(url, params={'league': league}).json()
    for item in response['lines']:
        # Fated uniques are created by prophecies, not dropped.
        if item['name'] in BLACKLIST:
            continue
        # All six-linkable items have 3 entries: regular, 5link and 6link. We only want regular.
        if item['links'] >= 5:
            continue
        unique_prices[item['baseType']] = max(unique_prices[item['baseType']], item['chaosValue'])


def sort_into_tiers(unique_prices, thresholds):
    return {
        'top_tier': [k for k, v in unique_prices.items() if v >= thresholds.top_tier],
        'valuable': [k for k, v in unique_prices.items() if v >= thresholds.valuable and v < thresholds.top_tier],
        'mediocre': [k for k, v in unique_prices.items() if v > thresholds.worthless and v < thresholds.valuable],
        'worthless': [k for k, v in unique_prices.items() if v > thresholds.hidden and v <= thresholds.worthless],
        'hidden': [k for k, v in unique_prices.items() if v < thresholds.hidden],
    }