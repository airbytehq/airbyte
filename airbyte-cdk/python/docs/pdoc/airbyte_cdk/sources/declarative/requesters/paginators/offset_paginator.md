Module airbyte_cdk.sources.declarative.requesters.paginators.offset_paginator
=============================================================================

Classes
-------

`OffsetPaginator(page_size: int, state: Optional[airbyte_cdk.sources.declarative.states.dict_state.DictState] = None, offset_key: str = 'offset')`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.declarative.requesters.paginators.paginator.Paginator
    * abc.ABC

    ### Methods

    `next_page_token(self, response: requests.models.Response, last_records: List[Mapping[str, Any]]) ‑> Optional[Mapping[str, Any]]`
    :