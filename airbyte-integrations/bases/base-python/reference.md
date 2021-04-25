Module base_python
==================
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Sub-modules
-----------
* base_python.catalog_helpers
* base_python.cdk
* base_python.client
* base_python.entrypoint
* base_python.integration
* base_python.logger
* base_python.schema_helpers
* base_python.source

Classes
-------

`AbstractSource()`
:   Abstract base class for an Airbyte Source. Consumers should implement any abstract methods
in this class to create an Airbyte Specification compliant Source.

    ### Ancestors (in MRO)

    * base_python.integration.Source
    * base_python.integration.Integration
    * abc.ABC

    ### Instance variables

    `name: str`
    :   Source name

    ### Methods

    `check(self, logger: base_python.logger.AirbyteLogger, config: Mapping[str, Any]) ‑> airbyte_protocol.models.airbyte_protocol.AirbyteConnectionStatus`
    :   Implements the Check Connection operation from the Airbyte Specification. See https://docs.airbyte.io/architecture/airbyte-specification.

    `check_connection(self, logger: base_python.logger.AirbyteLogger, config: Mapping[str, Any]) ‑> Tuple[bool, Union[Any, NoneType]]`
    :   :param config: The user-provided configuration as specified by the source's spec. This usually contains information required to check connection e.g. tokens, secrets and keys etc.
        :return: A tuple of (boolean, error). If boolean is true, then the connection check is successful and we can connect to the underlying data
        source using the provided configuration.
        Otherwise, the input config cannot be used to connect to the underlying data source, and the "error" object should describe what went wrong.
        The error object will be cast to string to display the problem to the user.

    `discover(self, logger: base_python.logger.AirbyteLogger, config: Mapping[str, Any]) ‑> airbyte_protocol.models.airbyte_protocol.AirbyteCatalog`
    :   Implements the Discover operation from the Airbyte Specification. See https://docs.airbyte.io/architecture/airbyte-specification.

    `read(self, logger: base_python.logger.AirbyteLogger, config: Mapping[str, Any], catalog: airbyte_protocol.models.airbyte_protocol.ConfiguredAirbyteCatalog, state: MutableMapping[str, Any] = None) ‑> Iterator[airbyte_protocol.models.airbyte_protocol.AirbyteMessage]`
    :   Implements the Read operation from the Airbyte Specification. See https://docs.airbyte.io/architecture/airbyte-specification.

    `streams(self, config: Mapping[str, Any]) ‑> List[base_python.cdk.streams.core.Stream]`
    :   :param config: The user-provided configuration as specified by the source's spec. Any stream construction related operation should happen here.
        :return: A list of the streams in this source connector.

`AirbyteLogger()`
:

    ### Methods

    `debug(self, message)`
    :

    `error(self, message)`
    :

    `exception(self, message)`
    :

    `fatal(self, message)`
    :

    `info(self, message)`
    :

    `log(self, level, message)`
    :

    `log_by_prefix(self, message, default_level)`
    :

    `trace(self, message)`
    :

    `warn(self, message)`
    :

`AirbyteSpec(spec_string)`
:

    ### Static methods

    `from_file(file: str)`
    :

`BaseClient(**kwargs)`
:   Base client for API

    ### Ancestors (in MRO)

    * base_python.client.StreamStateMixin
    * abc.ABC

    ### Class variables

    `schema_loader_class`
    :   JSONSchema loader from package resources

    ### Instance variables

    `streams: Generator[airbyte_protocol.models.airbyte_protocol.AirbyteStream, NoneType, NoneType]`
    :   List of available streams

    ### Methods

    `health_check(self) ‑> Tuple[bool, str]`
    :   Check if service is up and running

    `read_stream(self, stream: airbyte_protocol.models.airbyte_protocol.AirbyteStream) ‑> Generator[Dict[str, Any], NoneType, NoneType]`
    :   Yield records from stream

`BaseSource()`
:   Base source that designed to work with clients derived from BaseClient

    ### Ancestors (in MRO)

    * base_python.integration.Source
    * base_python.integration.Integration

    ### Class variables

    `client_class: Type[base_python.client.BaseClient]`
    :

    ### Instance variables

    `name: str`
    :   Source name

    ### Methods

    `check(self, logger: base_python.logger.AirbyteLogger, config: Mapping[str, Any]) ‑> airbyte_protocol.models.airbyte_protocol.AirbyteConnectionStatus`
    :   Check connection

    `discover(self, logger: base_python.logger.AirbyteLogger, config: Mapping[str, Any]) ‑> airbyte_protocol.models.airbyte_protocol.AirbyteCatalog`
    :   Discover streams

`CatalogHelper()`
:

    ### Static methods

    `coerce_catalog_as_full_refresh(catalog: airbyte_protocol.models.airbyte_protocol.AirbyteCatalog) ‑> airbyte_protocol.models.airbyte_protocol.AirbyteCatalog`
    :   Updates the sync mode on all streams in this catalog to be full refresh

`Destination()`
:

    ### Ancestors (in MRO)

    * base_python.integration.Integration

`HttpAuthenticator()`
:   Base abstract class for various HTTP Authentication strategies. Authentication strategies are generally
expected to provide security credentials via HTTP headers.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * base_python.cdk.streams.auth.core.NoAuth
    * base_python.cdk.streams.auth.jwt.JWTAuthenticator
    * base_python.cdk.streams.auth.oauth.Oauth2Authenticator
    * base_python.cdk.streams.auth.token.TokenAuthenticator

    ### Methods

    `get_auth_header(self) ‑> Mapping[str, Any]`
    :   :return: A dictionary containing all the necessary headers to authenticate.

`HttpStream(authenticator: base_python.cdk.streams.auth.core.HttpAuthenticator = <base_python.cdk.streams.auth.core.NoAuth object>)`
:   Base abstract class for an Airbyte Stream using the HTTP protocol. Basic building block for users building an Airbyte source for a HTTP API.

    ### Ancestors (in MRO)

    * base_python.cdk.streams.core.Stream
    * abc.ABC

    ### Instance variables

    `authenticator: base_python.cdk.streams.auth.core.HttpAuthenticator`
    :

    `http_method: str`
    :   Override if needed. See get_request_data if using POST.

    `url_base: str`
    :   :return: URL base for the  API endpoint e.g: if you wanted to hit https://myapi.com/v1/some_entity then this should return "https://myapi.com/v1/"

    ### Methods

    `backoff_time(self, response: requests.models.Response) ‑> Union[float, NoneType]`
    :   Override this method to dynamically determine backoff time e.g: by reading the X-Retry-After header.
        
        This method is called only if should_backoff() returns True for the input request.
        
        :return how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff
        to the default backoff behavior (e.g using an exponential algorithm).

    `next_page_token(self, response: requests.models.Response) ‑> Union[Mapping[str, Any], NoneType]`
    :   Override this method to define a pagination strategy.
        
        The value returned from this method is passed to most other methods in this class. Use it to form a request e.g: set headers or query params.
        
        :return: The token for the next page from the input response object. Returning None means there are no more pages to read in this response.

    `parse_response(self, response: requests.models.Response, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> Iterable[Mapping]`
    :   Parses the raw response object into a list of records.
        By default, this returns an iterable containing the input. Override to parse differently.
        :param response:
        :return: An iterable containing the parsed response

    `path(self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> str`
    :   Returns the URL path for the API endpoint e.g: if you wanted to hit https://myapi.com/v1/some_entity then this should return "some_entity"

    `request_body_json(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> Union[Mapping, NoneType]`
    :   TODO make this possible to do for non-JSON APIs
        Override when creating POST requests to populate the body of the request with a JSON payload.

    `request_headers(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> Mapping[str, Any]`
    :   Override to return any non-auth headers. Authentication headers will overwrite any overlapping headers returned from this method.

    `request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) ‑> MutableMapping[str, Any]`
    :   Override this method to define the query parameters that should be set on an outgoing HTTP request given the inputs.
        
        E.g: you might want to define query parameters for paging if next_page_token is not None.

    `should_retry(self, response: requests.models.Response) ‑> bool`
    :   Override to set different conditions for backoff based on the response from the server.
        
        By default, back off on the following HTTP response statuses:
         - 429 (Too Many Requests) indicating rate limiting
         - 500s to handle transient server errors
        
        Unexpected but transient exceptions (connection timeout, DNS resolution failed, etc..) are retried by default.

`Integration()`
:

    ### Descendants

    * base_python.integration.Destination
    * base_python.integration.Source

    ### Static methods

    `read_config(config_path: str) ‑> <module 'json' from '/Users/davinchia/.pyenv/versions/3.7.9/lib/python3.7/json/__init__.py'>`
    :

    `write_config(config: <module 'json' from '/Users/davinchia/.pyenv/versions/3.7.9/lib/python3.7/json/__init__.py'>, config_path: str)`
    :

    ### Methods

    `check(self, logger: base_python.logger.AirbyteLogger, config: <module 'json' from '/Users/davinchia/.pyenv/versions/3.7.9/lib/python3.7/json/__init__.py'>) ‑> airbyte_protocol.models.airbyte_protocol.AirbyteConnectionStatus`
    :   Tests if the input configuration can be used to successfully connect to the integration e.g: if a provided Stripe API token can be used to connect
        to the Stripe API.

    `configure(self, config: <module 'json' from '/Users/davinchia/.pyenv/versions/3.7.9/lib/python3.7/json/__init__.py'>, temp_dir: str) ‑> <module 'json' from '/Users/davinchia/.pyenv/versions/3.7.9/lib/python3.7/json/__init__.py'>`
    :   Persist config in temporary directory to run the Source job

    `discover(self, logger: base_python.logger.AirbyteLogger, config: <module 'json' from '/Users/davinchia/.pyenv/versions/3.7.9/lib/python3.7/json/__init__.py'>) ‑> airbyte_protocol.models.airbyte_protocol.AirbyteCatalog`
    :   Returns an AirbyteCatalog representing the available streams and fields in this integration. For example, given valid credentials to a
        Postgres database, returns an Airbyte catalog where each postgres table is a stream, and each table column is a field.

    `read_catalog(self, catalog_path: str) ‑> airbyte_protocol.models.airbyte_protocol.ConfiguredAirbyteCatalog`
    :

    `read_state(self, state_path: str) ‑> Dict[str, <built-in function any>]`
    :

    `spec(self, logger: base_python.logger.AirbyteLogger) ‑> airbyte_protocol.models.airbyte_protocol.ConnectorSpecification`
    :   Returns the spec for this integration. The spec is a JSON-Schema object describing the required configurations (e.g: username and password)
        required to run this integration.

`Source()`
:

    ### Ancestors (in MRO)

    * base_python.integration.Integration

    ### Descendants

    * base_python.cdk.abstract_source.AbstractSource
    * base_python.source.BaseSource

    ### Methods

    `read(self, logger: base_python.logger.AirbyteLogger, config: <module 'json' from '/Users/davinchia/.pyenv/versions/3.7.9/lib/python3.7/json/__init__.py'>, catalog: airbyte_protocol.models.airbyte_protocol.ConfiguredAirbyteCatalog, state_path: Dict[str, <built-in function any>]) ‑> Generator[airbyte_protocol.models.airbyte_protocol.AirbyteMessage, NoneType, NoneType]`
    :   Returns a generator of the AirbyteMessages generated by reading the source with the given configuration, catalog, and state.

`Stream()`
:   Base abstract class for an Airbyte Stream. Makes no assumption of the Stream's underlying transport protocol.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * base_python.cdk.streams.http.HttpStream

    ### Class variables

    `logger`
    :

    ### Instance variables

    `cursor_field: Union[str, List[str]]`
    :   Override to return the default cursor field used by this stream e.g: an API entity might always use created_at as the cursor field.
        :return: The name of the field used as a cursor. If the cursor is nested, return an array consisting of the path to the cursor.

    `name: str`
    :   :return: Stream name. By default this is the implementing class name, but it can be overridden as needed.

    `source_defined_cursor: bool`
    :   Return False if the cursor can be configured by the user.

    `state_checkpoint_interval: Union[int, NoneType]`
    :   Decides how often to checkpoint state (i.e: emit a STATE message). E.g: if this returns a value of 100, then state is persisted after reading
        100 records, then 200, 300, etc.. A good default value is 1000 although your mileage may vary depending on the underlying data source.
        
        Checkpointing a stream avoids re-reading records in the case a sync is failed or cancelled.
        
        return None if state should not be checkpointed e.g: because records returned from the underlying data source are not returned in
        ascending order with respect to the cursor field. This can happen if the source does not support reading records in ascending order of
        created_at date (or whatever the cursor is). In those cases, state must only be saved once the full stream has been read.

    `supports_incremental: bool`
    :   :return: True if this stream supports incrementally reading data

    ### Methods

    `as_airbyte_stream(self) ‑> airbyte_protocol.models.airbyte_protocol.AirbyteStream`
    :

    `get_json_schema(self) ‑> Mapping[str, Any]`
    :   :return: A dict of the JSON schema representing this stream.
        
        The default implementation of this method looks for a JSONSchema file with the same name as this stream's "name" property.
        Override as needed.

    `get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any])`
    :   Override to extract state from the latest record. Needed to implement incremental sync.
        
        Inspects the latest record extracted from the data source and the current state object and return an updated state object.
        
        For example: if the state object is based on created_at timestamp, and the current state is {'created_at': 10}, and the latest_record is
        {'name': 'octavia', 'created_at': 20 } then this method would return {'created_at': 20} to indicate state should be updated to this object.
        
        :param current_stream_state: The stream's current state object
        :param latest_record: The latest record extracted from the stream
        :return: An updated state object

    `read_records(self, sync_mode: airbyte_protocol.models.airbyte_protocol.SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, <built-in function any>] = None, stream_state: Mapping[str, Any] = None) ‑> Iterable[Mapping[str, Any]]`
    :   This method should be overridden by subclasses to read records based on the inputs

    `stream_slices(self, sync_mode: airbyte_protocol.models.airbyte_protocol.SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) ‑> Iterable[Union[Mapping[str, <built-in function any>], NoneType]]`
    :   Override to define the slices for this stream. See the stream slicing section of the docs for more information.
        
        :param stream_state:
        :return:

`TokenAuthenticator(token: str, auth_method: str = 'Bearer', auth_header: str = 'Authorization')`
:   Base abstract class for various HTTP Authentication strategies. Authentication strategies are generally
expected to provide security credentials via HTTP headers.

    ### Ancestors (in MRO)

    * base_python.cdk.streams.auth.core.HttpAuthenticator
    * abc.ABC
