# Error Handling

:::warning
When using the "Test" button to run a test sync of the connector, the Connector Builder UI will not retry failed requests. This is done to reduce the amount of waiting time in between test syncs.
:::

Error handlers allow for the connector to decide how to continue fetching data according to the contents of the response from the partner API. Depending on attributes of the response such as status code, text body, or headers, the connector can continue making requests, retry unsuccessful attempts, or fail the sync.

An error handler is made of two parts, "Backoff strategy" and "Response filter". When the conditions of the response filter are met, the connector will proceed with the sync according to behavior specified. See the [Response filter](#response-filter) section for a detailed breakdown of possible response filter actions. In the event of a failed request that needs to be retried, the backoff strategy determines how long the connector should wait before attempting the request again. 

When an error handler is not configured for a stream, the connector will default to retrying requests that received a 429 and 5XX status code in the response 5 times using a 5-second exponential backoff. This default retry behavior is recommended if the API documentation does not specify error handling or retry behavior.

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

The [Intercom API](https://developers.intercom.com/intercom-api-reference/reference/http-responses) is an API that recommends a constant backoff strategy when retrying requests.

### Exponential

When the API documentation recommends that requests be retried after waiting an exponentially increasing amount of time, the "Exponential" backoff strategy should be set on the error handler.

The exponential backoff strategy is similar to constant where the connector waits to retry a request based on a numeric value "Multiplier" defined on the connector. For a backoff strategy with "Multiplier" set to 5 seconds, when the connector receives an API response that should be retried, it will wait 5 seconds before reattempting the request. Upon receiving subsequent failed responses, the connector will wait 10, 20, 40, and 80, permanently stopping after a total of 5 retries.

Note: When no backoff strategy is defined, the connector defaults to using an exponential backoff to retry requests.

#### Example

The [Delighted API](https://app.delighted.com/docs/api#rate-limits) is an API that recommends using an exponential backoff. In this case, the API documentation recommends retrying requests after 2 seconds, 4 seconds, then 8 seconds and so on. 

Although a lot of API documentation does not call out using an exponential backoff, some APIs like the [Posthog API](https://posthog.com/docs/api) mention rate limits that are advantageous to use an exponential backoff. In this case, the rate limit of 240 requests/min should work for most syncs. However, if there is a spike in traffic, then the exponential backoff allows the connector to avoid sending more requests than the endpoint can support.

### Wait time from header

The "Wait time from header" backoff strategy allows the connector to wait before retrying a request based on the value specified in the API response.

<iframe width="640" height="545" src="https://www.loom.com/embed/84b65299b5cd4f83a8e3b6abdfa0ebd2" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>

#### Example

The [Chargebee API](https://apidocs.chargebee.com/docs/api/error-handling) documentation recommends using the `Retry-After` in the response headers to determine when to retry the request.

When running a sync, the connector receives from the Chargebee API a response with a 429 status code and the `Retry-After` header set to 60. The connector interprets the response retrieving that value from the `Retry-After` header and will pause the sync for 60 seconds before retrying.

### Wait until time from header

The "Wait until time from header" backoff strategy allows the connector to wait until a specific time before retrying a request according to the API response.

<iframe width="640" height="562" src="https://www.loom.com/embed/023bc8a5e5464b2fba125f9344e3f02f" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>

#### Example

The [Recurly API](https://recurly.com/developers/api/v2021-02-25/index.html#section/Getting-Started/Limits) is an API that defines a header `X-RateLimit-Reset` which specifies when the request rate limit will be reset. 

Take for example a connector that makes a request at 25/04/2023 01:00:00 GMT and receives a response with a 429 status code and the header `X-RateLimit-Reset` set to 1682413200. This epoch time is equivalent to 25/04/2023 02:00:00 GMT. Using the `X-RateLimit-Reset` header value, the connector will pause the sync for one hour before attempting subsequent requests to the Recurly API.

## Response filter

A response filter should be used when a connector needs to interpret an API response to decide how the sync should proceed. Common use cases for this feature include ignoring error codes to continue fetching data, retrying requests for specific error codes, and stopping a sync based on the response received from the API.

<iframe width="640" height="716" src="https://www.loom.com/embed/dc86147384204156a2b79442a00c0dd3" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>

### Response conditions

The following conditions can be specified on the "Response filter" and are used to determine if attributes of the response match the filter. When more than one of condition is specified, the filter will take action if the response satisfies any of the conditions:
* [If error message matches](#if-error-message-matches)
* [and predicate is fulfilled](#and-predicate-is-fulfilled)
* [and HTTP codes match](#and-http-codes-match)

#### If error message matches

For a response filter that defines the "If error message matches" field, the connector will check if the provided text exists within the text body of the API response. If the text is present, the response filter will carry out the specified action.

##### Example

For the Chargebee API, some endpoints are only available for a specific API version and if an endpoint is unavailable, the response text will contain `"This API operation is not enabled for this site"`. The Airbyte Chargebee integration allows customers to configure which API version to use when retrieving data for a stream. When the connector makes requests to Chargebee using an unsupported version, the response filter will match according to the response text and proceeds based on the "Then execute action".

#### and predicate is fulfilled

This field allows for more granular control over how the response filter matches against attributes of an API response. For a filter that defines the "and predicate is fulfilled" field, the connector evaluates the interpolation expression against an API response's text body or headers.

##### Example

For the Zoom API, the response text body can include a special non-error status codes under the `code` field. An example response text body would look like `{"code": 300}`. The "If error message matches" condition is too broad because there could be record data containing the text "300". Instead, for a response filter defining "and predicate is fulfilled" as `{{ response.code == 300 }}`, during a sync, the predicate expression will be evaluated to true and the connector proceeds based on the "Then execute action".

#### and HTTP codes match

A response filter can specify for the "and HTTP codes match" field a set of numeric HTTP status codes (ex. 200, 404, 500). When receiving an API response, the connector will check to see if the status code of the response is in the provided set of HTTP status codes.

##### Example

The Pocket API emits API responses for rate limiting errors using a 403 error status code. The default error handler interprets 403 errors as non-retryable and will fail the sync when they are encountered. The connector can configures a response filter field "and HTTP status codes" that contains 403 within the set. When a 403 error response from the API is encountered, the connector proceeds based on the "Then execute action"

### Then execute action

If a response from the API matches the predicates of the response filter the connector will continue the sync according to the "Then execute action" definition. This is a list of the actions that a connector can take:
- SUCCESS: The response was successful and the connector will extract records from the response and emit them to a destination. The connector will continue fetching the next set of records from the API.
- RETRY: The response was unsuccessful, but the error is transient and may be successful on subsequent attempts. The request will be retried according to the backoff policy defined on the error handler.
- IGNORE: The response was unsuccessful, but the error should be ignored. The connector will not emit any records for the current response. The connector will continue fetching the next set of records from the API.
- FAIL: The response was unsuccessful and the connector should stop syncing records and indicate that it failed to retrieve the complete set of records.

### Error message

The "Error message" field is used to customize the message that is relayed back to users when the API response matches a response filter that returns an error.

## Multiple error handlers

In the "Error handlers" section of a stream, one or more handlers can be defined. In the case multiple error handlers are specified, the response will be evaluated against each error handler in the order they are defined. The connector will take the action of the first error handler that matches the response and ignore subsequent handlers.
