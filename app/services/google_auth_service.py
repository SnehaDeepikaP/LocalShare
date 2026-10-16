import os
import secrets
import requests
from flask import session, url_for, request, current_app

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

def is_google_auth_configured():
    """Check if Google OAuth Client ID and Secret are provided in environment."""
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    return bool(client_id and client_secret and not client_id.startswith('replace-with-'))

def get_google_provider_cfg():
    """Fetch OpenID Connect configuration from Google."""
    try:
        resp = requests.get(GOOGLE_DISCOVERY_URL, timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        current_app.logger.warning(f"Failed to fetch Google OIDC config: {e}")
    # Fallback to standard Google endpoints
    return {
        "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_endpoint": "https://oauth2.googleapis.com/token",
        "userinfo_endpoint": "https://openidconnect.googleapis.com/v1/userinfo"
    }

def get_google_redirect_uri():
    """Construct absolute authorized redirect URI for the current request."""
    # Ensure redirect URI matches what's configured in Google Cloud Console
    return url_for('auth.google_callback', _external=True)

def generate_google_auth_url():
    """Generate state, nonce, and Google authorization URL."""
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    if not is_google_auth_configured():
        return None, None

    provider_cfg = get_google_provider_cfg()
    auth_endpoint = provider_cfg.get("authorization_endpoint")

    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)

    session['oauth_state'] = state
    session['oauth_nonce'] = nonce

    redirect_uri = get_google_redirect_uri()

    auth_url = (
        f"{auth_endpoint}?"
        f"response_type=code&"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=openid%20email%20profile&"
        f"state={state}&"
        f"nonce={nonce}&"
        f"prompt=select_account"
    )
    return auth_url, state

def exchange_google_code_for_userinfo(code, returned_state):
    """
    Validates state and exchanges OAuth authorization code for Google user profile.
    Returns (user_info_dict, error_message).
    """
    stored_state = session.get('oauth_state')
    if not stored_state or not returned_state or stored_state != returned_state:
        return None, "Invalid or expired OAuth state parameter. Please try logging in again."

    # Clear state from session
    session.pop('oauth_state', None)
    session.pop('oauth_nonce', None)

    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    provider_cfg = get_google_provider_cfg()
    token_endpoint = provider_cfg.get("token_endpoint")

    redirect_uri = get_google_redirect_uri()

    # Exchange authorization code for tokens
    token_data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }

    try:
        token_resp = requests.post(token_endpoint, data=token_data, timeout=10)
        if token_resp.status_code != 200:
            current_app.logger.error(f"Google token error: {token_resp.text}")
            return None, "Failed to exchange authorization code with Google."

        tokens = token_resp.json()
        access_token = tokens.get('access_token')
        if not access_token:
            return None, "Google token response did not contain an access token."

        # Fetch verified userinfo using access token
        userinfo_endpoint = provider_cfg.get("userinfo_endpoint")
        userinfo_resp = requests.get(
            userinfo_endpoint,
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        if userinfo_resp.status_code != 200:
            return None, "Failed to fetch user profile from Google."

        userinfo = userinfo_resp.json()

        # Enforce verified email requirement
        if not userinfo.get('email_verified', False):
            return None, "Your Google email address is not verified by Google."

        return userinfo, None

    except Exception as e:
        current_app.logger.exception("Exception during Google OIDC exchange")
        return None, f"An error occurred while communicating with Google: {str(e)}"
