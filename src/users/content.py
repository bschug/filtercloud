

def load_style(username, stylename, db):
    data = db.styles.find_one({'owner': username, 'name': stylename})
    if data is None:
        return None
    return data['content']


def load_config(username, configname, db):
    data = db.configs.find_one({'owner': username, 'name': configname})
    if data is None:
        return None
    return data['content']


def store_style(username, stylename, style, db):
    db.styles.update(
        {'owner': username, 'name': stylename},
        {'$set': {'content': style}},
        upsert=True)
    db.users.update(
        {'name': username},
        {'$addToSet': {'styles': stylename}}
    )


def store_config(username, configname, config, db):
    db.configs.update(
        {'owner': username, 'name': configname},
        {'$set': {'content': config}},
        upsert=True
    )
    db.users.update(
        {'name': username},
        {'$addToSet': {'configs': configname}}
    )
