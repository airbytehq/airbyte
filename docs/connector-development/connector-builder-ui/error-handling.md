# Error Handling

Error handlers allow for the connection to decide how to continue fetching data according to the contents of the response from the partner API. Depending on attributes of the response such as status code, text body, or headers, the connection can continue making requests, retry unsuccessful attempts, or fail the sync.

An error handler is made of two parts, "Backoff strategy" and "Response filter". When the conditions of the response filter are met, the connection will proceed with the sync according to behavior specified. See the [Response filter](#response-filter) section for a detailed breakdown of possible response filter actions. In the event of a failed request that needs to be retried, the backoff strategy determines how long the connection should wait before attempting the request again. 

When an error handler is not implemented for a stream, the connection will default to retrying requests that received a 429 and 5XX status code in the response 5 times using a 5-second exponential backoff. This default retry behavior is recommended if an API's documentation does not specify error handling or retry behavior.

Refer to the documentation of the API you are building a connector for to determine how to handle response errors. There can either be a dedicated section listing expected error responses (ex. [Delighted](https://app.delighted.com/docs/api#http-status-codes)) or API endpoints will list their error responses individually (ex. [Intercom](https://developers.intercom.com/intercom-api-reference/reference/listcompaniesforacontact)). There is also typically a section on rate limiting that summarizes how rate limits are communicated in the response and when to retry.

## Backoff strategies

The API documentation will usually cover when to reattempt a failed request that is retryable. This is often through a `429 Too Many Requests` response status code, but it can vary for different APIs. The following backoff strategies are supported in the connector builder:
* [Constant](#constant)
* [Exponential](#exponential)
* [Wait time from header](#wait-time-from-header)
* [Wait until time from header](#wait-until-time-from-header)

### Constant

When the API documentation recommends that requests be retried after waiting a constant amount of time, the "Constant" backoff strategy should be set on the error handler.

#### Example

The [Intercom API]() is an API that recommends a constant backoff strategy when retrying requests.

### Exponential

The exponential backoff strategy is similar to constant where the connection waits to retry a request based on a numeric value defined on the connector. When the API documentation recommends that requests be retried after waiting an exponentially increasing amount of time, the "Exponential" backoff strategy should be set on the error handler.

Note: When no backoff strategy is defined, the connection defaults to using an exponential backoff to retry requests.

#### Example

The [Delighted API](https://app.delighted.com/docs/api#rate-limits) is an API that recommends using an exponential backoff. In this case, the API documentation recommends retrying requests after 2 seconds, then 4 seconds, and so on. 

Although a lot of API documentation does not call out using an exponential backoff, some APIs like the [Posthog API](https://posthog.com/docs/api) mention rate limits that are advantageous to use an exponential backoff. In this case, the rate limit of 240 requests/min should work for most syncs. However, if there is a spike in traffic, then the exponential backoff allows the connection to avoid sending more requests than the endpoint can support.

### Wait time from header

The "Wait time from header" backoff strategy allows the connection to wait before retrying a request based on the value specified in the API response.

#### Example

The [Chargebee API](https://apidocs.chargebee.com/docs/api/error-handling) documentation recommends using the `Retry-After` in the response headers to determine when to retry the request.

When running a sync, if the API responds with a 429 error response, the connection will interpret the response and check the `Retry-After` header to see when to attempt the request again.

### Wait until time from header

The "Wait until time from header" backoff strategy allows the connection to wait until a specific time before retrying a request according to the API response.

#### Example

The [Recurly API](https://recurly.com/developers/api/v2021-02-25/index.html#section/Getting-Started/Limits) is an API that defines a header `X-RateLimit-Reset` which specifies when the request rate limit will be reset. 

During a sync, if the connection receives a 429 error response, it will read the `X-RateLimit-Reset` header and pause making further requests to the Recurly API until after the time specified in the header.

## Response filter

A response filter should be used when a connection needs to interpret an API response to decide how the sync should proceed. Common use cases for this feature include ignoring error codes to continue fetching data, retrying requests for specific error codes, and stopping a sync based on the response received from the API.

### Response conditions

The following conditions can be specified on the "Response filter" and are used to determine if attributes of the response match the filter:
- "If error message matches": The filter will match the provided text against the text body of the API response.
- "and predicate is fulfilled": This allows for more granular control over how the filter matches by evaluating an interpolation expression against the API response.
- "and HTTP codes match": The filter will check to see if the HTTP status code of the response is in the provided set of HTTP status codes.

### Then execute action

If a response from the API matches the predicates of the response filter the connection will continue the sync according to the "Then execute action" definition. This is a list of the actions that a connection can take:
- SUCCESS: The response was successful and the connection will continue fetching the next set of records from the API.
- RETRY: The response was unsuccessful, but the error is transient and may be successful on subsequent attempts. The request will be retried according to the backoff policy defined on the error handler.
- IGNORE: The response was unsuccessful, but the error should be ignored and the connection can continue fetching the next set of records from the API.
- FAIL: The response was unsuccessful and the sync should stop syncing records and indicate that it failed to retrieve the complete set of records.

### Error message

The "Error message" field is used to customize the message that is relayed back to users when the API response matches a response filter that returns an error.

## Multiple error handlers

In the "Error handlers" section of a stream, one or more handlers can be defined. In the case multiple error handlers are specified, the response will be evaluated against each error handler in the order they are defined. The connection will take the action of the first error handler that matches the response and ignore subsequent handlers.