Module airbyte_cdk.sources.streams.http.auth.oauth
==================================================

Classes
-------

`Oauth2Authenticator(token_refresh_endpoint: str, client_id: str, client_secret: str, refresh_token: str, scopes: List[str] = None, refresh_access_token_headers: Optional[Mapping[str, Any]] = None, refresh_access_token_authenticator: Optional[airbyte_cdk.sources.streams.http.auth.core.HttpAuthenticator] = None)`
:   Generates OAuth2.0 access tokens from an OAuth2.0 refresh token and client credentials.
    The generated access token is attached to each request via the Authorization header.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.streams.http.auth.core.HttpAuthenticator
    * abc.ABC

    ### Methods

    `get_access_token(self)`
    :

    `get_refresh_access_token_headers(self)`
    :

    `get_refresh_request_body(self) ‑> Mapping[str, Any]`
    :   Override to define additional parameters

    `refresh_access_token(self) ‑> Tuple[str, int]`
    :   returns a tuple of (access_token, token_lifespan_in_seconds)

    `token_has_expired(self) ‑> bool`
    :