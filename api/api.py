from flask import request, jsonify, redirect

from .database import Modlog
from .constants import pat_entry_id, pat_user, limit_allowed
from .functions import try_int, response
from settings import DEFAULT_PAGE_LIMIT

db = Modlog.get_instance()


def index():
    return redirect('https://rchile.net/')


def entries():
    filters = {}

    # Exclude AutoModerator (automod=0)
    automod = request.args.get('automod', '') not in ['false', 'False', '0']
    if not automod:
        filters['mod'] = {'$ne': 'AutoModerator'}
    
    # Filter by specific mod (mod=<mod_username>)
    mod = pat_user.match(request.args.get('mod', ''))
    if mod:
        filters['mod'] = mod.groupdict()['username']
    
    # Filter by specific user target (user=<username>)
    mod = pat_user.match(request.args.get('user', ''))
    if mod:
        filters['target_author'] = mod.groupdict()['username']

    # Get mod actions after a specific entry (after=<entry_id>)
    after_id = pat_entry_id.match(request.args.get('after', ''))
    if after_id:
        after_id = 'ModAction_' + mod.groupdict()['entry_id']

    # Fetch entries and return
    limit = try_int(request.args.get('limit', ''), DEFAULT_PAGE_LIMIT)
    if limit not in limit_allowed:
        limit = DEFAULT_PAGE_LIMIT
    entries = db.entries(after_id, limit, filters)
    return jsonify(entries)


def entry(entry_id=None):
    entry_id = pat_entry_id.match(entry_id)
    if not entry_id:
        return response('Invalid entry ID', 400)

    entry = db.entry('ModAction_' + entry_id.groupdict()['entry_id'])
    if not entry:
        return response('Entry not found', 404)

    return entry
