import itertools
import logging
from collections import Counter

from .cache import WikiCache

logger = logging.getLogger("wiki.selector")


def update_selectors(db):
    wiki = WikiCache(db)
    itemdata = wiki.get_game_constants()['itemClasses']
    update_selectors_for('body', itemdata['Body Armours'], db)
    update_selectors_for('gloves', itemdata['Gloves'], db)
    update_selectors_for('helmet', itemdata['Helmets'], db)
    update_selectors_for('boots', itemdata['Boots'], db)
    update_selectors_for('shields', itemdata['Shields'], db)
    update_selectors_for('other_armour', dict(**itemdata['Gloves'], **itemdata['Helmets'], **itemdata['Boots']), db)
    logger.info("Selectors updated")


def update_selectors_for(name, items, db):
    logger.info("Updating selectors for {}x {}".format(len(items), name))
    for s, d, i, sd, si, di in itertools.product((True, False), repeat=6):
        logger.info("    {} {}".format(name, (s, d, i, sd, si, di)))
        selector = build_selector_for(items, (s, d, i, sd, si, di))
        db.selectors.replace_one(
            {'name': name, 'str': s, 'dex': d, 'int': i, 'strdex': sd, 'strint': si, 'dexint': di},
            {'name': name, 'str': s, 'dex': d, 'int': i, 'strdex': sd, 'strint': si, 'dexint': di, 'selector': selector},
            upsert=True
        )


def build_selector_for(items, mask):
    in_set = [x for x, y in items.items() if item_matches_attribute_mask(y, mask)]
    out_set = [x for x, y in items.items() if not item_matches_attribute_mask(y, mask)]
    selector = build_selector(in_set, out_set)
    validate_selector(selector, in_set, out_set)
    return selector


def item_matches_attribute_mask(item, mask):
    purestr, puredex, pureint, strdex, strint, dexint = mask
    s = int(item['req_str']) > 0
    d = int(item['req_dex']) > 0
    i = int(item['req_int']) > 0
    return (purestr and (s and not d and not i)) \
        or (puredex and (d and not s and not i)) \
        or (pureint and (i and not s and not d)) \
        or (strdex and (s and d and not i)) \
        or (strint and (s and i and not d)) \
        or (dexint and (d and i and not s))


def validate_selector(selector, in_set, out_set):
    for w in in_set:
        for sel in selector:
            assert any(x in w for x in sel), "VALIDATION FAILED"
    for w in out_set:
        excluded = False
        for sel in selector:
            excluded = excluded or not any(x in w for x in sel)
        assert excluded, "VALIDATION FAILED"
    logger.info("Validation OK")


def build_selector(in_set, out_set):
    """
    Find a list of sets of substrings of the strings in in_set, such that each string from in_set matches at least one
    substring from each set, and each string from out_set has at least one set in which it matches not a single entry.
    """
    in_substr = list_substrings(in_set)
    out_remaining = set(out_set)
    out_removed = set()

    selectors = []

    while len(out_remaining) > 0:
        in_remaining = set(in_set)
        out_remaining_local = set(out_remaining)
        selector = []

        while len(in_remaining) > 0:
            in_counts = count_substr_occurrences(in_substr, in_remaining)
            out_counts = count_substr_occurrences(in_substr, out_remaining)

            # Find the substring that matches the least of the remaining out-set elements
            # (remember, we need to have at least one selector per out-set element that doesn't match it!)
            for substrings in list_substrings_matching_least(in_counts, out_counts):
                # Never pick one that would bring back something from out_removed
                substrings = [ss for ss in substrings if not any(ss in orm for orm in out_removed)]

                # Never pick one that would match each of the remaining from out_remaining
                substrings = [ss for ss in substrings if not all(ss in x for x in out_remaining_local)]

                # Never pick one that would match nothing from the in-set
                substrings = [ss for ss in substrings if any(ss in w for w in in_remaining)]

                # If all of the most frequent substrings would bring something back, move to the next best one
                ic = Counter({ss: in_counts[ss] for ss in substrings})
                if len(ic) == 0:
                    continue

                # Pick the one that matches the most from in_remaining
                ss = list(ic.most_common())[0][0]

                # We have now picked a substring to include in our selector.
                selector.append(ss)

                out_remaining_local = {x for x in out_remaining_local if not any(ss in x for ss in selector)}

                logger.debug("{}({})   [{}]".format(ss, in_counts[ss], out_remaining_local))

                # Remove it from in_counts, so that it won't get picked again in the next iteration.
                in_counts[ss] = 0

                # Then remove all the entries from in_remaining that match this substring because we don't care about
                # those anymore now.
                in_remaining = {x for x in in_remaining if ss not in x}

                # We stop looking for the substring now.
                break
            else:
                raise Exception("Could not find a match for {}".format(in_remaining))


        # We can filter out now all entries from the out-set that don't match any of the substrings in this selector
        out_removed = {x for x in out_remaining if not any(ss in x for ss in selector)}
        out_remaining = {x for x in out_remaining if any(ss in x for ss in selector)}

        logger.debug(' --- {} remaining'.format(len(out_remaining)))

        selectors.append(selector)

    return selectors


def list_substrings_matching_most(in_counts):
    for k, g in itertools.groupby(in_counts.most_common(), lambda x: x[1]):
        if k == 0:
            continue
        yield [ss for ss, c in list(g)]


def list_substrings_matching_least(in_counts, out_counts):
    yield [ss for ss, c in in_counts.items() if out_counts[ss] == 0]
    for k, g in itertools.groupby(out_counts.most_common(), lambda x: x[1]):
        if k == 0:
            continue
        yield reversed([ss for ss, c in list(g)])


def list_substrings(strings):
    """Return a set of all 1-, 2- and 3-char substrings of strings"""
    substrings = set()

    # full words
    for x in strings:
        substrings.add(x)

    # 2-char substrings
    for s in strings:
        for i in range(len(s) - 1):
            substrings.add(''.join([s[i], s[i+1]]))

    # 3-char substrings
    for s in strings:
        for i in range(len(s) - 2):
            substrings.add(''.join([s[i], s[i+1]]))

    # 4-char substrings
    for s in strings:
        for i in range(len(s) - 3):
            substrings.add(''.join([s[i], s[i+1], s[i+2]]))

    # 5-char substrings
    for s in strings:
        for i in range(len(s) - 4):
            substrings.add(''.join([s[i], s[i+1], s[i+2], s[i+3]]))

    return substrings


def count_substr_occurrences(substrs, strings):
    result = Counter()
    for s in strings:
        for ss in substrs:
            if ss in s:
                result[ss] += 1
    return result
