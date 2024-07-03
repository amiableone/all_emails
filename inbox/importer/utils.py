from google_auth_oauthlib.flow import Flow
from pathlib import Path

from django.conf import settings

CLIENT_SECRET = settings.BASE_DIR.parent / "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def google_oauth2(login, redirect_uri):
    flow = Flow.from_client_secrets_file(CLIENT_SECRET, scopes=SCOPES)
    # Pass redirect_uri to the current func from GoogleAuthView.
    flow.redirect_uri = redirect_uri
    # Generate url of Google's OAuth2.0 server to redirect a user to.
    # The server will authenticate and obtain consent from the user to
    # read messages from their Gmail inbox.
    auth_url, state = flow.authorization_url(
        access_type="offline",
        login_hint=login,
        prompt="consent",
    )
    return auth_url, state


def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
    }


def google_oauth2_cb(state, redirect_uri, auth_resp):
    # State is retrieved from session in CompleteGoogleAuthView.get().
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET,
        scopes=SCOPES,
        state=state,
    )
    flow.redirect_uri = redirect_uri
    flow.fetch_token(authorization_response=auth_resp)
    credentials = flow.credentials
    return credentials_to_dict(credentials)
