# Request Options

The primary way to set request parameters and headers is to define them as key-value pairs using a `RequestOptionsProvider`.
Other components, such as an `Authenticator` can also set additional request params or headers as needed.

Additionally, some stateful components use a `RequestOption` to configure the options and update the value. Example of such components are [Paginators](./pagination.md) and [DatetimeBasedCursors](./incremental-syncs.md#DatetimeBasedCursor).

## Request Options Provider

The primary way to set request options is through the `Requester`'s `RequestOptionsProvider`.
The options can be configured as key value pairs:

Schema:

```yaml
RequestOptionsProvider:
  type: object
  anyOf:
    - "$ref": "#/definitions/InterpolatedRequestOptionsProvider"
InterpolatedRequestOptionsProvider:
  type: object
  additionalProperties: true
  properties:
    "$parameters":
      "$ref": "#/definitions/$parameters"
    request_parameters:
      "$ref": "#/definitions/RequestInput"
    request_headers:
      "$ref": "#/definitions/RequestInput"
    request_body_data:
      "$ref": "#/definitions/RequestInput"
    request_body_json:
      "$ref": "#/definitions/RequestInput"
```

Example:

```yaml
requester:
  type: HttpRequester
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
  url_base: "https://api.exchangeratesapi.io/v1/"
  http_method: "GET"
  request_options_provider:
    request_body_json:
      key: value
```

### Request Option Component

Some components can be configured to inject additional request options to the requests sent to the API endpoint.

Schema:

```yaml
RequestOption:
  description: A component that specifies the key field and where in the request a component's value should be inserted into.
  type: object
  required:
    - type
    - inject_into
  properties:
    type:
      type: string
      enum: [RequestOption]
    inject_into:
      enum:
        - request_parameter
        - header
        - body_data
        - body_json
  oneOf:
    - properties:
      field_name:
        type: string
        description: The key where the value will be injected. Used for non-nested injection
      field_path:
        type: array
          items: 
            type: string
          description: For body_json injection, specifies the nested path to the inject values. Particularly useful for GraphQL queries where values need to be injected into the variables object.
```

### GraphQL request injection

For `body_json` injections, the `field_path` property is used to provide a list of strings representing a path to a nested key to inject. This is particularly useful when working with GraphQL APIs. GraphQL queries typically accept variables as a separate object in the request body, allowing values to be parameterized without string manipulation of the query itself. As an example, to inject a page size option into a GraphQL query, you might need to provide a `limit` key in the request's `variables` as:

```yaml
page_size_option:
  request_option:
    type: RequestOption
    inject_into: body_json
    field_path:
      - variables
      - limit
```

This would inject the following value in the request body:

```json
{ "variables": { "limit": value }}
```

Here's an example of what your final request might look like:

```json
{
  "query": "query($limit: Int) { users(limit: $limit) { id name } }",
  "variables": {
    "limit": 10
  }
}
```

:::note
Nested key injection is ONLY available for `body_json` injection. All other injection types use the top-level `field_name` instead.
The `field_name` field is slated to be deprecated in favor of `field_path` in the future.
:::

### Request Path

As an alternative to adding various options to the request being sent, some components can be configured to
modify the HTTP path of the API endpoint being accessed.

Schema:

```yaml
RequestPath:
  description: A component that specifies where in the request path a component's value should be inserted into.
  type: object
  required:
    - type
  properties:
    type:
      type: string
      enum: [RequestPath]
```

## Authenticators

It is also possible for authenticators to set request parameters or headers as needed.
For instance, the `BearerAuthenticator` will always set the `Authorization` header.

More details on the various authenticators can be found in the [authentication section](authentication.md).

## Paginators

The `DefaultPaginator` can optionally set request options through the `page_size_option` and the `page_token_option`.
The respective values can be set on the outgoing HTTP requests by specifying where it should be injected.

The following example will set the "page" request parameter value to the page to fetch, and the "page_size" request parameter to 5:

```yaml
paginator:
  type: "DefaultPaginator"
  page_size_option:
    type: "RequestOption"
    inject_into: request_parameter
    field_name: page_size
  pagination_strategy:
    type: "PageIncrement"
    page_size: 5
  page_token:
    type: "RequestOption"
    inject_into: "request_parameter"
    field_name: "page"
```

More details on paginators can be found in the [pagination section](./pagination.md).

## Incremental syncs

The `DatetimeBasedCursor` can optionally set request options through the `start_time_option` and `end_time_option` fields.
The respective values can be set on the outgoing HTTP requests by specifying where it should be injected.

The following example will set the "created[gte]" request parameter value to the start of the time window, and "created[lte]" to the end of the time window.

```yaml
incremental_sync:
  type: DatetimeBasedCursor
  start_datetime: "2021-02-01T00:00:00.000000+0000",
  end_datetime: "2021-03-01T00:00:00.000000+0000",
  step: "P1D"
  start_time_option:
    type: "RequestOption"
    field_name: "created[gte]"
    inject_into: "request_parameter"
  end_time_option:
    type: "RequestOption"
    field_name: "created[lte]"
    inject_into: "request_parameter"
```

More details on incremental syncs can be found in the [incremental syncs section](./incremental-syncs.md).

## More readings

- [Requester](./requester.md)
- [Pagination](./pagination.md)
- [Incremental Syncs](./incremental-syncs.md)
