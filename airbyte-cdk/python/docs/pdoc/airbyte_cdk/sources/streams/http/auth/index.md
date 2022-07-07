Module airbyte_cdk.sources.streams.http.auth
============================================

Sub-modules
-----------
* airbyte_cdk.sources.streams.http.auth.core
* airbyte_cdk.sources.streams.http.auth.oauth
* airbyte_cdk.sources.streams.http.auth.token

Classes
-------

`BasicHttpAuthenticator(username: str, password: str, auth_method: str = 'Basic', auth_header: str = 'Authorization')`
:   Builds auth based off the basic authentication scheme as defined by RFC 7617, which transmits credentials as USER ID/password pairs, encoded using bas64
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#basic_authentication_scheme

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.streams.http.auth.token.TokenAuthenticator
    * airbyte_cdk.sources.streams.http.auth.core.HttpAuthenticator
    * abc.ABC

`HttpAuthenticator(*args, **kwargs)`
:   Base abstract class for various HTTP Authentication strategies. Authentication strategies are generally
    expected to provide security credentials via HTTP headers.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * airbyte_cdk.sources.streams.http.auth.core.NoAuth
    * airbyte_cdk.sources.streams.http.auth.oauth.Oauth2Authenticator
    * airbyte_cdk.sources.streams.http.auth.token.MultipleTokenAuthenticator
    * airbyte_cdk.sources.streams.http.auth.token.TokenAuthenticator

    ### Methods

    `get_auth_header(self) ‑> Mapping[str, Any]`
    :   :return: A dictionary containing all the necessary headers to authenticate.

`MultipleTokenAuthenticator(tokens: List[str], auth_method: str = 'Bearer', auth_header: str = 'Authorization')`
:   Base abstract class for various HTTP Authentication strategies. Authentication strategies are generally
    expected to provide security credentials via HTTP headers.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.streams.http.auth.core.HttpAuthenticator
    * abc.ABC

`NoAuth(*args, **kwargs)`
:   Base abstract class for various HTTP Authentication strategies. Authentication strategies are generally
    expected to provide security credentials via HTTP headers.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.streams.http.auth.core.HttpAuthenticator
    * abc.ABC

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

`TokenAuthenticator(token: str, auth_method: str = 'Bearer', auth_header: str = 'Authorization')`
:   Base abstract class for various HTTP Authentication strategies. Authentication strategies are generally
    expected to provide security credentials via HTTP headers.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.streams.http.auth.core.HttpAuthenticator
    * abc.ABC

    ### Descendants

    * airbyte_cdk.sources.streams.http.auth.token.BasicHttpAuthenticator