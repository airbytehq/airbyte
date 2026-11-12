# Error Handling

:::warning
When using the "Test" button to run a test sync of the connector, the Connector Builder UI will not retry failed requests. This is done to reduce the amount of waiting time in between test syncs.
:::

Error handlers allow the connector to decide how to continue fetching data according to the contents of the response from the partner API. Depending on attributes of the response such as status code, text body, or headers, the connector can continue making requests, retry unsuccessful attempts, or fail the sync.

The Connector Builder provides three types of error handlers to handle different scenarios:

- **Default Error Handler**: The most commonly used error handler that provides configurable backoff strategies and response filters
- **Composite Error Handler**: Allows chaining multiple error handlers together, where each handler is evaluated in sequence until one matches
- **Custom Error Handler**: For advanced use cases requiring custom code implementations

When an error handler is not configured for a stream, the connector will default to retrying requests that received a 429 and 5XX status code in the response 5 times using a 5-second exponential backoff. This default retry behavior is recommended if the API documentation does not specify error handling or retry behavior.

Refer to the documentation of the API you are building a connector for to determine how to handle response errors. There can either be a dedicated section listing expected error responses (ex. [Delighted](https://app.delighted.com/docs/api#http-status-codes)) or API endpoints will list their error responses individually (ex. [Intercom](https://developers.intercom.com/intercom-api-reference/reference/listcompaniesforacontact)). There is also typically a section on rate limiting that summarizes how rate limits are communicated in the response and when to retry.

## Error Handler Types

### Default Error Handler

The Default Error Handler is the most commonly used error handler and provides comprehensive configuration options for handling API errors. It consists of three main components:

1. **Backoff strategies**: Determine how long to wait before retrying a failed request
2. **Response filters**: Define which responses should be retried, ignored, or cause the sync to fail
3. **Max retries**: Set the maximum number of retry attempts (default: 5)

### Composite Error Handler

The Composite Error Handler allows you to chain multiple error handlers together. When a response is received, each error handler in the list is evaluated in sequence until one matches the response. This is useful when you need different error handling logic for different types of failures.

Example use cases:
- Handle rate limiting differently from server errors
- Apply different retry strategies based on specific error codes
- Combine custom error handling with standard retry logic

### Custom Error Handler

The Custom Error Handler allows you to implement custom error handling logic through code. This requires specifying a fully-qualified class name that implements the custom error handling behavior. This option is for advanced users who need error handling logic that cannot be achieved through the standard configuration options.

## Backoff Strategies

The API documentation will usually cover when to reattempt a failed request that is retryable. This is often through a `429 Too Many Requests` response status code, but it can vary for different APIs. The following backoff strategies are supported in the connector builder:

- [Constant](#constant)
- [Exponential](#exponential)
- [Wait time from header](#wait-time-from-header)
- [Wait until time from header](#wait-until-time-from-header)

### Constant

When the API documentation recommends that requests be retried after waiting a constant amount of time, the "Constant" backoff strategy should be set on the error handler.

**Configuration:**
- **Backoff time in seconds** (required): The fixed number of seconds to wait before retrying. This can be a numeric value or an interpolated string referencing your connector configuration.

**Examples:**
- Fixed value: `30` (wait 30 seconds)
- Decimal value: `30.5` (wait 30.5 seconds)  
- From config: `"{{ config['backoff_time'] }}"` (use value from connector configuration)

#### Example

The [Intercom API](https://developers.intercom.com/intercom-api-reference/reference/http-responses) is an API that recommends a constant backoff strategy when retrying requests.

### Exponential

When the API documentation recommends that requests be retried after waiting an exponentially increasing amount of time, the "Exponential" backoff strategy should be set on the error handler.

The exponential backoff strategy uses a multiplicative factor to determine wait times. The interval is calculated as `factor * 2^attempt_count`. For a backoff strategy with factor set to 5 seconds, when the connector receives an API response that should be retried, it will wait 5 seconds before reattempting the request. Upon receiving subsequent failed responses, the connector will wait 10, 20, 40, and 80 seconds, permanently stopping after a total of 5 retries.

**Configuration:**
- **Factor** (optional): Multiplicative constant applied on each retry. Default value is 5. This can be a numeric value or an interpolated string.

**Examples:**
- Default: `5` (uses 5-second base factor)
- Custom: `10` (uses 10-second base factor)
- From config: `"{{ config['retry_factor'] or 5 }}"` (use config value or default to 5)

Note: When no backoff strategy is defined, the connector defaults to using an exponential backoff to retry requests.

#### Example

The [Delighted API](https://app.delighted.com/docs/api#rate-limits) is an API that recommends using an exponential backoff. In this case, the API documentation recommends retrying requests after 2 seconds, 4 seconds, then 8 seconds and so on.

Although a lot of API documentation does not call out using an exponential backoff, some APIs like the [Posthog API](https://posthog.com/docs/api) mention rate limits that are advantageous to use an exponential backoff. In this case, the rate limit of 240 requests/min should work for most syncs. However, if there is a spike in traffic, then the exponential backoff allows the connector to avoid sending more requests than the endpoint can support.

### Wait Time Extracted from Response Header

The "Wait Time Extracted from Response Header" backoff strategy allows the connector to wait before retrying a request based on the value specified in the API response header.

**Configuration:**
- **Response header name** (required): The name of the response header that contains the wait time value
- **Extraction regex** (optional): Optional regex to extract the wait time value from the header. The regex should define a capture group for the wait time
- **Max waiting time in seconds** (optional): Maximum time to wait before giving up. If the header value exceeds this limit, the stream will stop

**Examples:**
- Header name: `"Retry-After"`
- Regex: `"([-+]?\\d+)"` (extracts numeric value)
- Max wait: `3600` (don't wait more than 1 hour)

#### Example

The [Chargebee API](https://apidocs.chargebee.com/docs/api/error-handling) documentation recommends using the `Retry-After` in the response headers to determine when to retry the request.

When running a sync, the connector receives from the Chargebee API a response with a 429 status code and the `Retry-After` header set to 60. The connector interprets the response retrieving that value from the `Retry-After` header and will pause the sync for 60 seconds before retrying.

### Wait Until Time Defined in Response Header

The "Wait Until Time Defined in Response Header" backoff strategy allows the connector to wait until a specific time before retrying a request according to the API response header. This strategy extracts a timestamp from the response header and waits until that time before retrying.

**Configuration:**
- **Response header** (required): The name of the response header that contains the timestamp when retrying is allowed
- **Minimum wait time** (optional): Minimum time to wait before retrying, even if the header suggests a shorter wait
- **Extraction regex** (optional): Optional regex to extract the timestamp value from the header. The regex should define a capture group for the timestamp

**Examples:**
- Header name: `"X-RateLimit-Reset"`
- Min wait: `10` (always wait at least 10 seconds)
- Regex: `"([-+]?\\d+)"` (extracts numeric timestamp)

#### Example

The [Recurly API](https://recurly.com/developers/api/v2021-02-25/index.html#section/Getting-Started/Limits) is an API that defines a header `X-RateLimit-Reset` which specifies when the request rate limit will be reset.

Take for example a connector that makes a request at 25/04/2023 01:00:00 GMT and receives a response with a 429 status code and the header `X-RateLimit-Reset` set to 1682413200. This epoch time is equivalent to 25/04/2023 02:00:00 GMT. Using the `X-RateLimit-Reset` header value, the connector will pause the sync for one hour before attempting subsequent requests to the Recurly API.

## Response Filters

A response filter should be used when a connector needs to interpret an API response to decide how the sync should proceed. Response filters allow you to define specific conditions that determine whether a response should be retried, ignored, treated as successful, cause the sync to fail, or be treated as rate-limited.

Multiple response filters can be configured for a single error handler. When using multiple filters, they are applied sequentially and the response will be processed according to the first filter that matches.

### Action

If a response from the API matches the conditions of the response filter, the connector will continue the sync according to the configured action. The following actions are available:

- **SUCCESS**: The response was successful and the connector will extract records from the response and emit them to a destination. The connector will continue fetching the next set of records from the API.
- **RETRY**: The response was unsuccessful, but the error is transient and may be successful on subsequent attempts. The request will be retried according to the backoff strategy defined on the error handler.
- **IGNORE**: The response was unsuccessful, but the error should be ignored. The connector will not emit any records for the current response. The connector will continue fetching the next set of records from the API.
- **FAIL**: The response was unsuccessful and the connector should stop syncing records and indicate that it failed to retrieve the complete set of records.
- **RATE_LIMITED**: The response indicates that the connector has been rate limited. This action triggers the backoff strategy and retry logic specifically designed for rate limiting scenarios.

### Failure Types

When using the FAIL action, you can optionally specify a failure type to categorize the error:

- **system_error**: Indicates a system-level error that is not related to user configuration
- **config_error**: Indicates an error caused by incorrect user configuration
- **transient_error**: Indicates a temporary error that might resolve itself

### Error Message

The "Error message" field allows you to customize the message that is relayed back to users when the API response matches a response filter. This field supports interpolation, allowing you to include dynamic information from the response in the error message.

**Configuration:**

- **Error message**: Custom error message to display when the filter matches

**Interpolation context available:**

- `config`: Access to connector configuration values
- `response`: Access to the API response content
- `headers`: Access to response headers

#### Example

- `"API rate limit exceeded. Please try again later."`
- `"Invalid API key: {{ response.error_message }}"`
- `"Request failed with status {{ response.status_code }}: {{ response.message }}"`

### Error Message Substring

For a response filter that defines the "Error Message Substring" field, the connector will check if the provided text exists within the text body of the API response. If the text is present, the response filter will carry out the specified action.

**Configuration:**
- **Error message substring**: The text to search for in the response body

**Example:**
- Value: `"This API operation is not enabled for this site"`

#### Example

For the Chargebee API, some endpoints are only available for a specific API version and if an endpoint is unavailable, the response text will contain `"This API operation is not enabled for this site"`. The Airbyte Chargebee integration allows customers to configure which API version to use when retrieving data for a stream. When the connector makes requests to Chargebee using an unsupported version, the response filter will match according to the response text and proceeds based on the configured action.

### HTTP Codes

A response filter can specify a set of numeric HTTP status codes to match against. When receiving an API response, the connector will check if the status code of the response is in the provided set of HTTP status codes.

**Configuration:**
- **HTTP codes**: An array of HTTP status codes to match against

**Examples:**
- `[420, 429]` (match rate limiting codes)
- `[500]` (match server errors)
- `[403, 404]` (match specific client errors)

#### Example

The Pocket API emits API responses for rate limiting errors using a 403 error status code. The default error handler interprets 403 errors as non-retryable and will fail the sync when they are encountered. The connector can configure a response filter with HTTP status codes that contains 403. When a 403 error response from the API is encountered, the connector proceeds based on the configured action.

### Predicate

This field allows for more granular control over how the response filter matches against attributes of an API response. The predicate is an interpolation expression that is evaluated against the API response's text body or headers.

**Configuration:**
- **Predicate**: An interpolation expression that evaluates to true or false based on the response content

**Examples:**
- `"{{ 'Too many requests' in response }}"` (check if text exists in response)
- `"{{ response.code == 300 }}"` (check specific field value)
- `"{{ 'error_code' in response and response['error_code'] == 'ComplexityException' }}"` (complex condition)

#### Example

For the Zoom API, the response text body can include a special non-error status codes under the `code` field. An example response text body would look like `{"code": 300}`. The "Error message contains" condition is too broad because there could be record data containing the text "300". Instead, for a response filter defining the predicate as `{{ response.code == 300 }}`, during a sync, the predicate expression will be evaluated to true and the connector proceeds based on the configured action.

## Advanced Error Handling Configuration

### Max Retry Count

The "Max retry count" field allows you to configure the maximum number of times a request will be retried before giving up. This applies to all retryable responses (those with RETRY or RATE_LIMITED actions).

**Configuration:**
- **Max retry count**: Maximum number of retry attempts (default: 5)

**Examples:**
- `5` (default - retry up to 5 times)
- `0` (no retries)
- `10` (retry up to 10 times for persistent issues)

### Composite Error Handler Usage

When using a Composite Error Handler, you can chain multiple error handlers together. Each error handler in the list is evaluated in sequence until one matches the response. This allows for sophisticated error handling workflows:

1. **First handler**: Check for specific API error codes and handle them with custom logic
2. **Second handler**: Handle rate limiting with appropriate backoff
3. **Third handler**: Default handler for all other errors

### Custom Error Handler Implementation

For advanced use cases that cannot be handled through configuration, you can implement a Custom Error Handler. This requires:

1. **Class name**: Fully-qualified name of your custom error handler class
2. **Implementation**: The class must implement the required error handler interface
3. **Parameters**: Optional parameters to pass to your custom implementation

**Example:**
- Class name: `"source_myapi.components.MyCustomErrorHandler"`

## Common Error Handling Patterns

### Rate Limiting

Most APIs implement rate limiting. Here's a recommended approach:

1. **Use appropriate backoff strategy**: 
   - "Wait Until Time Defined in Response Header" if the API provides `Retry-After` header
   - "Exponential backoff" for APIs without specific guidance
2. **Configure response filter**:
   - HTTP codes: `[429]`
   - Action: `RATE_LIMITED`
3. **Set reasonable max retries**: Usually 5-10 attempts

### Server Errors

For temporary server issues:

1. **Use exponential backoff**: Gives the server time to recover
2. **Configure response filter**:
   - HTTP codes: `[500, 502, 503, 504]`
   - Action: `RETRY`
3. **Limit retries**: Usually 3-5 attempts to avoid long delays

### API-Specific Errors

For known API error conditions:

1. **Use predicate or error message matching**: Target specific error responses
2. **Choose appropriate action**:
   - `IGNORE`: For expected errors that should not stop the sync
   - `FAIL`: For configuration errors that require user intervention
   - `SUCCESS`: For responses that contain valid data despite error status codes

### Troubleshooting

If your error handler is not working as expected:

1. **Check the order**: Error handlers are evaluated in sequence
2. **Verify conditions**: Ensure your filter conditions match the actual API responses
3. **Test with simple conditions**: Start with HTTP status codes before adding complex predicates
4. **Use custom error messages**: Include response details to understand what's happening
5. **Check logs**: Review sync logs to see which error handlers are being triggered
