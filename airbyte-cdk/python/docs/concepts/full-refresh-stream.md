# The Basic Full-Refresh Stream

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

You can also dynamically set your schema. See the [schema docs](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/bases/base-python/docs/schemas.md) for more information.

These four elements - the `url_base` property, the `path` function, the `parse_response` function and the schema file -
are the bare minimum required to implement the `HTTPStream`, and can be seen in the same [Stripe example](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L38).

This basic implementation gives us a Full-Refresh Airbyte Stream. We say Full-Refresh since the stream does not have
state and will always indiscriminately read all data from the underlying API resource.