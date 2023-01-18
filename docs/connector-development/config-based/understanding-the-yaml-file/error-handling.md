# Error handling

By default, only server errors (HTTP 5XX) and too many requests (HTTP 429) will be retried up to 5 times with exponential backoff.
Other HTTP errors will result in a failed read.

Other behaviors can be configured through the `Requester`'s `error_handler` field.

Schema:

```yaml
  ErrorHandler:
    type: object
    description: "Error handler"
    anyOf:
      - "$ref": "#/definitions/DefaultErrorHandler"
      - "$ref": "#/definitions/CompositeErrorHandler"
```

## Default error handler

Schema:

```yaml
  DefaultErrorHandler:
    type: object
    required:
      - max_retries
    additionalProperties: true
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      response_filters:
        type: array
        items:
          "$ref": "#/definitions/HttpResponseFilter"
      max_retries:
        type: integer
        default: 5
      backoff_strategies:
        type: array
        items:
          "$ref": "#/definitions/BackoffStrategy"
        default: [ ]
```

## Defining errors

### From status code

Response filters can be used to define how to handle requests resulting in responses with a specific HTTP status code.
For instance, this example will configure the handler to also retry responses with 404 error:

Schema:

```yaml
  HttpResponseFilter:
    type: object
    required:
      - action
    additionalProperties: true
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      action:
        "$ref": "#/definitions/ResponseAction"
      http_codes:
        type: array
        items:
          type: integer
        default: [ ]
      error_message_contains:
        type: string
      predicate:
        type: string
  ResponseAction:
    type: string
    enum:
      - SUCCESS
      - FAIL
      - IGNORE
      - RETRY
```

Example:

```yaml
requester:
  <...>
  error_handler:
    response_filters:
        - http_codes: [ 404 ]
          action: RETRY
```

Response filters can be used to specify HTTP errors to ignore.
For instance, this example will configure the handler to ignore responses with 404 error:

```yaml
requester:
  <...>
  error_handler:
    response_filters:
        - http_codes: [ 404 ]
          action: IGNORE
```

### From error message

Errors can also be defined by parsing the error message.
For instance, this error handler will ignore responses if the error message contains the string "ignorethisresponse"

```yaml
requester:
  <...>
  error_handler:
    response_filters:
        - error_message_contain: "ignorethisresponse"
          action: IGNORE
```

This can also be done through a more generic string interpolation strategy with the following parameters:

- response: the decoded response

This example ignores errors where the response contains a "code" field:

```yaml
requester:
  <...>
  error_handler:
    response_filters:
        - predicate: "{{ 'code' in response }}"
          action: IGNORE
```

The error handler can have multiple response filters.
The following example is configured to ignore 404 errors, and retry 429 errors:

```yaml
requester:
  <...>
  error_handler:
    response_filters:
        - http_codes: [ 404 ]
          action: IGNORE
        - http_codes: [ 429 ]
          action: RETRY
```

## Backoff Strategies

The error handler supports a few backoff strategies, which are described in the following sections.

Schema:

```yaml
  BackoffStrategy:
    type: object
    anyOf:
      - "$ref": "#/definitions/ExponentialBackoffStrategy"
      - "$ref": "#/definitions/ConstantBackoffStrategy"
      - "$ref": "#/definitions/WaitTimeFromHeader"
      - "$ref": "#/definitions/WaitUntilTimeFromHeader"
```

### Exponential backoff

This is the default backoff strategy. The requester will backoff with an exponential backoff interval

Schema:

```yaml
  ExponentialBackoffStrategy:
    type: object
    additionalProperties: true
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      factor:
        type: integer
        default: 5
```

### Constant Backoff

When using the `ConstantBackoffStrategy` strategy, the requester will backoff with a constant interval.

Schema:

```yaml
  ConstantBackoffStrategy:
    type: object
    additionalProperties: true
    required:
      - backoff_time_in_seconds
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      backoff_time_in_seconds:
        type: number
```

### Wait time defined in header

When using the `WaitTimeFromHeader`, the requester will backoff by an interval specified in the response header.
In this example, the requester will backoff by the response's "wait_time" header value:

Schema:

```yaml
  WaitTimeFromHeader:
    type: object
    additionalProperties: true
    required:
      - header
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      header:
        type: string
      regex:
        type: string
```

Example:

```yaml
requester:
  <...>
  error_handler:
    <...>
    backoff_strategies:
        - type: "WaitTimeFromHeader"
          header: "wait_time"
```

Optionally, a regular expression can be configured to extract the wait time from the header value.

Example:

```yaml
requester:
  <...>
  error_handler:
    <...>
    backoff_strategies:
        - type: "WaitTimeFromHeader"
          header: "wait_time"
          regex: "[-+]?\d+"
```

### Wait until time defined in header

When using the `WaitUntilTimeFromHeader` backoff strategy, the requester will backoff until the time specified in the response header.
In this example, the requester will wait until the time specified in the "wait_until" header value:

Schema:

```yaml
  WaitUntilTimeFromHeader:
    type: object
    additionalProperties: true
    required:
      - header
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      header:
        type: string
      regex:
        type: string
      min_wait:
        type: number
```

Example:

```yaml
requester:
  <...>
  error_handler:
    <...>
    backoff_strategies:
        - type: "WaitUntilTimeFromHeader"
          header: "wait_until"
          regex: "[-+]?\d+"
          min_wait: 5
```

The strategy accepts an optional regular expression to extract the time from the header value, and a minimum time to wait.

## Advanced error handling

The error handler can have multiple backoff strategies, allowing it to fallback if a strategy cannot be evaluated.
For instance, the following defines an error handler that will read the backoff time from a header, and default to a constant backoff if the wait time could not be extracted from the response:

Example:

```yaml
requester:
  <...>
  error_handler:
    <...>
    backoff_strategies:
        - type: "WaitTimeFromHeader"
          header: "wait_time"
            - type: "ConstantBackoff"
              backoff_time_in_seconds: 5
```

The `requester` can be configured to use a `CompositeErrorHandler`, which sequentially iterates over a list of error handlers, enabling different retry mechanisms for different types of errors.

In this example, a constant backoff of 5 seconds, will be applied if the response contains a "code" field, and an exponential backoff will be applied if the error code is 403:

Schema:

```yaml
  CompositeErrorHandler:
    type: object
    required:
      - error_handlers
    additionalProperties:
      "$options":
        "$ref": "#/definitions/$options"
      error_handlers:
        type: array
        items:
          "$ref": "#/definitions/ErrorHandler"
```

Example:

```yaml
requester:
  <...>
  error_handler:
    type: "CompositeErrorHandler"
    error_handlers:
      - response_filters:
          - predicate: "{{ 'code' in response }}"
            action: RETRY
        backoff_strategies:
          - type: "ConstantBackoffStrategy"
            backoff_time_in_seconds: 5
      - response_filters:
          - http_codes: [ 403 ]
            action: RETRY
        backoff_strategies:
          - type: "ExponentialBackoffStrategy"
```

## More readings

- [Requester](./requester.md)
