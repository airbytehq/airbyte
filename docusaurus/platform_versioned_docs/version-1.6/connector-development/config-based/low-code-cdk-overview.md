# Low-code connector development

Airbyte's low-code framework enables you to build source connectors for REST APIs via a [connector builder UI](../connector-builder-ui/overview.md) or by modifying boilerplate YAML files via terminal or text editor. Low-code CDK is a part of Python CDK that provides a mapping from connector manifest YAML files to actual behavior implementations.

## Why low-code?

### API Connectors are common and formulaic

In building and maintaining hundreds of connectors at Airbyte, we've observed that whereas API source connectors constitute the overwhelming majority of connectors, they are also the most formulaic. API connector code almost always solves small variations of these problems:

1. Making requests to various endpoints under the same API URL e.g: `https://api.stripe.com/customers`, `https://api.stripe.com/transactions`, etc..
2. Authenticating using a common auth strategy such as Oauth or API keys
3. Pagination using one of the 4 ubiquitous pagination strategies: limit-offset, page-number, cursor pagination, and header link pagination
4. Gracefully handling rate limiting by implementing exponential backoff, fixed-time backoff, or variable-time backoff
5. Describing the schema of the data returned by the API, so that downstream warehouses can create normalized tables
6. Decoding the format of the data returned by the API (e.g JSON, XML, CSV, etc..) and handling compression (GZIP, BZIP, etc..)
7. Supporting incremental data exports by remembering what data was already synced, usually using date-based cursors

and so on.

### A declarative, low-code paradigm commoditizes solving formulaic problems

Given that these problems each have a very finite number of solutions, we can remove the need for writing the code to build these API connectors by providing configurable off-the-shelf components to solve them. In doing so, we significantly decrease development effort and bugs while improving maintainability and accessibility. In this paradigm, instead of having to write the exact lines of code to solve this problem over and over, a developer can pick the solution to each problem from an available component, and rely on the framework to run the logic for them.

## Overview of the process

To use the low-code framework to build an REST API Source connector:

1. Generate the API key or credentials for the source you want to build a connector for
2. Set up the project on your local machine
3. Set up your local development environment
4. Use the connector builder UI to define the connector YAML manifest and test the connector
5. Specify stream schemas
6. Add the connector to the Airbyte platform

For a step-by-step tutorial, refer to the [Getting Started with the Connector Builder](../connector-builder-ui/tutorial.mdx) or the [video tutorial](https://youtu.be/i7VSL2bDvmw)

## Configuring the YAML file

The low-code framework involves editing the Connector Manifest, which is a boilerplate YAML file. The general structure of the YAML file is as follows:

```
version: "0.1.0"
definitions:
  <key-value pairs defining objects which will be reused in the YAML connector>
streams:
  <list stream definitions>
check:
  <definition of connection checker>
spec:
  <connector spec>
```

The following table describes the components of the YAML file:

| Component     | Description                                                                                                                                                                                                       |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `version`     | Indicates the framework version                                                                                                                                                                                   |
| `definitions` | Describes the objects to be reused in the YAML connector                                                                                                                                                          |
| `streams`     | Lists the streams of the source                                                                                                                                                                                   |
| `check`       | Describes how to test the connection to the source by trying to read a record from a specified list of streams and failing if no records could be read                                                            |
| `spec`        | A [connector specification](../../understanding-airbyte/airbyte-protocol#actor-specification) which describes the required and optional parameters which can be input by the end user to configure this connector |

:::tip
Streams define the schema of the data to sync, as well as how to read it from the underlying API source. A stream generally corresponds to a resource within the API. They are analogous to tables for a relational database source.
:::

For each stream, configure the following components:

| Component              | Sub-component    | Description                                                                                                                                                                                                                           |
| ---------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name                   |                  | Name of the stream                                                                                                                                                                                                                    |
| Primary key (Optional) |                  | Used to uniquely identify records, enabling deduplication. Can be a string for single primary keys, a list of strings for composite primary keys, or a list of list of strings for composite primary keys consisting of nested fields |
| Schema                 |                  | Describes the data to sync                                                                                                                                                                                                            |
| Incremental sync       |                  | Describes the behavior of an incremental sync which enables checkpointing and replicating only the data that has changed since the last sync to a destination.                                                                        |
| Data retriever         |                  | Describes how to retrieve data from the API                                                                                                                                                                                           |
|                        | Requester        | Describes how to prepare HTTP requests to send to the source API and defines the base URL and path, the request options provider, the HTTP method, authenticator, error handler components                                            |
|                        | Pagination       | Describes how to navigate through the API's pages                                                                                                                                                                                     |
|                        | Record Selector  | Describes how to extract records from a HTTP response                                                                                                                                                                                 |
|                        | Partition Router | Describes how to partition the stream, enabling incremental syncs and checkpointing                                                                                                                                                   |
| Cursor field           |                  | Field to use as stream cursor. Can either be a string, or a list of strings if the cursor is a nested field.                                                                                                                          |
| Transformations        |                  | A set of transformations to be applied on the records read from the source before emitting them to the destination                                                                                                                    |

For a deep dive into each of the components, refer to [Understanding the YAML file](./understanding-the-yaml-file/yaml-overview.md) or the [full YAML Schema definition](https://github.com/airbytehq/airbyte-python-cdk/blob/main/airbyte_cdk/sources/declarative/declarative_component_schema.yaml)

## Sample connectors

For examples of production-ready config-based connectors, refer to:

- [Greenhouse](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-greenhouse/source_greenhouse/manifest.yaml)
- [Sendgrid](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-sendgrid/source_sendgrid/manifest.yaml)
- [Sentry](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-sentry/source_sentry/manifest.yaml)

## Reference

The full schema definition for the YAML file can be found [here](https://raw.githubusercontent.com/airbytehq/airbyte-python-cdk/main/airbyte_cdk/sources/declarative/declarative_component_schema.yaml).
