from datetime import datetime


def build_date_string():
    today = datetime.now()
    return '{}-{}-{}'.format(today.year, today.month, today.day)