import os
import re
import praw
from praw.models import ModAction

import settings

pat_modentry = re.compile(r'^(ModAction_)?[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$')


def get_reddit_instance():
    """
    Creates a ``praw.Reddit`` instance with parameters from settings or environment variables.
    If variables are not set, then the RuntimeError exception is raised.
    :return: A ``praw.Reddit`` instance.
    """
    params = {
        'client_id': settings.CLIENT_ID or os.environ.get('CLIENT_ID', ''),
        'client_secret': settings.CLIENT_SECRET or os.environ.get('CLIENT_SECRET', ''),
        'refresh_token': settings.REFRESH_TOKEN or os.environ.get('REFRESH_TOKEN', ''),
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
