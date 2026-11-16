# Requester

The `Requester` defines how to prepare HTTP requests to send to the source API.
There is currently only one implementation, the `HttpRequester`, which is defined by

1. A base url: The root of the API source
2. A path: The specific endpoint to fetch data from for a resource
3. The HTTP method: the HTTP method to use (GET or POST)
4. [A request options provider](./request-options.md#request-options-provider): Defines the request parameters (query parameters), headers, and request body to set on outgoing HTTP requests
5. [An authenticator](./authentication.md): Defines how to authenticate to the source
6. [An error handler](./error-handling.md): Defines how to handle errors

The schema of a requester object is:

```yaml
Requester:
  type: object
  anyOf:
    - "$ref": "#/definitions/HttpRequester"
HttpRequester:
  type: object
  additionalProperties: true
  required:
    - url_base
    - path
  properties:
    "$parameters":
      "$ref": "#/definitions/$parameters"
    url_base:
      type: string
      description: "base url"
    path:
      type: string
      description: "path"
    http_method:
      "$ref": "#/definitions/HttpMethod"
      default: "GET"
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

Additionally, some stateful components use a `RequestOption` to configure the options and update the value. Example of such components are [Paginators](./pagination.md) and [Partition routers](./partition-router.md).

## More readings

- [Request options](./request-options.md)
