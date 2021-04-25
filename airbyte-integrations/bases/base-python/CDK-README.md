# Airbyte Connector Development Kit (CDK)

The Airbyte CDK is a low-code Python framework for fast development of Airbyte Specification-compliant
HTTP Sources. The CDK is built on top the [Airbyte Specification's](https://docs.airbyte.io/architecture/airbyte-specification)
and provides an improved developer experience by providing basic implementation structure and abstracting away
low-level glue boilerplate. The CDK's aims to make implementing a Source as simple as possible -
reading the Source's API, and filling in a few Python function should be all that is needed.

This document is a general introduction to the CDK. Readers should be familiar with the above linked Airbyte
Specification between proceeding.

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
   
Careful reader will realise one of the core concepts discussed here is the __Source__.

The Source contains one or more __Streams__ (or __Airbyte Streams__). A __Stream__ is the other concept key to
understanding how Airbyte models the data syncing process. A __Stream__ models the logical data groups that make
up the larger __Source__. If the __Source__ is a RDMS, each __Stream__ is a table. Here, each __Stream__ corresponds
to one resource within the API. e.g. a __Stripe Source__ would have have one __Stream__ for `Transactions`, one
for `Charges` and so on.

### The AbstractSource Object
This brings us to the CDK's `AbstractSource` object. This represents the just discussed `Source` concept and is
the top-level entrypoint for the 4 methods __Source__'s need to implement.

`Spec` and `Check` are the `AbstractSource`'s simplest operations.

`Spec` returns a checked in json schema file encoding the required configuration. The `AbstractSource` looks for
a file named `spec.json` by default in the module's root. Here is an [example](#link exchange rate file).

`Check` delegates to the `AbstractSource`'s `check_connection` function. The function `config` parameter
the user-provided configuration, as specified in the `spec.json` returned by `Spec`, and is used to validate
authentication and authorization.

#### The Streams Interface
In parallel with the above concepts, an `AbstractSource` owns a set of [`Streams`](). This is populated via
the `AbstractSource`'s `streams` [function](). `Discover` and `Read` rely on this populated set.

`Discover` returns an [`AirbyteCatalog`]() representing all the distinct resources the underlying API supports.

In summary, a concrete implementation of the `AbstractSource` object - including implementing the `check_connection`
function, and placing a few json file - is all that is need to implement 2 of the 4 methods.

### The HTTPStream Object

// The code construct an Airbyte Stream corresponds to

// full-refresh: the basic

// incremental: the state object,


// authentication

// rate limiting

// Look at the Exchange Rate and the Stripe api for examples

