Module airbyte_cdk.sources.declarative.requesters.paginators.no_pagination
==========================================================================

Classes
-------

`NoPagination()`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.declarative.requesters.paginators.paginator.Paginator
    * abc.ABC

    ### Methods

    `next_page_token(self, response: requests.models.Response, last_records: List[Mapping[str, Any]]) ‑> Optional[Mapping[str, Any]]`
    :