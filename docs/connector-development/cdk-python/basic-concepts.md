# Basic Concepts

## The Airbyte Specification

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

A core concept discussed here is the **Source**.

The Source contains one or more **Streams** \(or **Airbyte Streams**\). A **Stream** is the other concept key to understanding how Airbyte models the data syncing process. A **Stream** models the logical data groups that make up the larger **Source**. If the **Source** is a RDMS, each **Stream** is a table. In a REST API setting, each **Stream** corresponds to one resource within the API. e.g. a **Stripe Source** would have have one **Stream** for `Transactions`, one for `Charges` and so on.

## The `Source` class

Airbyte provides abstract base classes which make it much easier to perform certain categories of tasks e.g: `HttpStream` makes it easy to create HTTP API-based streams. However, if those do not satisfy your use case \(for example, if you're pulling data from a relational database\), you can always directly implement the Airbyte Protocol by subclassing the CDK's `Source` class.

The `Source` class implements the `Spec` operation by looking for a file named `spec.yaml` (or `spec.json`) in the module's root by default. This is expected to be a json schema file that specifies the required configuration. Here is an [example](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-exchange-rates/source_exchange_rates/spec.yaml) from the Exchange Rates source.

Note that while this is the most flexible way to implement a source connector, it is also the most toilsome as you will be required to manually manage state, input validation, correctly conforming to the Airbyte Protocol message formats, and more. We recommend using a subclass of `Source` unless you cannot fulfill your use case otherwise.

## The `AbstractSource` Object

`AbstractSource` is a more opinionated implementation of `Source`. It implements `Source`'s 4 methods as follows:

`Check` delegates to the `AbstractSource`'s `check_connection` function. The function's `config` parameter contains the user-provided configuration, specified in the `spec.yaml` returned by `Spec`. `check_connection` uses this configuration to validate access and permissioning. Here is an [example](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-exchange-rates/source_exchange_rates/source.py#L90) from the same Exchange Rates API.

### The `Stream` Abstract Base Class

An `AbstractSource` also owns a set of `Stream`s. This is populated via the `AbstractSource`'s `streams` [function](https://github.com/airbytehq/airbyte-python-cdk/blob/main//airbyte_cdk/sources/abstract_source.py#L63). `Discover` and `Read` rely on this populated set.

`Discover` returns an `AirbyteCatalog` representing all the distinct resources the underlying API supports. Here is the [entrypoint](https://github.com/airbytehq/airbyte-python-cdk/blob/main//airbyte_cdk/sources/abstract_source.py#L74) for those interested in reading the code. See [schemas](https://github.com/airbytehq/airbyte/tree/21116cad97f744f936e503f9af5a59ed3ac59c38/docs/contributing-to-airbyte/python/concepts/schemas.md) for more information on how to declare the schema of a stream.

`Read` creates an in-memory stream reading from each of the `AbstractSource`'s streams. Here is the [entrypoint](https://github.com/airbytehq/airbyte-python-cdk/blob/main//airbyte_cdk/sources/abstract_source.py#L90) for those interested.

As the code examples show, the `AbstractSource` delegates to the set of `Stream`s it owns to fulfill both `Discover` and `Read`. Thus, implementing `AbstractSource`'s `streams` function is required when using the CDK.

A summary of what we've covered so far on how to use the Airbyte CDK:

- A concrete implementation of the `AbstractSource` object is required.
- This involves,
  1. implementing the `check_connection`function.
  2. Creating the appropriate `Stream` classes and returning them in the `streams` function.
  3. placing the above mentioned `spec.yaml` file in the right place.

## HTTP Streams

We've covered how the `AbstractSource` works with the `Stream` interface in order to fulfill the Airbyte Specification. Although developers are welcome to implement their own object, the CDK saves developers the hassle of doing so in the case of HTTP APIs with the [`HTTPStream`](http-streams.md) object.
