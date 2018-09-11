from datetime import datetime


def build_date_string():
    today = datetime.now()
    return '{}-{}-{}'.format(today.year, today.month, today.day)


def sort_into_tiers(prices, thresholds):
    return {
        'top_tier': [k for k, v in prices.items() if v >= thresholds.top_tier],
        'valuable': [k for k, v in prices.items() if v >= thresholds.valuable and v < thresholds.top_tier],
        'mediocre': [k for k, v in prices.items() if v > thresholds.worthless and v < thresholds.valuable],
        'worthless': [k for k, v in prices.items() if v > thresholds.hidden and v <= thresholds.worthless],
        'hidden': [k for k, v in prices.items() if v < thresholds.hidden],
    }
