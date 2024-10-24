from flask import Flask, g
from routes.main import main
from routes.auth import auth
from routes.data import data
from database import init_db, get_db_connection, migrate_db
from config import oauth
import os
import secrets

def create_app():
    app = Flask(__name__)

    # Set a secret key for session management
    app.secret_key = secrets.token_hex(32)

    # Load config
    app.config.from_object('config')

    # Initialize OAuth with app
    oauth.init_app(app)

    # Initialize database
    with app.app_context():
        db = get_db_connection()
        init_db(db)
        migrate_db(db)
        db.close()

    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(data, url_prefix='/data')

    @app.before_request
    def before_request():
        g._database = get_db_connection()

    @app.teardown_request
    def teardown_request(exception):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
