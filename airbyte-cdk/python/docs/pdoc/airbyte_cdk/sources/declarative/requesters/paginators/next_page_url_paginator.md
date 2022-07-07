Module airbyte_cdk.sources.declarative.requesters.paginators.next_page_url_paginator
====================================================================================

Classes
-------

`NextPageUrlPaginator(url_base: str = None, next_page_token_template: Optional[Mapping[str, str]] = None, config: Optional[Mapping[str, Any]] = None)`
:   A paginator wrapper that delegates to an inner paginator and removes the base url from the next_page_token to only return the path to the next page
    
    :param url_base: url base to remove from the token
    :param interpolated_paginator: optional paginator to delegate to
    :param next_page_token_template: optional mapping to delegate to if interpolated_paginator is None
    :param config: connection config

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.declarative.requesters.paginators.paginator.Paginator
    * abc.ABC

    ### Methods

    `next_page_token(self, response: requests.models.Response, last_records: List[Mapping[str, Any]]) ‑> Optional[Mapping[str, Any]]`
    :