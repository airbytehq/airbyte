Module airbyte_cdk.sources.streams.http.auth.token
==================================================

Classes
-------

`BasicHttpAuthenticator(username: str, password: str, auth_method: str = 'Basic', auth_header: str = 'Authorization')`
:   Builds auth based off the basic authentication scheme as defined by RFC 7617, which transmits credentials as USER ID/password pairs, encoded using bas64
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#basic_authentication_scheme

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.streams.http.auth.token.TokenAuthenticator
    * airbyte_cdk.sources.streams.http.auth.core.HttpAuthenticator
    * abc.ABC

`MultipleTokenAuthenticator(tokens: List[str], auth_method: str = 'Bearer', auth_header: str = 'Authorization')`
:   Base abstract class for various HTTP Authentication strategies. Authentication strategies are generally
    expected to provide security credentials via HTTP headers.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.streams.http.auth.core.HttpAuthenticator
    * abc.ABC

`TokenAuthenticator(token: str, auth_method: str = 'Bearer', auth_header: str = 'Authorization')`
:   Base abstract class for various HTTP Authentication strategies. Authentication strategies are generally
    expected to provide security credentials via HTTP headers.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.streams.http.auth.core.HttpAuthenticator
    * abc.ABC

    ### Descendants

    * airbyte_cdk.sources.streams.http.auth.token.BasicHttpAuthenticator