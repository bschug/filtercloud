

WEAPON_ITEM_CLASSES = [
    "Claws", "Daggers", "Rune Daggers", "Wands", "One Hand Swords", "Thrusting One Hand Swords", "One Hand Axes", "One Hand Maces",
    "Bows", "Staves", "Warstaves", "Two Hand Swords", "Two Hand Axes", "Two Hand Maces", "Sceptres",
]
ARMOUR_ITEM_CLASSES = [
    "Gloves", "Boots", "Body Armours", "Helmets", "Shields",
]
JEWELRY_ITEM_CLASSES = [
    "Amulets", "Rings", "Quivers", "Belts",
]
GEM_ITEM_CLASSES = [
    "Active Skill Gems", "Support Skill Gems"
]
FLASK_ITEM_CLASSES = [
    "Life Flasks", "Mana Flasks", "Hybrid Flasks", "Utility Flasks", "Critical Utility Flasks",
]
CURRENCY_ITEM_CLASSES = [
    "Currency", "Stackable Currency",
]
OTHER_ITEM_CLASSES = [
    "Quest Items", "Maps", "Fishing Rods", "Map Fragments", "Jewel", "Abyss Jewel",
    "Divination Card", "Labyrinth Item", "Labyrinth Trinket", "Labyrinth Map Item", "Misc Map Items", "Leaguestones",
    "Pantheon Soul", "Piece"
]
ALL_ITEM_CLASSES = WEAPON_ITEM_CLASSES + ARMOUR_ITEM_CLASSES + JEWELRY_ITEM_CLASSES + GEM_ITEM_CLASSES + \
                   FLASK_ITEM_CLASSES + CURRENCY_ITEM_CLASSES + OTHER_ITEM_CLASSES

ALL_LEAGUES = [
    "Ambush",
    "Anarchy",
    "Beyond",
    "Bloodlines",
    "Breach",
    "Domination",
    "Incursion",
    "Invasion",
    "Nemesis",
    "Onslaught",
    "Perandus",
    "Rampage",
    "Talisman",
    "Tempest",
    "Torment",
    "Warbands"
]


LEAGUE_UNIQUES = {
    'Ambush': {"Vaal Caress", "Voideye"},
    'Anarchy': {"Daresso's Salute", "Gifts from Above", "Shavronne's Revelation", "Voll's Devotion"},
    'Beyond': {"Edge of Madness", "The Dark Seer", "The Harvest"},
    'Bloodlines': {"Ngamahu's Sign", "Tasalio's Sign", "Valako's Sign"},
    'Breach': {"Esh's Mirror", "Hand of Thought and Motion", "Severed in Sleep", "Skin of the Loyal", "The Anticipation",
               "The Blue Dream", "The Formless Flame", "The Green Dream", "The Halcyon", "The Infinite Pursuit",
               "The Red Dream", "The Snowblind Grace", "Tulborn", "Uul-Netol's Kiss", "Voice of the Storm",
               "Xoph's Inception", "Xoph's Heart"},
    'Domination': {"Berek's Grip", "Berek's Pass", "Berek's Respite", "Blood of the Karui", "Lavianga's Spirit",
                   "The Gull", },
    'Invasion': {"Vaal Caress", "Voideye"},
    'Incursion': {"Apep's Slumber", "Architect's Hand", "Coward's Chains", "Dance of the Offered",
                  "Mask of the Spirit Drinker", "Sacrificial Heart", "Soul Catcher", "Story of the Vaal",
                  "String of Servitude", "Tempered Flesh", "Tempered Mind", "Tempered Spirit"},
    'Nemesis': {"Berek's Grip", "Berek's Pass", "Berek's Respite", "Blood of the Karui", "Headhunter",
                "Lavianga's Spirit"},
    'Onslaught': {"Death Rush", "Shavronne's Revelation", "Victario's Acuity", "Voll's Devotion"},
    'Perandus': {"Seven-League Step", "Trypanon", "Umbilicus Immortalis", "Varunastra", "Zerphi's Last Breath"},
    'Rampage': {"Null and Void", "Shadows and Dust"},
    'Talisman': {"Blightwell", "Eyes of the Greatwolf", "Faminebind", "Feastbind", "Rigwald's Command",
                 "Rigwald's Crest", "Rigwald's Curse", "Rigwald's Quills", "Rigwald's Savagery"},
    'Tempest': {"Crown of the Pale King", "Jorrhast's Blacksteel", "Trolltimber Spire", "Ylfeban's Trickery"},
    'Torment': {"Brutus' Lead Sprinkler", "Scold's Bridle", "The Rat Cage"},
    'Warbands': {"Brinerot Flag", "Brinerot Mark", "Brinerot Whalers", "Broken Faith", "Mutewind Pennant",
                 "Mutewind Seal", "Mutewind Whispersteps", "Redblade Band", "Redblade Banner", "Redblade Tramplers",
                 "Steppan Eard", "The Pariah"},
}