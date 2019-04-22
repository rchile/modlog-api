from flask import Flask, jsonify, redirect, request, session, abort
from flask_cors import CORS

from modlog.api import get_reddit_instance, api
from modlog.common import InvalidUsage, random_string, pat_oauth_code, pat_oauth_state, get_config
from modlog import data

app = Flask(__name__)
CORS(app)  # Enable CORS for this app
app.config['SECRET_KEY'] = get_config('SESSION_SECRET')


@app.route('/')
def index():
    return redirect('https://rchile.xyz/modlog/')


@app.route('/login')
def login():
    reddit = get_reddit_instance(app=True)
    session['state'] = random_string()
    return redirect(reddit.auth.url(['identity'], session['state']))


@app.route('/return')
def login_return():
    reddit = get_reddit_instance(app=True)
    code = request.args.get('code', '')
    state = request.args.get('state', '')
    if not pat_oauth_code.match(code) or not pat_oauth_state.match(state):
        print(pat_oauth_code.match(code), pat_oauth_state.match(state))
        return abort(400)

    if state != session.get('state', ''):
        return abort(401)

    if reddit.auth.authorize(code) is None:
        return abort(403)

    mods = reddit.subreddit(get_config('SUBREDDIT', 'chile')).moderator()
    print(mods)

    return reddit.user.me().name


@app.route('/entries', defaults={'after': None})
@app.route('/entries/after/<after>')
def modlog_entries(after):
    modactions = data.get_entries(after)
    return jsonify(modactions)


@app.route('/entry/<entry_id>')
def modlog_entry(entry_id):
    entry = data.get_entry(entry_id)
    if entry is None:
        raise InvalidUsage('Entry not found', 404)

    return jsonify(entry)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == '__main__':
    app.run()
