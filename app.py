from flask import Flask, g
from werkzeug.middleware.proxy_fix import ProxyFix
from routes.main import main
from routes.auth import auth
from routes.data import data
from database import init_db, get_db_connection, migrate_db
from config import oauth
import os
import secrets

def create_app():
    app = Flask(__name__)

    # Configure ProxyFix for HTTPS behind nginx
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Use a fixed secret key or load from environment variable
    app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-fixed-secret-key-here')

    # Load config
    app.config.from_object('config')

    # Force HTTPS for session cookie
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['PREFERRED_URL_SCHEME'] = 'https'

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
