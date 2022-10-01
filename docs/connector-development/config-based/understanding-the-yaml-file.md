# Understanding the YAML file

This section deep dives into the components of the [YAML file](./index.md#configuring-the-yaml-file)

## Defining the stream

Streams define the schema of the data to sync, as well as how to read it from the underlying API source.
A stream generally corresponds to a resource within the API. They are analogous to tables for a relational database source.

A stream's schema will can defined as a [JSONSchema](https://json-schema.org/) file in `<source_connector_name>/schemas/<stream_name>.json`.
More information on how to define a stream's schema can be found [here](../cdk-python/schemas.md)

The schema of a stream object is:

```yaml
Stream:
  type: object
  additionalProperties: false
  required:
    - name
    - schema_loader
    - retriever
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    name:
      type: string
    primary_key:
      "$ref": "#/definitions/PrimaryKey"
    schema_loader:
      "$ref": "#/definitions/SchemaLoader"
    retriever:
      "$ref": "#/definitions/Retriever"
    stream_cursor_field:
      type: object
      oneOf:
        - type: string
        - type: array
          items:
            type: string
    transformations:
      type: array
      items:
        "$ref": "#/definitions/RecordTransformation"
    checkpoint_interval:
      type: integer
```

More details on streams and sources can be found in the [basic concepts section](../cdk-python/basic-concepts.md).

## Configuring the data retriever

The data retriever defines how to read the data for a Stream and acts as an orchestrator for the data retrieval flow.

It is described by:

1. Requester: Describes how to submit requests to the API source
2. [Paginator](./pagination.md): Describes how to navigate through the API's pages
3. [Record selector](./record-selector.md): Describes how to extract records from a HTTP response
4. [Stream Slicer](./stream-slicers.md): Describes how to partition the stream, enabling incremental syncs and checkpointing

Each of those components (and their subcomponents) are defined by an explicit interface and one or many implementations.
The developer can choose and configure the implementation they need depending on specifications of the integration they are building against.

Since the `Retriever` is defined as part of the Stream configuration, different Streams for a given Source can use different `Retriever` definitions if needed.

The schema of a retriever object is:

```yaml
Retriever:
  type:
  oneOf:
    - "$ref": "#/definitions/SimpleRetriever"
SimpleRetriever:
  type: object
  additionalProperties: false
  required:
    - name
    - primary_key
    - requester
    - record_selector
    - stream_slicer
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    name:
      type: string
    primary_key:
      "$ref": "#/definitions/PrimaryKey"
    requester:
      "$ref": "#/definitions/Requester"
    record_selector:
      "$ref": "#/definitions/HttpSelector"
    paginator:
      "$ref": "#/definitions/Paginator"
    stream_slicer:
      "$ref": "#/definitions/StreamSlicer"
PrimaryKey:
  type: object
  oneOf:
    - string
    - type: array
      items:
        type: string
    - type: array
      items:
        type: array
        items:
          type: string
```

## Configuring the requester

The `Requester` defines how to prepare HTTP requests to send to the source API.
There is currently only one implementation, the `HttpRequester`, which is defined by

1. A base url: The root of the API source
2. A path: The specific endpoint to fetch data from for a resource
3. The HTTP method: the HTTP method to use (GET or POST)
4. [A request options provider](./request-options.md): Defines the request parameters (query parameters), headers, and request body to set on outgoing HTTP requests
5. [An authenticator](./authentication.md): Defines how to authenticate to the source
6. [An error handler](./error-handling.md): Defines how to handle errors

The schema of a request object is:

```yaml
Requester:
  type: object
  oneOf:
    - "$ref": "#/definitions/HttpRequester"
HttpRequester:
  type: object
  additionalProperties: false
  required:
    - name
    - url_base
    - path
    - http_method
    - request_options_provider
    - authenticator
    - error_handler
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    name:
      type: string
    url_base:
      type: string
      description: "base url"
    path:
      type: string
      description: "path"
    http_method:
      "$ref": "#/definitions/HttpMethod"
    request_options_provider:
      "$ref": "#/definitions/RequestOptionsProvider"
    authenticator:
      "$ref": "#/definitions/Authenticator"
    error_handler:
      "$ref": "#/definitions/ErrorHandler"
HttpMethod:
  type: string
  enum:
    - GET
    - POST
```

## Configuring request parameters and headers

The primary way to set request parameters and headers is to define them as key-value pairs using a `RequestOptionsProvider`.
Other components, such as an `Authenticator` can also set additional request params or headers as needed.

Additionally, some stateful components using a `RequestOption` to configure the options and update the value. Example of such components are [Paginators](#configuring-the-paginator) and [Stream slicers](./advanced-topics.md#stream-slicers).

### Request Options Provider

The primary way to set request options is through the `Requester`'s `RequestOptionsProvider`.
The options can be configured as key value pairs:

Schema:

```yaml
RequestOptionsProvider:
  type: object
  oneOf:
    - "$ref": "#/definitions/InterpolatedRequestOptionsProvider"
InterpolatedRequestOptionsProvider:
  type: object
  additionalProperties: false
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    request_parameters:
      "$ref": "#/definitions/RequestInput"
    request_headers:
      "$ref": "#/definitions/RequestInput"
    request_body_data:
      "$ref": "#/definitions/RequestInput"
    request_body_json:
      "$ref": "#/definitions/RequestInput"
RequestInput:
  type: object
  additionalProperties: true
```

Example:

```yaml
requester:
  type: HttpRequester
  name: "{{ options['name'] }}"
  url_base: "https://api.exchangeratesapi.io/v1/"
  http_method: "GET"
  request_options_provider:
    request_parameters:
      k1: v1
      k2: v2
    request_headers:
      header_key1: header_value1
      header_key2: header_value2
```

It is also possible to configure add a json-encoded body to outgoing requests.

```yaml
requester:
  type: HttpRequester
  name: "{{ options['name'] }}"
  url_base: "https://api.exchangeratesapi.io/v1/"
  http_method: "GET"
  request_options_provider:
    request_body_json:
      key: value
```

### Request Options

Some components can add request options to the requests sent to the API endpoint.

Schema:

```yaml
RequestOption:
  type: object
  additionalProperties: false
  required:
    - inject_into
  properties:
    inject_into:
      "$ref": "#/definitions/RequestOptionType"
    field_name:
      type: string
RequestOptionType:
  type: string
  enum:
    - request_parameter
    - header
    - path
    - body_data
    - body_json
```

## Configuring authentication

The `Authenticator` defines how to configure outgoing HTTP requests to authenticate on the API source.

Schema:

```yaml
Authenticator:
  type: object
  description: "Authenticator type"
  oneOf:
    - "$ref": "#/definitions/OAuth"
    - "$ref": "#/definitions/ApiKeyAuthenticator"
    - "$ref": "#/definitions/BearerAuthenticator"
    - "$ref": "#/definitions/BasicHttpAuthenticator"
```

## Authenticators

### ApiKeyAuthenticator

The `ApiKeyAuthenticator` sets an HTTP header on outgoing requests.
The following definition will set the header "Authorization" with a value "Bearer hello":

Schema:

```yaml
ApiKeyAuthenticator:
  type: object
  additionalProperties: false
  required:
    - header
    - api_token
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    header:
      type: string
    api_token:
      type: string
```

Example:

```yaml
authenticator:
  type: "ApiKeyAuthenticator"
  header: "Authorization"
  token: "Bearer hello"
```

### BearerAuthenticator

The `BearerAuthenticator` is a specialized `ApiKeyAuthenticator` that always sets the header "Authorization" with the value "Bearer {token}".
The following definition will set the header "Authorization" with a value "Bearer hello"

Schema:

```yaml
BearerAuthenticator:
  type: object
  additionalProperties: false
  required:
    - api_token
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    api_token:
      type: string
```

Example:

```yaml
authenticator:
  type: "BearerAuthenticator"
  token: "hello"
```

More information on bearer authentication can be found [here](https://swagger.io/docs/specification/authentication/bearer-authentication/).

### BasicHttpAuthenticator

The `BasicHttpAuthenticator` set the "Authorization" header with a (USER ID/password) pair, encoded using base64 as per [RFC 7617](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#basic_authentication_scheme).
The following definition will set the header "Authorization" with a value "Basic {encoded credentials}"

Schema:

```yaml
BasicHttpAuthenticator:
  type: object
  additionalProperties: false
  required:
    - username
    - password
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    username:
      type: string
    password:
      type: string
```

Example:

```yaml
authenticator:
  type: "BasicHttpAuthenticator"
  username: "hello"
  password: "world"
```

The password is optional. Authenticating with APIs using Basic HTTP and a single API key can be done as:

Example:

```yaml
authenticator:
  type: "BasicHttpAuthenticator"
  username: "hello"
```

### OAuth

OAuth authentication is supported through the `OAuthAuthenticator`, which requires the following parameters:

- token_refresh_endpoint: The endpoint to refresh the access token
- client_id: The client id
- client_secret: The client secret
- refresh_token: The token used to refresh the access token
- scopes (Optional): The scopes to request. Default: Empty list
- token_expiry_date (Optional): The access token expiration date formatted as RFC-3339 ("%Y-%m-%dT%H:%M:%S.%f%z")
- access_token_name (Optional): The field to extract access token from in the response. Default: "access_token".
- expires_in_name (Optional): The field to extract expires_in from in the response. Default: "expires_in"
- refresh_request_body (Optional): The request body to send in the refresh request. Default: None

Schema:

```yaml
OAuth:
  type: object
  additionalProperties: false
  required:
    - token_refresh_endpoint
    - client_id
    - client_secret
    - refresh_token
    - access_token_name
    - expires_in_name
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    token_refresh_endpoint:
      type: string
    client_id:
      type: string
    client_secret:
      type: string
    refresh_token:
      type: string
    scopes:
      type: array
      items:
        type: string
      default: [ ]
    token_expiry_date:
      type: string
    access_token_name:
      type: string
      default: "access_token"
    expires_in_name:
      type: string
      default: "expires_in"
    refresh_request_body:
      type: object
```

Example:

```yaml
authenticator:
  type: "OAuthAuthenticator"
  token_refresh_endpoint: "https://api.searchmetrics.com/v4/token"
  client_id: "{{ config['api_key'] }}"
  client_secret: "{{ config['client_secret'] }}"
  refresh_token: ""
```

## Configuring the Paginator

Given a page size and a pagination strategy, the `DefaultPaginator` will point to pages of results for as long as its strategy returns a `next_page_token`.

Iterating over pages of result is different from iterating over stream slices.
Stream slices have semantic value, for instance, a Datetime stream slice defines data for a specific date range. Two stream slices will have data for different date ranges.
Conversely, pages don't have semantic value. More pages simply means that more records are to be read, without specifying any meaningful difference between the records of the first and later pages.

Schema:

```yaml
Paginator:
  type: object
  oneOf:
    - "$ref": "#/definitions/DefaultPaginator"
```

### Default paginator

The default paginator is defined by

- `page_size_option`: How to specify the page size in the outgoing HTTP request
- `pagination_strategy`: How to compute the next page to fetch
- `page_token_option`: How to specify the next page to fetch in the outgoing HTTP request

Schema:

```yaml
DefaultPaginator:
  type: object
  additionalProperties: false
  required:
    - page_token_option
    - pagination_strategy
    - url_base
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    page_size:
      type: integer
    page_size_option:
      "$ref": "#/definitions/RequestOption"
    page_token_option:
      "$ref": "#/definitions/RequestOption"
    pagination_strategy:
      "$ref": "#/definitions/PaginationStrategy"
    url_base:
      type: string
```

3 pagination strategies are supported

1. Page increment
2. Offset increment
3. Cursor-based

### Pagination Strategies

Schema:

```yaml
PaginationStrategy:
  type: object
  oneOf:
    - "$ref": "#/definitions/CursorPagination"
    - "$ref": "#/definitions/OffsetIncrement"
    - "$ref": "#/definitions/PageIncrement"
```

#### Page increment

When using the `PageIncrement` strategy, the page number will be set as part of the `page_token_option`.

Schema:

```yaml
PageIncrement:
  type: object
  additionalProperties: false
  required:
    - page_size
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    page_size:
      type: integer
```

The following paginator example will fetch 5 records per page, and specify the page number as a request_parameter:

Example:

```yaml
paginator:
  type: "DefaultPaginator"
  page_size_option:
    inject_into: "request_parameter"
    field_name: "page_size"
  pagination_strategy:
    type: "PageIncrement"
    page_size: 5
  page_token:
    inject_into: "request_parameter"
    field_name: "page"
```

If the page contains less than 5 records, then the paginator knows there are no more pages to fetch.
If the API returns more records than requested, all records will be processed.

Assuming the endpoint to fetch data from is `https://cloud.airbyte.com/api/get_data`,
the first request will be sent as `https://cloud.airbyte.com/api/get_data?page_size=5&page=0`
and the second request as `https://cloud.airbyte.com/api/get_data?page_size=5&page=1`,

#### Offset increment

When using the `OffsetIncrement` strategy, the number of records read will be set as part of the `page_token_option`.

Schema:

```yaml
OffsetIncrement:
  type: object
  additionalProperties: false
  required:
    - page_size
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    page_size:
      type: integer
```

The following paginator example will fetch 5 records per page, and specify the offset as a request_parameter:

Example:

```yaml
paginator:
  type: "DefaultPaginator"
  page_size_option:
    inject_into: "request_parameter"
    field_name: "page_size"
  pagination_strategy:
    type: "OffsetIncrement"
    page_size: 5
  page_token:
    field_name: "offset"
    inject_into: "request_parameter"
```

Assuming the endpoint to fetch data from is `https://cloud.airbyte.com/api/get_data`,
the first request will be sent as `https://cloud.airbyte.com/api/get_data?page_size=5&offset=0`
and the second request as `https://cloud.airbyte.com/api/get_data?page_size=5&offset=5`,

#### Cursor

The `CursorPaginationStrategy` outputs a token by evaluating its `cursor_value` string with the following parameters:

- `response`: The decoded response
- `headers`: HTTP headers on the response
- `last_records`: List of records selected from the last response

This cursor value can be used to request the next page of record.

Schema:

```yaml
Schema:

  ```yaml
CursorPaginationStrategy:
  type: object
  additionalProperties: false
  required:
    - cursor_value
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    cursor_value:
      type: string
    stop_condition:
      type: string
    page_size:
      type: integer
```

##### Cursor paginator in request parameters

In this example, the next page of record is defined by setting the `from` request parameter to the id of the last record read:

```yaml
paginator:
  type: "DefaultPaginator"
  <...>
  pagination_strategy:
    type: "CursorPaginationStrategy"
    cursor_value: "{{ last_records[-1]['id'] }}"
  page_token:
    field_name: "from"
    inject_into: "request_parameter"
```

Assuming the endpoint to fetch data from is `https://cloud.airbyte.com/api/get_data`,
the first request will be sent as `https://cloud.airbyte.com/api/get_data`.

Assuming the id of the last record fetched is 1000,
the next request will be sent as `https://cloud.airbyte.com/api/get_data?from=1000`.

##### Cursor paginator in path

Some APIs directly point to the URL of the next page to fetch. In this example, the URL of the next page is extracted from the response headers:

```yaml
paginator:
  type: "DefaultPaginator"
  <...>
  pagination_strategy:
    type: "CursorPaginationStrategy"
    cursor_value: "{{ headers['urls']['next'] }}"
  page_token:
    inject_into: "path"
```

Assuming the endpoint to fetch data from is `https://cloud.airbyte.com/api/get_data`,
the first request will be sent as `https://cloud.airbyte.com/api/get_data`

Assuming the response's next url is `https://cloud.airbyte.com/api/get_data?page=1&page_size=100`,
the next request will be sent as `https://cloud.airbyte.com/api/get_data?page=1&page_size=100`

## Configuring the Record Selector

The record selector is responsible for translating an HTTP response into a list of Airbyte records by extracting records from the response and optionally filtering and shaping records based on a heuristic.

Schema:

```yaml
HttpSelector:
  type: object
  oneOf:
    - "$ref": "#/definitions/RecordSelector"
RecordSelector:
  type: object
  required:
    - extractor
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    extractor:
      "$ref": "#/definitions/RecordExtractor"
    record_filter:
      "$ref": "#/definitions/RecordFilter"
RecordExtractor:
  type: object
  oneOf:
    - "$ref": "#/definitions/DpathExtractor"
```

The current record extraction implementation uses [dpath](https://pypi.org/project/dpath/) to select records from the json-decoded HTTP response.

Schema:

```yaml
DpathExtractor:
  type: object
  additionalProperties: false
  required:
    - field_pointer
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    field_pointer:
      type: array
      items:
        type: string
  RecordFilter:
    type: object
    additionalProperties: false
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      condition:
        type: string
```

### Common recipes:

Here are some common patterns:

#### Selecting the whole response

If the root of the response is an array containing the records, the records can be extracted using the following definition:

```yaml
selector:
  extractor:
    field_pointer: [ ]
```

If the root of the response is a json object representing a single record, the record can be extracted and wrapped in an array.

For example, given a response body of the form

```json
{
  "id": 1
}
```

and a selector

```yaml
selector:
  extractor:
    field_pointer: [ ]
```

The selected records will be

```json
[
  {
    "id": 1
  }
]
```

#### Selecting a field

Given a response body of the form

```
{
  "data": [{"id": 0}, {"id": 1}],
  "metadata": {"api-version": "1.0.0"}
}
```

and a selector

```yaml
selector:
  extractor:
    field_pointer: [ "data" ]
```

The selected records will be

```json
[
  {
    "id": 0
  },
  {
    "id": 1
  }
]
```

#### Selecting an inner field

Given a response body of the form

```json
{
  "data": {
    "records": [
      {
        "id": 1
      },
      {
        "id": 2
      }
    ]
  }
}
```

and a selector

```yaml
selector:
  extractor:
    field_pointer: [ "data", "records" ]
```

The selected records will be

```json
[
  {
    "id": 1
  },
  {
    "id": 2
  }
]
```

### Filtering records

Records can be filtered by adding a record_filter to the selector.
The expression in the filter will be evaluated to a boolean returning true if the record should be included.

In this example, all records with a `created_at` field greater than the stream slice's `start_time` will be filtered out:

```yaml
selector:
  extractor:
    field_pointer: [ ]
  record_filter:
    condition: "{{ record['created_at'] < stream_slice['start_time'] }}"
```

## Configuring the cursor field for incremental syncs

Incremental syncs are supported by using a `DatetimeStreamSlicer` to iterate over a datetime range.

Given a start time, an end time, and a step function, it will partition the interval [start, end] into small windows of the size described by the step.
Note that the `StreamSlicer`'s `cursor_field` must match the `Stream`'s `stream_cursor_field`.

Schema:

```yaml
DatetimeStreamSlicer:
  type: object
  required:
    - start_datetime
    - end_datetime
    - step
    - cursor_field
    - datetime_format
  additional_properties: false
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    start_datetime:
      "$ref": "#/definitions/MinMaxDatetime"
    end_datetime:
      "$ref": "#/definitions/MinMaxDatetime"
    step:
      type: string
    cursor_field:
      type: string
    datetime_format:
      type: string
    start_time_option:
      "$ref": "#/definitions/RequestOption"
    end_time_option:
      "$ref": "#/definitions/RequestOption"
    stream_state_field_start:
      type: string
    stream_state_field_end:
      type: string
    lookback_window:
      type: string
MinMaxDatetime:
  type: object
  required:
    - datetime
  additionalProperties: false
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    datetime:
      type: string
    datetime_format:
      type: string
    min_datetime:
      type: string
    max_datetime:
      type: string
```

More information on the `DatetimeStreamSlicer` can be found in the [advanced topics sections](./notareallink).

## Configuring the check method

The `ConnectionChecker` defines how to test the connection to the integration.

The only implementation as of now is `CheckStream`, which tries to read a record from a specified list of streams and fails if no records could be read.

Schema:

```yaml
ConnectionChecker:
  type: object
  oneOf:
    - "$ref": "#/definitions/CheckStream"
CheckStream:
  type: object
  additionalProperties: false
  required:
    - stream_names
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    stream_names:
      type: array
      items:
        type: string
```

Example:

```yaml
check:
  type: CheckStream
  stream_names: [ "applications" ]
```