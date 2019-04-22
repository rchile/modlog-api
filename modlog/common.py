import os
import random
import re
from functools import wraps

import praw
from flask import session, abort
from praw.models import ModAction
from prawcore import OAuthException

pat_modentry = re.compile(r'^(ModAction_)?[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$')
pat_oauth_code = re.compile(r'^[a-zA-Z0-9\-_]{27}$')
pat_oauth_state = re.compile(r'^[a-zA-Z0-9]{12}$')


def get_config(name, default=None):
    """
    Attempts to retrieve a value from the settings module. If not, tries to get
    the value as a environment variable. If also is not found there, the default
    value is returned.
    :param name: The configuration value.
    :param default: The default value.
    :return: The requested configuration value, or the default value if the configuration was not found.
    """

    value = os.environ.get(name, default)
    try:
        import settings
        value = getattr(settings, name, default) or default
    except ModuleNotFoundError:
        pass

    return value


def random_string(length=12, alpha=True):
    str_set = 'abcdefghijklmnopqrstuvwxyz0123456789'
    if not alpha:
        str_set += '!@#$%^&*(-_=+)'

    return ''.join(random.SystemRandom().choice(str_set) for _ in [0] * length)


def serialize(item: ModAction):
    """
    Converts a ``ModAction`` object to a JSON serializable ``dict``.
    :param item:
    :return:
    """
    d = vars(item)
    del d['_reddit']
    d['mod'] = d.pop('_mod')
    return d


def valid_entry_id(value):
    """
    Validates and normalizes an entry ID in the format [ModAction_]<UUID>
    (abcdef01-cdef-0123-4567-0123456789ab), where the first part is optional,
    but is added if it's not found.

    :param value: The value to check and normalize.
    :return: The normalized value.
    :raises InvalidUsage if the entry id does not meet the required format.
    """
    if value is not None:
        if not pat_modentry.match(value):
            raise InvalidUsage('Invalid entry id')
        if not value.startswith('ModAction_'):
            value = 'ModAction_' + value

    return value


def filter_entry(entry):
    """
    Filters data out from a hidden entry
    :param entry: The entry to remove it's public data
    :return: The filtered entry
    """

    if 'hidden' in entry and entry['hidden']:
        clear_attrs = 'target_author,target_permalink,target_body,target_title,' \
                      'target_fullname,description,details'.split(',')
        for x in clear_attrs:
            entry[x] = None

    return entry


def get_reddit_instance(app=False, refresh=None):
    """
    Creates a ``praw.Reddit`` instance with parameters from settings or environment variables.
    If variables are not set, then the RuntimeError exception is raised.
    :param app: Return an instance based on an app or a user profile.
    :param refresh: A refresh token in case if it's needed (e.g., to verify a session)
    :return: A ``praw.Reddit`` instance.
    """

    if app:
        params = {
            'client_id': get_config('APP_ID', ''),
            'client_secret': get_config('APP_SECRET', ''),
            'redirect_uri': get_config('APP_RETURN', 'http://localhost:8080/return'),
            'user_agent': 'rchilemodlog/0.1.0'
        }

        if not params['client_id'] or not params['client_secret'] or not params['redirect_uri']:
            raise RuntimeError('Configuration vars not set')
    else:
        params = {
            'client_id': get_config('CLIENT_ID', ''),
            'client_secret': get_config('CLIENT_SECRET', ''),
            'refresh_token': get_config('REFRESH_TOKEN', ''),
            'user_agent': 'rchilemodlog/0.1.0'
        }

        if not params['client_id'] or not params['client_secret'] or not params['refresh_token']:
            raise RuntimeError('Configuration vars not set')

    if refresh:
        params['refresh_token'] = refresh

    return praw.Reddit(**params)


def user_is_allowed(reddit):
    user_name = reddit.user.me().name
    mods = reddit.subreddit(get_config('SUBREDDIT', 'chile')).moderator()
    mod = next(x for x in mods if user_name == x.name and 'all' in x.mod_permissions)

    return mod is not None


def get_authed_instance(_session):
    session_refresh = _session.get('refresh_token', '')
    if session_refresh == '':
        return None

    try:
        reddit = get_reddit_instance(app=True, refresh=session_refresh)
        if not user_is_allowed(reddit):
            del _session['refresh_token']
            return None
        else:
            return reddit
    except OAuthException:
        return None


def require_session():
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            reddit = get_authed_instance(session)
            if reddit is None:
                return abort(403)

            kwargs['reddit'] = reddit
            return f(*args, **kwargs)

        return wrapped
    return decorator


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
