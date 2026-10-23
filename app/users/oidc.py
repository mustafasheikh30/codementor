from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client.apps import StarletteOAuth2App

from app.core.config import settings

CODEFORCES_DISCOVERY_URL = "https://codeforces.com/.well-known/openid-configuration"


def codeforces_client() -> StarletteOAuth2App:
    """Create the Codeforces OIDC client from server-side environment settings."""
    oauth = OAuth()
    oauth.register(
        name="codeforces",
        client_id=settings.codeforces_oidc_client_id,
        client_secret=settings.codeforces_oidc_client_secret.get_secret_value(),
        server_metadata_url=CODEFORCES_DISCOVERY_URL,
        client_kwargs={
            "scope": "openid",
            "token_endpoint_auth_method": "client_secret_post",
        },
    )
    client = oauth.create_client("codeforces")
    if client is None:
        raise RuntimeError("Authlib did not create the Codeforces OIDC client")
    return client
