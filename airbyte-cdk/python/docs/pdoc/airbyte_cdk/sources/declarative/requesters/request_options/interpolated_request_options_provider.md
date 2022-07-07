Module airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider
=======================================================================================================

Classes
-------

`InterpolatedRequestOptionsProvider(*, config, request_parameters=None, request_headers=None, request_body_data=None, request_body_json=None)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.declarative.requesters.request_options.request_options_provider.RequestOptionsProvider
    * abc.ABC

    ### Methods

    `request_body_data(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> Union[Mapping, str, ForwardRef(None)]`
    :

    `request_body_json(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> Optional[Mapping]`
    :

    `request_headers(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> Mapping[str, Any]`
    :

    `request_kwargs(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> Mapping[str, Any]`
    :

    `request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> MutableMapping[str, Any]`
    :