Module airbyte_cdk.sources.declarative.requesters.http_requester
================================================================

Classes
-------

`HttpRequester(*, name: str, url_base: [<class 'str'>, <class 'airbyte_cdk.sources.declarative.interpolation.interpolated_string.InterpolatedString'>], path: [<class 'str'>, <class 'airbyte_cdk.sources.declarative.interpolation.interpolated_string.InterpolatedString'>], http_method: Union[str, airbyte_cdk.sources.declarative.requesters.requester.HttpMethod] = HttpMethod.GET, request_options_provider: Optional[airbyte_cdk.sources.declarative.requesters.request_options.request_options_provider.RequestOptionsProvider] = None, authenticator: airbyte_cdk.sources.streams.http.auth.core.HttpAuthenticator, retrier: Optional[airbyte_cdk.sources.declarative.requesters.retriers.retrier.Retrier] = None, config: Mapping[str, Any])`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.declarative.requesters.requester.Requester
    * abc.ABC