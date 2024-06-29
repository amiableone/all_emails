from google_auth_oauthlib.flow import Flow

CLIENT_SECRET = "../../client_secret.json"
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
