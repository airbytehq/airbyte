Module airbyte_cdk.sources.declarative.retrievers.simple_retriever
==================================================================

Classes
-------

`SimpleRetriever(name, primary_key, requester: airbyte_cdk.sources.declarative.requesters.requester.Requester, record_selector: airbyte_cdk.sources.declarative.extractors.http_selector.HttpSelector, paginator: airbyte_cdk.sources.declarative.requesters.paginators.paginator.Paginator = None, stream_slicer: Optional[airbyte_cdk.sources.declarative.stream_slicers.stream_slicer.StreamSlicer] = <airbyte_cdk.sources.declarative.stream_slicers.single_slice.SingleSlice object>, state: Optional[airbyte_cdk.sources.declarative.states.state.State] = None)`
:   Base abstract class for an Airbyte Stream using the HTTP protocol. Basic building block for users building an Airbyte source for a HTTP API.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.declarative.retrievers.retriever.Retriever
    * airbyte_cdk.sources.streams.http.http.HttpStream
    * airbyte_cdk.sources.streams.core.Stream
    * abc.ABC

    ### Class variables

    `page_size: Optional[int]`
    :

    ### Instance variables

    `cache_filename`
    :   Return the name of cache file

    `max_retries: Optional[int]`
    :   Specifies maximum amount of retries for backoff policy. Return None for no limit.

    `name: str`
    :   :return: Stream name

    `raise_on_http_errors: bool`
    :   If set to False, allows opting-out of raising HTTP code exception.

    `retry_factor: float`
    :   Specifies factor to multiply the exponentiation by for backoff policy.

    `use_cache`
    :   If True, all records will be cached.

    ### Methods

    `backoff_time(self, response: requests.models.Response) ‑> Optional[float]`
    :   Specifies backoff time.
        
         This method is called only if should_backoff() returns True for the input request.
        
         :param response:
         :return how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff
         to the default backoff behavior (e.g using an exponential algorithm).

    `next_page_token(self, response: requests.models.Response) ‑> Optional[Mapping[str, Any]]`
    :   Specifies a pagination strategy.
        
        The value returned from this method is passed to most other methods in this class. Use it to form a request e.g: set headers or query params.
        
        :return: The token for the next page from the input response object. Returning None means there are no more pages to read in this response.

    `request_body_data(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> Union[Mapping, str, ForwardRef(None)]`
    :   Specifies how to populate the body of the request with a non-JSON payload.
        
        If returns a ready text that it will be sent as is.
        If returns a dict that it will be converted to a urlencoded form.
        E.g. {"key1": "value1", "key2": "value2"} => "key1=value1&key2=value2"
        
        At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.

    `request_body_json(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> Optional[Mapping]`
    :   Specifies how to populate the body of the request with a JSON payload.
        
        At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.

    `request_headers(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> Mapping[str, Any]`
    :   Specifies request headers.
        Authentication headers will overwrite any overlapping headers returned from this method.

    `request_kwargs(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> Mapping[str, Any]`
    :   Specifies how to configure a mapping of keyword arguments to be used when creating the HTTP request.
        Any option listed in https://docs.python-requests.org/en/latest/api/#requests.adapters.BaseAdapter.send for can be returned from
        this method. Note that these options do not conflict with request-level options such as headers, request params, etc..

    `request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> MutableMapping[str, Any]`
    :   Specifies the query parameters that should be set on an outgoing HTTP request given the inputs.
        
        E.g: you might want to define query parameters for paging if next_page_token is not None.

    `should_retry(self, response: requests.models.Response) ‑> bool`
    :   Specifies conditions for backoff based on the response from the server.
        
        By default, back off on the following HTTP response statuses:
         - 429 (Too Many Requests) indicating rate limiting
         - 500s to handle transient server errors
        
        Unexpected but transient exceptions (connection timeout, DNS resolution failed, etc..) are retried by default.

    `stream_slices(self, *, sync_mode: airbyte_cdk.models.airbyte_protocol.SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) ‑> Iterable[Optional[Mapping[str, Any]]]`
    :   Specifies the slices for this stream. See the stream slicing section of the docs for more information.
        
        :param sync_mode:
        :param cursor_field:
        :param stream_state:
        :return: