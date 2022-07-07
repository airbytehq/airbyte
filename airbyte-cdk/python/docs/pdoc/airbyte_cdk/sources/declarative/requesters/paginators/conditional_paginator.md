Module airbyte_cdk.sources.declarative.requesters.paginators.conditional_paginator
==================================================================================

Classes
-------

`ConditionalPaginator(stop_condition: str, state: airbyte_cdk.sources.declarative.states.dict_state.DictState, decoder: airbyte_cdk.sources.declarative.decoders.decoder.Decoder, config)`
:   A paginator that performs pagination by incrementing a page number and stops based on a provided stop condition.

    ### Methods

    `next_page_token(self, response: requests.models.Response, last_records: List[Mapping[str, Any]]) ‑> Optional[Mapping[str, Any]]`
    :