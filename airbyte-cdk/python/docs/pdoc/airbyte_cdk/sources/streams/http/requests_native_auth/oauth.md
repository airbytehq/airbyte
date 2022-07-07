Module airbyte_cdk.sources.streams.http.requests_native_auth.oauth
==================================================================

Classes
-------

`Oauth2Authenticator(token_refresh_endpoint: str, client_id: str, client_secret: str, refresh_token: str, scopes: List[str] = None, token_expiry_date: pendulum.datetime.DateTime = None, access_token_name: str = 'access_token', expires_in_name: str = 'expires_in')`
:   Generates OAuth2.0 access tokens from an OAuth2.0 refresh token and client credentials.
    The generated access token is attached to each request via the Authorization header.

    ### Ancestors (in MRO)

    * requests.auth.AuthBase

    ### Methods

    `get_access_token(self)`
    :

    `get_auth_header(self) ‑> Mapping[str, Any]`
    :

    `get_refresh_request_body(self) ‑> Mapping[str, Any]`
    :   Override to define additional parameters

    `refresh_access_token(self) ‑> Tuple[str, int]`
    :   returns a tuple of (access_token, token_lifespan_in_seconds)

    `token_has_expired(self) ‑> bool`
    :