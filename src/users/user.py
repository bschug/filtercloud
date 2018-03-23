import re


def load(token, db):
    user_id = get_userid_from_google_token(token)
    userdata = db.users.find_one({'id': user_id})
    return User(userdata, token)


def create(token, name, db):
    """
    Create a new user. If the user is already registered, or the name is already taken, pymongo raises a
    DuplicateKeyError. If the name is invalid, raises a ValueError.
    :param token: Google auth token
    :param name: Desired username
    :param db: Database instance
    :return: The created user object
    """
    if not is_valid_name(name):
        raise ValueError("Invalid Username: " + str(name))
    userdata = {
        'id': get_userid_from_google_token(token),
        'name': name,
        'configs': [],
        'styles': []
    }
    db.users.insert(userdata)
    return User(userdata, token)


def is_valid_name(name):
    """
    Checks if the name is a valid username.
    Usernames must contain only lowercase characters, digits and minus.
    They must neither start nor end with a minus.
    They must be at least two characters long.
    """
    return re.match(r'[a-z0-9]+[a-z0-9\-]*[a-z0-9]+', name) is not None


def create_anonymous():
    return User({}, None)


class User(object):
    """
    User object, compatible with Flask-Login.
    """
    def __init__(self, data, token):
        self.data = data or {}
        self.token = token

    @property
    def is_authenticated(self):
        return 'id' in self.data

    @property
    def is_active(self):
        return self.is_authenticated

    @property
    def is_anonymous(self):
        return not self.is_authenticated

    def get_id(self):
        return self.token

    @property
    def name(self):
        return self.data.get('name')

    @property
    def configs(self):
        """List of filter configs owned by this user"""
        return self.data.get('configs', [])

    @property
    def styles(self):
        """List of styles owned by this user"""
        return self.data.get('styles', [])

    def to_dict(self):
        return {
            'name': self.name,
            'configs': self.configs,
            'styles': self.styles
        }


def get_userid_from_google_token(token):
    from google.oauth2 import id_token
    import google.auth.transport.requests
    import cachecontrol
    import requests

    try:
        session = requests.session()
        cached_session = cachecontrol.CacheControl(session)
        request = google.auth.transport.requests.Request(session=cached_session)

        client_id = "951108445762-7bp1popjbdemfdhhnkmiqm2ml9u8kdmp.apps.googleusercontent.com"
        idinfo = id_token.verify_oauth2_token(token, request, client_id)
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise AuthenticationError('bad_token')

        return idinfo['sub']

    except:
        # That google function above can also raise some exception if it fails.
        # All we need to know is that authentication failed, so we convert everything
        # to AuthenticationError.
        raise AuthenticationError('bad_token')


class AuthenticationError(Exception):
    """
    Raise if the authentication token provided by the user wasn't valid.
    """
    def __init__(self, reason):
        super().__init__('Authentication Error')
        self.reason = reason
