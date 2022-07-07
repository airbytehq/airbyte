Module airbyte_cdk.sources.streams.http.requests_native_auth
============================================================

Sub-modules
-----------
* airbyte_cdk.sources.streams.http.requests_native_auth.oauth
* airbyte_cdk.sources.streams.http.requests_native_auth.token

Classes
-------

`MultipleTokenAuthenticator(tokens: List[str], auth_method: str = 'Bearer', auth_header: str = 'Authorization')`
:   Builds auth header, based on the list of tokens provided.
    Auth header is changed per each `get_auth_header` call, using each token in cycle.
    The token is attached to each request via the `auth_header` header.

    ### Ancestors (in MRO)

    * requests.auth.AuthBase

    ### Descendants

    * airbyte_cdk.sources.streams.http.requests_native_auth.token.TokenAuthenticator

    ### Methods

    `get_auth_header(self) ‑> Mapping[str, Any]`
    :

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

`TokenAuthenticator(token: str, auth_method: str = 'Bearer', auth_header: str = 'Authorization')`
:   Builds auth header, based on the token provided.
    The token is attached to each request via the `auth_header` header.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.streams.http.requests_native_auth.token.MultipleTokenAuthenticator
    * requests.auth.AuthBase

    ### Descendants

    * airbyte_cdk.sources.streams.http.requests_native_auth.token.BasicHttpAuthenticator