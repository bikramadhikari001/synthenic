import os
from authlib.integrations.flask_client import OAuth

# Auth0 configuration with hardcoded values
AUTH0_CLIENT_ID = 'YOqctT8i6HJhkbMKz7rjN3qlFs3HJkgG'
AUTH0_CLIENT_SECRET = 'F3Y5Ij6oH3Xn-bz_NJaMBIFmIDf5Djwovzn8tbT_Mpum6ywlKYhxEuGXGiXAv_eo'
AUTH0_DOMAIN = 'dev-5bknupzhbwplp5fc.us.auth0.com'
AUTH0_CALLBACK_URL = 'https://syntheti.org/callback'

# Initialize OAuth
oauth = OAuth()

# Configure Auth0
auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=f'https://{AUTH0_DOMAIN}',
    access_token_url=f'https://{AUTH0_DOMAIN}/oauth/token',
    authorize_url=f'https://{AUTH0_DOMAIN}/authorize',
    jwks_uri=f'https://{AUTH0_DOMAIN}/.well-known/jwks.json',
    server_metadata_url=f'https://{AUTH0_DOMAIN}/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid profile email',
        'response_type': 'code'
    }
)
