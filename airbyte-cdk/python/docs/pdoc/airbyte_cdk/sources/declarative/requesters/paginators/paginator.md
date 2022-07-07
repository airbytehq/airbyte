Module airbyte_cdk.sources.declarative.requesters.paginators.paginator
======================================================================

Classes
-------

`Paginator()`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * airbyte_cdk.sources.declarative.requesters.paginators.interpolated_paginator.InterpolatedPaginator
    * airbyte_cdk.sources.declarative.requesters.paginators.next_page_url_paginator.NextPageUrlPaginator
    * airbyte_cdk.sources.declarative.requesters.paginators.no_pagination.NoPagination
    * airbyte_cdk.sources.declarative.requesters.paginators.offset_paginator.OffsetPaginator

    ### Methods

    `next_page_token(self, response: requests.models.Response, last_records: List[Mapping[str, Any]]) ‑> Optional[Mapping[str, Any]]`
    :