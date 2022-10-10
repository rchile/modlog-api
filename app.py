from flask import Flask
from api import api
from settings import CORS_ORIGINS

app = Flask(__name__)
app.route('/')(api.index)
app.route('/api/entries', methods=['GET'])(api.entries)
app.route('/api/entries/<entry_id>', methods=['GET'])(api.entry)
app.route('/api/action_count', methods=['GET'])(api.action_count)
app.route('/api/mod_action_count', methods=['GET'])(api.mod_action_count)

if CORS_ORIGINS:
    from flask_cors import CORS
    CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS}})

if __name__ == '__main__':
    import os
    os.environ['FLASK_ENV'] = 'development'
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, port=port)
