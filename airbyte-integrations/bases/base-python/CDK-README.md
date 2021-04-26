# Airbyte Connector Development Kit (CDK)
*Last Updated: 26/4/21*

The Airbyte Python CDK is a low-code framework for fast development of Airbyte Specification-compliant connectors.
The CDK is currently only available for HTTP Sources, and is built on top the [Airbyte Specification](https://docs.airbyte.io/architecture/airbyte-specification).
It provides an improved developer experience by providing basic implementation structure and abstracting away
low-level glue boilerplate. The CDK aims to make implementing a Source as simple as possible -
reading the Source's API, and filling in a few Python function should be all that is needed.

This document is a general introduction to the CDK. Readers should be familiar with the above linked Airbyte
Specification before proceeding.

### The Airbyte Specification
As a quick recap, the Airbyte Specification requires an Airbyte Source to support 4 distinct operations:
1. `Spec` - The required configuration in order to interact with the underlying technical system e.g. database
   information, authentication information etc.
2. `Check` - Validate that the provided configuration is valid with sufficient permissions for one to perform all
   required operations on the Source.
3. `Discover` - Discover the Source's schema. This let users select what a subset of the data to sync. Useful
   if users require only a subset of the data.
4. `Read` - Perform the actual syncing process. Data is read from the Source, parsed into `AirbyteRecordMessage`s
   and sent to the Airbyte Destination. Depending on how the Source is implemented, this sync can be incremental
   or a full-refresh.
   
Careful reader will realize one of the core concepts discussed here is the __Source__.

The Source contains one or more __Streams__ (or __Airbyte Streams__). A __Stream__ is the other concept key to
understanding how Airbyte models the data syncing process. A __Stream__ models the logical data groups that make
up the larger __Source__. If the __Source__ is a RDMS, each __Stream__ is a table. Here, each __Stream__ corresponds
to one resource within the API. e.g. a __Stripe Source__ would have have one __Stream__ for `Transactions`, one
for `Charges` and so on.

### The `AbstractSource` Object
This brings us to the CDK's `AbstractSource` object. This represents the just discussed `Source` concept and is
the top-level entrypoint for the 4 methods __Source__s need to implement.

`Spec` and `Check` are the `AbstractSource`'s simplest operations.

`Spec` returns a checked in json schema file specifying the required configuration. The `AbstractSource` looks for
a file named `spec.json` in the module's root by default. Here is an [example](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-exchange-rates/source_exchange_rates/spec.json).

`Check` delegates to the `AbstractSource`'s `check_connection` function. The function's `config` parameter contains
the user-provided configuration, specified in the `spec.json` returned by `Spec`. `check_connection` uses this configuration to validate
access and permissioning. Here is an [example](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-exchange-rates/source_exchange_rates/source.py#L90) from the same Exchange Rates API.

#### The Streams Interface
An `AbstractSource` also owns a set of `Stream`s. This is populated via the `AbstractSource`'s `streams` [function](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/bases/base-python/base_python/cdk/abstract_source.py#L63).
`Discover` and `Read` rely on this populated set.

`Discover` returns an `AirbyteCatalog` representing all the distinct resources the underlying API supports.
Here is the [entrypoint](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/bases/base-python/base_python/cdk/abstract_source.py#L74) for those interested in reading the code.

`Read` creates an in-memory stream reading from each of the `AbstractSource`'s streams. Here is the
[entrypoint](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/bases/base-python/base_python/cdk/abstract_source.py#L90) for those interested.

As the code examples show, the `AbstractSource` delegates to the set of `Stream`s it owns to fulfill both `Discover`
and `Read`. Thus, implementing `AbstractSource`'s `streams` function is required when using the CDK.

A summary of what we've covered so far on how to use the Airbyte CDK:
* A concrete implementation of the `AbstractSource` object is required. 
* This involves,
  1. implementing the `check_connection`function. 
  2. implementing the `streams` function.
  3. placing the above mentioned `spec.json` file in the right place.

### The HTTPStream Object

We've covered how the `AbstractSource` works with the `Stream` interface in order to fulfill the Airbyte
Specification. Although developers are welcome to implement their own object, the CDK saves developers the hassle
of doing so with the `HTTPStream` object. Similar to the `AbstractSource`, creating a `Stream` is a matter
of extending `HTTPStream`, filling in the right functions, and placing a single json file in the right place.

#### The Basic Full-Refresh Stream

Just like any general HTTP request, the basic `HTTPStream` requires a url to perform the request, and instructions
on how to parse the resulting response.

The full request path is broken up into two parts, the base url and the path. This makes it easy for developers
to create a Source-specific base `HTTPStream` class, with the base url filled in, and individual streams for
each available HTTP resource. The [Stripe CDK implementation](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py)
is a reification of this pattern.

The base url is set via the `url_base` property, while the path is set by implementing the abstract `path` function.

The `parse_response` function instructs the stream how to parse the API response. This returns an `Iterable`, whose
elements are each later transformed into an `AirbyteRecordMessage`. API routes that return a single response
generally have a `parse_reponse` function that return a list of just that one response. Routes that return a list,
usually have a `parse_response` function that return the received list with all elements. Pulling the data out
from the response is sufficient, any deserialization is handled by the CDK.

Lastly, the `HTTPStream` requires a JsonSchema of the API's response in order to validate and deserialise the received
data. Most APIs present this in the reference docs. The JsonSchema file 1) must be placed in a directory existing within
the Python module named `schemas` 2) must match the lower snake case name of the corresponding Stream. Here are
[examples](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-stripe/source_stripe/schemas)
from the Stripe API.

These four elements - the `url_base` property, the `path` function, the `parse_response` function and the schema file -
are the bare minimum required to implement the `HTTPStream`, and can be seen in the same [Stripe example](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L38).

This basic implementation gives us a Full-Refresh Airbyte Stream. We say Full-Refresh since the stream does not have
state and will always indiscriminately read all data from the underlying API resource.

#### The Incremental Stream

If possible, developers should try to implement an Incremental Stream. An Incremental Stream takes advantage of the
Airbyte Specification's `AirbyteStateMessage` to read only new data. This is suitable for any API that offers filter/group
query parameters and/or has an ordered field in the response. Some common examples are resource-specific ids, timestamps, or
enumerated types. Although the implementation is slightly more complex (not that much as we will soon see) - the resulting
Stream only reads what is necessary, and is thus far more efficient.

Several new pieces are essential to understand how the incrementality works with the CDK.

First is the `AirbyteStateMessage` and the `HttpStream`'s `cursor_field`. As mentioned, the `AirbyteStateMessage`
persists state between syncs, and allows a new sync to pick up from where the previous sync last finished.
The `cursor_field` is the actual element in the HTTP request used to determine order. The `cursor_field`'s only
practical implication is it tells the CDK the stream supports incremental syncs. Otherwise, it serves as a signpost
for what field is used as a cursor. This field is also commonly used as a direct index into the api response to
create the `AirbyteStateMessage`.

Next is the `get_updated_state` function. For every record processed (as returned by the `parse_response`
function mentioned above), this function helps the CDK figure out the latest state. This allows any sync
jobs to resume from where the sync last stopped, regardless of success or failure. This function typically
compares the state object's and the latest record's cursor field, picking the latest one.

This is paired with the `stream_slices` function. Conceptually, a Stream Slice is the smallest unit of data to be
synced. In the HTTP case, each Slice is equivalent to a HTTP request; indeed the CDK will make one request
per element returned by the `stream_slices` function. A Slice object is not typed, and the developer
is free to include any information necessary to make the request. This function is called when the
`HTTPStream` is first created. Typically, the `stream_slices` function, via inspecting the state object,
generates a Slice for every request to be made.

As an example, suppose an API is able to dispense data hourly. If the last sync was exactly 24 hours ago,
we can either make an API call retrieving all data at once, or make 24 calls each retrieving an hour's
worth of data. In the latter case, the `stream_slices` function, sees that the previous state contains
yesterday timestamp, and returns a list of 24 Slices, each with a different hourly timestamp to be
used when creating request.

Lastly, the `request_params` and `path` functions allow the per-request information contained in a Slice
to be injected into a request. 

#### Secondary Features

The CDK offers other features that make writing HTTP APIs a breeze.

##### Authentication

The CDK support token and OAuth2.0 authentication via the `TokenAuthenticator` and `Oauth2Authenticator` classes
respectively. Both authentication strategies are identical in that they place the api token in the `Authorization`
header. The `OAuth2Authenticator` goes an additional step further and has mechanisms to, given a refresh token,
refresh the current access token. Note that the `OAuth2Authenticator` currently only supports refresh tokens
and not the full OAuth2.0 loop.

Using either authenticator is as simple as passing the created authenticator into the relevant `HTTPStream`
constructor. Here is an [example](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L242) from the Stripe API.

##### Pagination

Most APIs, when facing a large call, tend to return the results in pages. The CDK accommodates paging
via the `next_page_token` function. This function is meant to extract the next page token from the latest
response. The CDK will continue making requests as long as the `next_page_function` continues returning
items. This can then be used in the `request_params` method to page through API responses. Here is an
[example](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L41) from the Stripe API.

##### Rate Limiting

The CDK, by default, will conduct exponential backoff on the HTTP code 429 and unexpected exceptions,
and fail after 5 tries.

Retries are governed by the `should_retry` and the `backoff_time` methods. Override these methods to
customise retry behavior.

Note that Airbyte will always attempt to make as many requests as possible and only slow down if there are
errors. It is not currently possible to specify a rate limit Airbyte should adhere to when making requests.

### Practical Tips
* Airbyte recommends using the CDK template generator to develop with the CDK. The generated template
  created all the required scaffolding, with convenient TODOs, to allow developers to truly focus on
  implementing the API.

### Examples

Those interested in getting their hands dirty can check out implemeneted APIs:
* [Exchange Rates API](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-exchange-rates/source_exchange_rates/source.py) (Incremental)
* [Stripe API](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py) (Incremental and Full-Refresh)
* [Slack API](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-slack/source_slack/source.py) (Incremental and Full-Refresh)

### Coming Soon
* Full OAuth 2.0 support
* Airbyte Java HTTP CDK
* CDK for other protocols
* General CDK for Destinations
