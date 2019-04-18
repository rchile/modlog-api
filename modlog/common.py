import os
import re
import praw
from praw.models import ModAction

pat_modentry = re.compile(r'^(ModAction_)?[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$')


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


def get_reddit_instance():
    """
    Creates a ``praw.Reddit`` instance with parameters from settings or environment variables.
    If variables are not set, then the RuntimeError exception is raised.
    :return: A ``praw.Reddit`` instance.
    """

    params = {
        'client_id': get_config('CLIENT_ID', ''),
        'client_secret': get_config('CLIENT_SECRET', ''),
        'refresh_token': get_config('REFRESH_TOKEN', ''),
        'user_agent': 'rchilemodlog/0.1.0'
    }

    if not params['client_id'] or not params['client_secret'] or not params['refresh_token']:
        raise RuntimeError('Configuration vars not set')

    return praw.Reddit(**params)


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
