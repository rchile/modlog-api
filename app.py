from flask import Flask, jsonify, redirect, request, session, abort
from flask_cors import CORS

from modlog.api import get_reddit_instance
from modlog.common import InvalidUsage, random_string, pat_oauth_code, pat_oauth_state, get_config, require_session, \
    get_authed_instance, user_is_allowed
from modlog import data
from modlog.data import db

app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable CORS for this app
app.config['SECRET_KEY'] = get_config('SESSION_SECRET')


@app.route('/')
def index():
    return redirect('https://rchile.xyz/modlog/')


@app.route('/login')
def login():
    if get_authed_instance(session) is not None:
        return redirect(get_config('APP_REDIRECT', 'http://127.0.0.1:8000/'))

    reddit = get_reddit_instance(app=True)
    session['state'] = random_string()
    return redirect(reddit.auth.url(['identity', 'read'], session['state']))


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

    refresh = reddit.auth.authorize(code)
    if refresh is None or not user_is_allowed(reddit):
        return abort(403)

    session['refresh_token'] = refresh
    return redirect(get_config('APP_REDIRECT', 'http://127.0.0.1:8000/'))


@app.route('/logout')
def logout():
    del session['refresh_token']
    return redirect(get_config('APP_REDIRECT', 'http://127.0.0.1:8000/'))


@app.route('/session_test')
@require_session()
def session_test(reddit):
    return jsonify({'logged': True, 'username': reddit.user.me().name})


@app.route('/session')
def session_info():
    reddit = get_authed_instance(session)
    if reddit is None:
        return jsonify({'logged': False})

    return jsonify({'logged': True, 'username': reddit.user.me().name})


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


@app.route('/entry_notes/', methods=['POST'])
@require_session()
def modlog_set_note(reddit):
    form = request.json
    if 'entry_id' not in form:
        raise InvalidUsage('entry_id text not sent')

    entry_id = form['entry_id']
    entry = data.get_entry(entry_id)

    if entry is None:
        raise InvalidUsage('Entry not found', 404)

    if 'notes' not in form:
        raise InvalidUsage('Note text not sent')

    if len(form['notes']) > 1000:
        raise InvalidUsage('Note text too long')

    db.set_entry_note(entry_id, form['notes'])
    return jsonify({'success': True})


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == '__main__':
    app.run()
