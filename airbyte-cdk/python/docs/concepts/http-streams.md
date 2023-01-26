# HTTP API-based Connectors

The CDK offers base classes that greatly simplify writing HTTP API-based connectors. Some of the most useful features include helper functionality for: 
* Authentication (basic auth, Oauth2, or any custom auth method)
* Pagination
* Handling rate limiting with static or dynamic backoff timing

All these features have sane off-the-shelf defaults but are completely customizable depending on your use case. They can also be combined with other stream features described in the [full refresh streams](./full-refresh-stream.md) and [incremental streams](incremental-stream.md) sections.

## Overview of HTTP Streams
Just like any general HTTP request, the basic `HTTPStream` requires a url to perform the request, and instructions
on how to parse the resulting response.

The full request path is broken up into two parts, the base url and the path. This makes it easy for developers
to create a Source-specific base `HTTPStream` class, with the base url filled in, and individual streams for
each available HTTP resource. The [Stripe CDK implementation](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py)
is a reification of this pattern.

The base url is set via the `url_base` property, while the path is set by implementing the abstract `path` function.

The `parse_response` function instructs the stream how to parse the API response. This returns an `Iterable`, whose
elements are each later transformed into an `AirbyteRecordMessage`. API routes whose response contains a single record
generally have a `parse_reponse` function that return a list of just that one response. Routes that return a list,
usually have a `parse_response` function that return the received list with all elements. Pulling the data out
from the response is sufficient, any deserialization is handled by the CDK.

Lastly, the `HTTPStream` must describe the schema of the records it outputs using JsonSchema.
The simplest way to do this is by placing a `.json` file per stream in the `schemas` directory in the generated python module.
The name of the `.json` file must match the lower snake case name of the corresponding Stream. Here are
[examples](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-stripe/source_stripe/schemas)
from the Stripe API.

You can also dynamically set your schema. See the [schema docs](./full-refresh-stream.md#defining-the-streams-schema) for more information.

These four elements - the `url_base` property, the `path` function, the `parse_response` function and the schema file -
are the bare minimum required to implement the `HTTPStream`, and can be seen in the same [Stripe example](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L38).

This basic implementation gives us a Full-Refresh Airbyte Stream. We say Full-Refresh since the stream does not have
state and will always indiscriminately read all data from the underlying API resource.

## Authentication

The CDK supports Basic and OAuth2.0 authentication via the `TokenAuthenticator` and `Oauth2Authenticator` classes
respectively. Both authentication strategies are identical in that they place the api token in the `Authorization`
header. The `OAuth2Authenticator` goes an additional step further and has mechanisms to, given a refresh token,
refresh the current access token. Note that the `OAuth2Authenticator` currently only supports refresh tokens
and not the full OAuth2.0 loop.

Using either authenticator is as simple as passing the created authenticator into the relevant `HTTPStream`
constructor. Here is an [example](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L242) from the Stripe API.

## Pagination

Most APIs, when facing a large call, tend to return the results in pages. The CDK accommodates paging
via the `next_page_token` function. This function is meant to extract the next page "token" from the latest
response. The contents of a "token" are completely up to the developer: it can be an ID, a page number, a partial URL etc.. The CDK will continue making requests as long as the `next_page_token` function. The CDK will continue making requests as long as the `next_page_token` continues returning
non-`None` results. This can then be used in the `request_params` and other methods in `HttpStream` to page through API responses. Here is an
[example](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L41) from the Stripe API.

## Rate Limiting

The CDK, by default, will conduct exponential backoff on the HTTP code 429 and any 5XX exceptions,
and fail after 5 tries.

Retries are governed by the `should_retry` and the `backoff_time` methods. Override these methods to
customise retry behavior. Here is an [example](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-slack/source_slack/source.py#L72) from the Slack API.

Note that Airbyte will always attempt to make as many requests as possible and only slow down if there are
errors. It is not currently possible to specify a rate limit Airbyte should adhere to when making requests.

### Stream Slicing

When implementing [stream slicing](incremental-stream.md#streamstream_slices) in an `HTTPStream` each Slice is equivalent to a HTTP request; the stream will make one request per element returned by the `stream_slices` function. The current slice being read is passed into every other method in `HttpStream` e.g: `request_params`, `request_headers`, `path`, etc.. to be injected into a request. This allows you to dynamically determine the output of the `request_params`, `path`, and other functions to read the input slice and return the appropriate value. 

### Caching

When we are dealing with streams that depend on the results of another stream, we can use caching to write the data of the parent stream to a file in order to use this data when the child stream synchronizes, rather than performing a full HTTP request again. We can turn on caching by overriding use_cache property, and use HttpSubStream class as base class of child stream.

### Network Adapter Keyword arguments

If you need to set any network-adapter keyword args on the outgoing HTTP requests such as `allow_redirects`, `stream`, `verify`, `cert`, etc..
override the `request_kwargs` method. Any option listed in [BaseAdapter.send](https://docs.python-requests.org/en/latest/api/#requests.adapters.BaseAdapter.send) can 
be returned as a keyword argument. 

## Stream Availability

The CDK defines an `AvailabilityStrategy` for a stream, which is used to perform the `check_availability` method. This method checks whether
the stream is available before performing `read_records`.

For HTTP streams, a `HttpAvailabilityStrategy` is defined, which attempts to read the first record of the stream, and excepts
a dictionary of known error codes and associated reasons, `reasons_for_unavailable_status_codes`. By default, this list contains only
`requests.status_codes.FORBIDDEN` (403), with an associated error message that tells the user that they are likely missing permissions associated with that stream.

You can use this `HttpAvailabilityStrategy` in your `HttpStream` by adding the following property to your stream class:

```python
    def availability_strategy(self) -> Optional[AvailabilityStrategy]:
        return HttpAvailabilityStrategy()
```

You can also subclass `HttpAvailabilityStrategy` to override the list of known errors to except more error codes and inform the user how to resolve errors specific to your connector or stream.
