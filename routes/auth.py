from flask import Blueprint, redirect, session, url_for, request, g
from functools import wraps
from urllib.parse import urlencode
import secrets
from config import auth0, AUTH0_CLIENT_ID, AUTH0_CALLBACK_URL, AUTH0_DOMAIN
from database import add_user

auth = Blueprint('auth', __name__)

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@auth.route('/login')
def login():
    session['state'] = secrets.token_urlsafe(32)
    return auth0.authorize_redirect(
        redirect_uri=AUTH0_CALLBACK_URL,
        state=session['state']
    )

@auth.route('/callback')
def callback():
    # Verify state before token exchange
    if 'state' not in session:
        return redirect(url_for('main.index'))
    
    if request.args.get('state') != session['state']:
        return redirect(url_for('main.index'))

    token = auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    session['jwt_payload'] = userinfo
    session['user'] = {
        'user_id': userinfo['sub'],
        'name': userinfo.get('name', ''),
        'email': userinfo.get('email', '')
    }

    # Add user to database
    add_user(g._database, userinfo['sub'], userinfo.get('name', ''), userinfo.get('email', ''))

    return redirect(url_for('main.dashboard'))

@auth.route('/logout')
def logout():
    session.clear()
    params = {
        'returnTo': 'https://syntheti.org',
        'client_id': AUTH0_CLIENT_ID
    }
    return redirect(f'https://{AUTH0_DOMAIN}/v2/logout?{urlencode(params)}')
