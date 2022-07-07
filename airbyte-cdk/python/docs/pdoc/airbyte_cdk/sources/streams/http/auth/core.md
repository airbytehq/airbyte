Module airbyte_cdk.sources.streams.http.auth.core
=================================================

Classes
-------

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

`NoAuth(*args, **kwargs)`
:   Base abstract class for various HTTP Authentication strategies. Authentication strategies are generally
    expected to provide security credentials via HTTP headers.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.streams.http.auth.core.HttpAuthenticator
    * abc.ABC