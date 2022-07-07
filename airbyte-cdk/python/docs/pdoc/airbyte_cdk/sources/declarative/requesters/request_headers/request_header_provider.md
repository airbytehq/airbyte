Module airbyte_cdk.sources.declarative.requesters.request_headers.request_header_provider
=========================================================================================

Classes
-------

`RequestHeaderProvider()`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * airbyte_cdk.sources.declarative.requesters.request_headers.interpolated_request_header_provider.InterpolatedRequestHeaderProvider

    ### Methods

    `request_headers(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> Mapping[str, Any]`
    :