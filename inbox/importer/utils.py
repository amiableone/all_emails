from google_auth_oauthlib.flow import Flow


def google_oauth2(login, redirect_uri):
    flow = Flow.from_client_secrets_file(
        "../../client_secret.json",
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    )
    flow.redirect_uri = redirect_uri
    auth_url, state = flow.authorization_url(
        access_type="offline",
        login_hint=login,
        prompt="consent",
    )
    return flow, auth_url, state
