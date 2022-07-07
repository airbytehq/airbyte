Module airbyte_cdk.sources.declarative.requesters.requester
===========================================================

Classes
-------

`HttpMethod(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   An enumeration.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `GET`
    :

    `POST`
    :

`Requester()`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * airbyte_cdk.sources.declarative.requesters.http_requester.HttpRequester

    ### Instance variables

    `cache_filename: str`
    :   Return the name of cache file

    `max_retries: Optional[int]`
    :   Specifies maximum amount of retries for backoff policy. Return None for no limit.

    `raise_on_http_errors: bool`
    :   If set to False, allows opting-out of raising HTTP code exception.

    `retry_factor: float`
    :   Specifies factor for backoff policy.

    `use_cache: bool`
    :   If True, all records will be cached.

    ### Methods

    `backoff_time(self, response: requests.models.Response) ‑> Optional[float]`
    :   Dynamically determine backoff time e.g: by reading the X-Retry-After header.
        
        This method is called only if should_backoff() returns True for the input request.
        
        :param response:
        :return how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff
        to the default backoff behavior (e.g using an exponential algorithm).

    `get_authenticator(self) ‑> requests.auth.AuthBase`
    :   Specifies the authenticator to use when submitting requests

    `get_method(self) ‑> airbyte_cdk.sources.declarative.requesters.requester.HttpMethod`
    :   Specifies the HTTP method to use

    `get_path(self, *, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any], next_page_token: Mapping[str, Any]) ‑> str`
    :   Returns the URL path for the API endpoint e.g: if you wanted to hit https://myapi.com/v1/some_entity then this should return "some_entity"

    `get_url_base(self) ‑> str`
    :   :return: URL base for the  API endpoint e.g: if you wanted to hit https://myapi.com/v1/some_entity then this should return "https://myapi.com/v1/"

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
    :   Return any non-auth headers. Authentication headers will overwrite any overlapping headers returned from this method.

    `request_kwargs(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> Mapping[str, Any]`
    :   Returns a mapping of keyword arguments to be used when creating the HTTP request.
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