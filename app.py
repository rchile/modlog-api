from flask import Flask, jsonify, redirect
from flask_cors import CORS

from modlog.common import InvalidUsage, get_reddit_instance, random_string
from modlog import data

app = Flask(__name__)
CORS(app)  # Enable CORS for this app


@app.route('/')
def index():
    return redirect('https://reddit.com/r/chile')


@app.route('/login')
def login():
    r = get_reddit_instance(app=True)
    return redirect(r.auth.url(['identity'], random_string()))


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
