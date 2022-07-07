Module airbyte_cdk.sources.declarative.requesters.paginators.interpolated_paginator
===================================================================================

Classes
-------

`InterpolatedPaginator(*, next_page_token_template: Mapping[str, str], config: Mapping[str, Any], decoder: Optional[airbyte_cdk.sources.declarative.decoders.decoder.Decoder] = None)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.declarative.requesters.paginators.paginator.Paginator
    * abc.ABC

    ### Methods

    `next_page_token(self, response: requests.models.Response, last_records: List[Mapping[str, Any]]) ‑> Optional[Mapping[str, Any]]`
    :