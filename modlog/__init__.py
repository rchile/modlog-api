from flask import Flask
from flask_cors import CORS

from modlog.common import get_config, valid_entry_id, filter_entry, get_logger
from modlog.worker import WorkerThread


def create_app():
    # thread = WorkerThread()
    # thread.start()

    app = Flask(__name__)
    CORS(app, supports_credentials=True)  # Enable CORS for this app
    app.config['SECRET_KEY'] = get_config('SESSION_SECRET')

    return app
