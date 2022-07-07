Module airbyte_cdk.sources.streams.http.http
============================================

Classes
-------

`HttpStream(authenticator: Union[requests.auth.AuthBase, airbyte_cdk.sources.streams.http.auth.core.HttpAuthenticator] = None)`
:   Base abstract class for an Airbyte Stream using the HTTP protocol. Basic building block for users building an Airbyte source for a HTTP API.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.streams.core.Stream
    * abc.ABC

    ### Descendants

    * airbyte_cdk.sources.declarative.retrievers.simple_retriever.SimpleRetriever
    * airbyte_cdk.sources.streams.http.http.HttpSubStream

    ### Class variables

    `page_size: Optional[int]`
    :

    ### Instance variables

    `authenticator: airbyte_cdk.sources.streams.http.auth.core.HttpAuthenticator`
    :

    `cache_filename`
    :   Override if needed. Return the name of cache file

    `http_method: str`
    :   Override if needed. See get_request_data/get_request_json if using POST/PUT/PATCH.

    `max_retries: Optional[int]`
    :   Override if needed. Specifies maximum amount of retries for backoff policy. Return None for no limit.

    `raise_on_http_errors: bool`
    :   Override if needed. If set to False, allows opting-out of raising HTTP code exception.

    `retry_factor: float`
    :   Override if needed. Specifies factor for backoff policy.

    `url_base: str`
    :   :return: URL base for the  API endpoint e.g: if you wanted to hit https://myapi.com/v1/some_entity then this should return "https://myapi.com/v1/"

    `use_cache`
    :   Override if needed. If True, all records will be cached.

    ### Methods

    `backoff_time(self, response: requests.models.Response) ‑> Optional[float]`
    :   Override this method to dynamically determine backoff time e.g: by reading the X-Retry-After header.
        
        This method is called only if should_backoff() returns True for the input request.
        
        :param response:
        :return how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff
        to the default backoff behavior (e.g using an exponential algorithm).

    `get_error_display_message(self, exception: BaseException) ‑> Optional[str]`
    :   Retrieves the user-friendly display message that corresponds to an exception.
        This will be called when encountering an exception while reading records from the stream, and used to build the AirbyteTraceMessage.
        
        The default implementation of this method only handles HTTPErrors by passing the response to self.parse_response_error_message().
        The method should be overriden as needed to handle any additional exception types.
        
        :param exception: The exception that was raised
        :return: A user-friendly message that indicates the cause of the error

    `next_page_token(self, response: requests.models.Response) ‑> Optional[Mapping[str, Any]]`
    :   Override this method to define a pagination strategy.
        
        The value returned from this method is passed to most other methods in this class. Use it to form a request e.g: set headers or query params.
        
        :return: The token for the next page from the input response object. Returning None means there are no more pages to read in this response.

    `parse_response(self, response: requests.models.Response, *, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> Iterable[Mapping]`
    :   Parses the raw response object into a list of records.
        By default, this returns an iterable containing the input. Override to parse differently.
        :param response:
        :param stream_state:
        :param stream_slice:
        :param next_page_token:
        :return: An iterable containing the parsed response

    `parse_response_error_message(self, response: requests.models.Response) ‑> Optional[str]`
    :   Parses the raw response object from a failed request into a user-friendly error message.
        By default, this method tries to grab the error message from JSON responses by following common API patterns. Override to parse differently.
        
        :param response:
        :return: A user-friendly message that indicates the cause of the error

    `path(self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> str`
    :   Returns the URL path for the API endpoint e.g: if you wanted to hit https://myapi.com/v1/some_entity then this should return "some_entity"

    `request_body_data(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> Union[Mapping, str, ForwardRef(None)]`
    :   Override when creating POST/PUT/PATCH requests to populate the body of the request with a non-JSON payload.
        
        If returns a ready text that it will be sent as is.
        If returns a dict that it will be converted to a urlencoded form.
        E.g. {"key1": "value1", "key2": "value2"} => "key1=value1&key2=value2"
        
        At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.

    `request_body_json(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> Optional[Mapping]`
    :   Override when creating POST/PUT/PATCH requests to populate the body of the request with a JSON payload.
        
        At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.

    `request_cache(self) ‑> <module 'vcr.cassette' from '/Users/alex/code/airbyte/airbyte-integrations/connectors/source-github/.venv/lib/python3.9/site-packages/vcr/cassette.py'>`
    :   Builds VCR instance.
        It deletes file everytime we create it, normally should be called only once.
        We can't use NamedTemporaryFile here because yaml serializer doesn't work well with empty files.

    `request_headers(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> Mapping[str, Any]`
    :   Override to return any non-auth headers. Authentication headers will overwrite any overlapping headers returned from this method.

    `request_kwargs(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> Mapping[str, Any]`
    :   Override to return a mapping of keyword arguments to be used when creating the HTTP request.
        Any option listed in https://docs.python-requests.org/en/latest/api/#requests.adapters.BaseAdapter.send for can be returned from
        this method. Note that these options do not conflict with request-level options such as headers, request params, etc..

    `request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> MutableMapping[str, Any]`
    :   Override this method to define the query parameters that should be set on an outgoing HTTP request given the inputs.
        
        E.g: you might want to define query parameters for paging if next_page_token is not None.

    `should_retry(self, response: requests.models.Response) ‑> bool`
    :   Override to set different conditions for backoff based on the response from the server.
        
        By default, back off on the following HTTP response statuses:
         - 429 (Too Many Requests) indicating rate limiting
         - 500s to handle transient server errors
        
        Unexpected but transient exceptions (connection timeout, DNS resolution failed, etc..) are retried by default.

`HttpSubStream(parent: airbyte_cdk.sources.streams.http.http.HttpStream, **kwargs)`
:   Base abstract class for an Airbyte Stream using the HTTP protocol. Basic building block for users building an Airbyte source for a HTTP API.
    
    :param parent: should be the instance of HttpStream class

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.streams.http.http.HttpStream
    * airbyte_cdk.sources.streams.core.Stream
    * abc.ABC

    ### Class variables

    `page_size: Optional[int]`
    :