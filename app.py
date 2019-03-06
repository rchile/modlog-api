from flask import Flask, jsonify, redirect
from flask_cors import CORS
from common import *

reddit = get_reddit_instance()
sub = reddit.subreddit('chile')
app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return redirect('https://reddit.com/r/chile')


@app.route('/entries', defaults={'after': None})
@app.route('/entries/after/<after>')
def modlog_entries(after):
    if after is not None:
        if not pat_modentry.match(after):
            raise InvalidUsage('Invalid entry id')
        if not after.startswith('ModAction_'):
            after = 'ModAction_' + after

    modactions = list(map(serialize, sub.mod.log(limit=100, params={'after': after})))
    return jsonify(modactions)


@app.route('/entry/<entry_id>')
def modlog_entry(entry_id):
    if not pat_modentry.match(entry_id):
        raise InvalidUsage('Invalid ModAction entry id')
    if not entry_id.startswith('ModAction_'):
        entry_id = 'ModAction_' + entry_id

    # Fetch the first after the selected one
    after_entries = list(sub.mod.log(limit=1, params={'after': entry_id}))
    if len(after_entries) == 0:
        raise InvalidUsage('Entry not found', 404)

    # Fetch the entry before the previous one, it should be the entry we want
    entry = list(sub.mod.log(limit=1, params={'before': after_entries[0].id}))
    if len(entry) == 0:
        raise InvalidUsage('Entry not found', 404)

    # If the fetched entry does not match the ID, then the entry does not exist
    entry = serialize(entry[0])
    if entry['id'] != entry_id:
        raise InvalidUsage('Entry not found', 404)

    return jsonify(entry)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == '__main__':
    app.run()
