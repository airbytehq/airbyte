Module airbyte_cdk.sources.declarative.extractors.http_selector
===============================================================

Classes
-------

`HttpSelector()`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * airbyte_cdk.sources.declarative.extractors.record_selector.RecordSelector

    ### Methods

    `select_records(self, response: requests.models.Response, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> List[Mapping[str, Any]]`
    :