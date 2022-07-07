Module airbyte_cdk.sources.declarative.extractors.record_selector
=================================================================

Classes
-------

`RecordSelector(extractor: airbyte_cdk.sources.declarative.extractors.jello.JelloExtractor, record_filter: airbyte_cdk.sources.declarative.extractors.record_filter.RecordFilter = None)`
:   Responsible for translating an HTTP response into a list of records by extracting records from the response and optionally filtering
    records based on a heuristic.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.declarative.extractors.http_selector.HttpSelector
    * abc.ABC

    ### Methods

    `select_records(self, response: requests.models.Response, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> List[Mapping[str, Any]]`
    :