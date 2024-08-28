---
displayed_sidebar: docs
---

# Building a Java Destination

:::warning
The template for building a Java Destination connector is currently unavailable. The Airbyte team is working on revamping the Java CDK.
:::

## Summary

This article provides a checklist for how to create a Java destination. Each step in the checklist
has a link to a more detailed explanation below.

## Requirements

Docker and Java with the versions listed in the
[tech stack section](../../understanding-airbyte/tech-stack.md).

## Checklist

### Creating a destination

- Step 1: Create the destination using the template generator
- Step 2: Build the newly generated destination
- Step 3: Implement `spec` to define the configuration required to run the connector
- Step 4: Implement `check` to provide a way to validate configurations provided to the connector
- Step 5: Implement `write` to write data to the destination
- Step 6: Set up Acceptance Tests
- Step 7: Write unit tests or integration tests
- Step 8: Update the docs \(in `docs/integrations/destinations/<destination-name>.md`\)

:::info

All `./gradlew` commands must be run from the root of the airbyte project.

:::

:::info

If you need help with any step of the process, feel free to submit a PR with your progress and any
questions you have, or ask us on [slack](https://slack.airbyte.io).

:::

## Explaining Each Step

### Step 1: Create the destination using the template

Airbyte provides a code generator which bootstraps the scaffolding for our connector.

```bash
$ cd airbyte-integrations/connector-templates/generator # assumes you are starting from the root of the Airbyte project.
$ ./generate.sh
```

Select the `Java Destination` template and then input the name of your connector. We'll refer to the
destination as `<name>-destination` in this tutorial, but you should replace `<name>` with the
actual name you used for your connector e.g: `BigQueryDestination` or `bigquery-destination`.

### Step 2: Build the newly generated destination

You can build the destination by running:

```bash
# Must be run from the Airbyte project root
./gradlew :airbyte-integrations:connectors:destination-<name>:build
```

This compiles the Java code for your destination and builds a Docker image with the connector. At
this point, we haven't implemented anything of value yet, but once we do, you'll use this command to
compile your code and Docker image.

:::info

Airbyte uses Gradle to manage Java dependencies. To add dependencies for your connector, manage them
in the `build.gradle` file inside your connector's directory.

:::

#### Iterating on your implementation

We recommend the following ways of iterating on your connector as you're making changes:

- Test-driven development \(TDD\) in Java
- Test-driven development \(TDD\) using Airbyte's Acceptance Tests
- Directly running the docker image

#### Test-driven development in Java

This should feel like a standard flow for a Java developer: you make some code changes then run java
tests against them. You can do this directly in your IDE, but you can also run all unit tests via
Gradle by running the command to build the connector:

```text
./gradlew :airbyte-integrations:connectors:destination-<name>:build
```

This will build the code and run any unit tests. This approach is great when you are testing local
behaviors and writing unit tests.

#### TDD using acceptance tests & integration tests

Airbyte provides a standard test suite \(dubbed "Acceptance Tests"\) that runs against every
destination connector. They are "free" baseline tests to ensure the basic functionality of the
destination. When developing a connector, you can simply run the tests between each change and use
the feedback to guide your development.

If you want to try out this approach, check out Step 6 which describes what you need to do to set up
the acceptance Tests for your destination.

The nice thing about this approach is that you are running your destination exactly as Airbyte will
run it in the CI. The downside is that the tests do not run very quickly. As such, we recommend this
iteration approach only once you've implemented most of your connector and are in the finishing
stages of implementation. Note that Acceptance Tests are required for every connector supported by
Airbyte, so you should make sure to run them a couple of times while iterating to make sure your
connector is compatible with Airbyte.

#### Directly running the destination using Docker

If you want to run your destination exactly as it will be run by Airbyte \(i.e. within a docker
container\), you can use the following commands from the connector module directory
\(`airbyte-integrations/connectors/destination-<name>`\):

```text
# First build the container
./gradlew :airbyte-integrations:connectors:destination-<name>:build

# Then use the following commands to run it
# Runs the "spec" command, used to find out what configurations are needed to run a connector
docker run --rm airbyte/destination-<name>:dev spec

# Runs the "check" command, used to validate if the input configurations are valid
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-<name>:dev check --config /secrets/config.json

# Runs the "write" command which reads records from stdin and writes them to the underlying destination
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/sample_files:/sample_files airbyte/destination-<name>:dev write --config /secrets/config.json --catalog /sample_files/configured_catalog.json
```

Note: Each time you make a change to your implementation you need to re-build the connector image
via `./gradlew :airbyte-integrations:connectors:destination-<name>:build`.

The nice thing about this approach is that you are running your destination exactly as it will be
run by Airbyte. The tradeoff is that iteration is slightly slower, because you need to re-build the
connector between each change.

#### Handling Exceptions

In order to best propagate user-friendly error messages and log error information to the platform,
the [Airbyte Protocol](../../understanding-airbyte/airbyte-protocol.md#The Airbyte Protocol)
implements AirbyteTraceMessage.

We recommend using AirbyteTraceMessages for known errors, as in these cases you can likely offer the
user a helpful message as to what went wrong and suggest how they can resolve it.

Airbyte provides a static utility class, `io.airbyte.integrations.base.AirbyteTraceMessageUtility`,
to give you a clear and straight-forward way to emit these AirbyteTraceMessages. Example usage:

```java
try {
  // some connector code responsible for doing X
}
catch (ExceptionIndicatingIncorrectCredentials credErr) {
  AirbyteTraceMessageUtility.emitConfigErrorTrace(
    credErr, "Connector failed due to incorrect credentials while doing X. Please check your connection is using valid credentials.")
  throw credErr
}
catch (ExceptionIndicatingKnownErrorY knownErr) {
  AirbyteTraceMessageUtility.emitSystemErrorTrace(
    knownErr, "Connector failed because of reason Y while doing X. Please check/do/make ... to resolve this.")
  throw knownErr
}
catch (Exception e) {
  AirbyteTraceMessageUtility.emitSystemErrorTrace(
    e, "Connector failed while doing X. Possible reasons for this could be ...")
  throw e
}
```

Note the two different error trace methods.

- Where possible `emitConfigErrorTrace` should be used when we are certain the issue arises from a
  problem with the user's input configuration, e.g. invalid credentials.
- For everything else or if unsure, use `emitSystemErrorTrace`.

### Step 3: Implement `spec`

Each destination contains a specification written in JsonSchema that describes its inputs. Defining
the specification is a good place to start when developing your destination. Check out the
documentation [here](https://json-schema.org/) to learn the syntax. Here's
[an example](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/destination-postgres/src/main/resources/spec.json)
of what the `spec.json` looks like for the postgres destination.

Your generated template should have the spec file in
`airbyte-integrations/connectors/destination-<name>/src/main/resources/spec.json`. The generated
connector will take care of reading this file and converting it to the correct output. Edit it and
you should be done with this step.

For more details on what the spec is, you can read about the Airbyte Protocol
[here](../../understanding-airbyte/airbyte-protocol.md).

See the `spec` operation in action:

```bash
# First build the connector
./gradlew :airbyte-integrations:connectors:destination-<name>:build

# Run the spec operation
docker run --rm airbyte/destination-<name>:dev spec
```

### Step 4: Implement `check`

The check operation accepts a JSON object conforming to the `spec.json`. In other words if the
`spec.json` said that the destination requires a `username` and `password` the config object might
be `{ "username": "airbyte", "password": "password123" }`. It returns a json object that reports,
given the credentials in the config, whether we were able to connect to the destination.

While developing, we recommend storing any credentials in `secrets/config.json`. Any `secrets`
directory in the Airbyte repo is gitignored by default.

Implement the `check` method in the generated file `<Name>Destination.java`. Here's an
[example implementation](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/destination-bigquery/src/main/java/io/airbyte/integrations/destination/bigquery/BigQueryDestination.java#L94)
from the BigQuery destination.

Verify that the method is working by placing your config in `secrets/config.json` then running:

```text
# First build the connector
./gradlew :airbyte-integrations:connectors:destination-<name>:build

# Run the check method
docker run -v $(pwd)/secrets:/secrets --rm airbyte/destination-<name>:dev check --config /secrets/config.json
```

### Step 5: Implement `write`

The `write` operation is the main workhorse of a destination connector: it reads input data from the
source and writes it to the underlying destination. It takes as input the config file used to run
the connector as well as the configured catalog: the file used to describe the schema of the
incoming data and how it should be written to the destination. Its "output" is two things:

1. Data written to the underlying destination
2. `AirbyteMessage`s of type `AirbyteStateMessage`, written to stdout to indicate which records have
   been written so far during a sync. It's important to output these messages when possible in order
   to avoid re-extracting messages from the source. See the
   [write operation protocol reference](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol#write)
   for more information.

To implement the `write` Airbyte operation, implement the `getConsumer` method in your generated
`<Name>Destination.java` file. Here are some example implementations from different destination
conectors:

- [BigQuery](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/destination-bigquery/src/main/java/io/airbyte/integrations/destination/bigquery/BigQueryDestination.java#L188)
- [Google Pubsub](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/destination-pubsub/src/main/java/io/airbyte/integrations/destination/pubsub/PubsubDestination.java#L98)
- [Local CSV](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/destination-csv/src/main/java/io/airbyte/integrations/destination/csv/CsvDestination.java#L90)
- [Postgres](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/destination-postgres/src/main/java/io/airbyte/integrations/destination/postgres/PostgresDestination.java)

:::info

The Postgres destination leverages the `AbstractJdbcDestination` superclass which makes it extremely
easy to create a destination for a database or data warehouse if it has a compatible JDBC driver. If
the destination you are implementing has a JDBC driver, be sure to check out
`AbstractJdbcDestination`.

:::

For a brief overview on the Airbyte catalog check out
[the Beginner's Guide to the Airbyte Catalog](../../understanding-airbyte/beginners-guide-to-catalog.md).

### Step 6: Set up Acceptance Tests

The Acceptance Tests are a set of tests that run against all destinations. These tests are run in
the Airbyte CI to prevent regressions and verify a baseline of functionality. The test cases are
contained and documented in the
[following file](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/bases/standard-destination-test/src/main/java/io/airbyte/integrations/standardtest/destination/DestinationAcceptanceTest.java).

To setup acceptance Tests for your connector, follow the `TODO`s in the generated file
`<name>DestinationAcceptanceTest.java`. Once setup, you can run the tests using
`./gradlew :airbyte-integrations:connectors:destination-<name>:integrationTest`. Make sure to run
this command from the Airbyte repository root.

### Step 7: Write unit tests and/or integration tests

The Acceptance Tests are meant to cover the basic functionality of a destination. Think of it as the
bare minimum required for us to add a destination to Airbyte. You should probably add some unit
testing or custom integration testing in case you need to test additional functionality of your
destination.

#### Step 8: Update the docs

Each connector has its own documentation page. By convention, that page should have the following
path: in `docs/integrations/destinations/<destination-name>.md`. For the documentation to get
packaged with the docs, make sure to add a link to it in `docs/SUMMARY.md`. You can pattern match
doing that from existing connectors.

## Wrapping up

Well done on making it this far! If you'd like your connector to ship with Airbyte by default,
create a PR against the Airbyte repo and we'll work with you to get it across the finish line.
