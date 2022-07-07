Module airbyte_cdk.sources.declarative.requesters.interpolated_request_input_provider
=====================================================================================

Classes
-------

`InterpolatedRequestInputProvider(*, config, request_inputs=None)`
:   Helper class that generically performs string interpolation on the provided dictionary or string input

    ### Methods

    `request_inputs(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> Union[Mapping, str]`
    :