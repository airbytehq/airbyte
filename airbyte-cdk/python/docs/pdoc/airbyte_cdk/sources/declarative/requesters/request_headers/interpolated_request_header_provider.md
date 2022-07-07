Module airbyte_cdk.sources.declarative.requesters.request_headers.interpolated_request_header_provider
======================================================================================================

Classes
-------

`InterpolatedRequestHeaderProvider(*, config, request_headers)`
:   Provider that takes in a dictionary of request headers and performs string interpolation on the defined templates and static
    values based on the current state of stream being processed

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.declarative.requesters.request_headers.request_header_provider.RequestHeaderProvider
    * abc.ABC

    ### Methods

    `request_headers(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> Mapping[str, Any]`
    :