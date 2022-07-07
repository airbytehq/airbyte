Module airbyte_cdk.sources.streams.http.requests_native_auth.token
==================================================================

Classes
-------

`BasicHttpAuthenticator(username: str, password: str, auth_method: str = 'Basic', auth_header: str = 'Authorization')`
:   Builds auth based off the basic authentication scheme as defined by RFC 7617, which transmits credentials as USER ID/password pairs, encoded using bas64
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#basic_authentication_scheme

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.streams.http.requests_native_auth.token.TokenAuthenticator
    * airbyte_cdk.sources.streams.http.requests_native_auth.token.MultipleTokenAuthenticator
    * requests.auth.AuthBase

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

`TokenAuthenticator(token: str, auth_method: str = 'Bearer', auth_header: str = 'Authorization')`
:   Builds auth header, based on the token provided.
    The token is attached to each request via the `auth_header` header.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.streams.http.requests_native_auth.token.MultipleTokenAuthenticator
    * requests.auth.AuthBase

    ### Descendants

    * airbyte_cdk.sources.streams.http.requests_native_auth.token.BasicHttpAuthenticator