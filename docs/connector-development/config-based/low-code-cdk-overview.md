# Low-code connector development

Airbyte’s low-code framework enables you to build source connectors for REST APIs by modifying boilerplate YAML files.

:::warning
The low-code framework is in [alpha](https://docs.airbyte.com/project-overview/product-release-stages/#alpha), which means it’s still in active development and may include backward-incompatible changes. Share feedback and requests with us on our [Slack channel](https://slack.airbyte.com/) or email us at [feedback@airbyte.io](mailto:feedback@airbyte.io)
:::

## What connectors can I build using the low-code framework?

Refer to the REST API documentation for the source you want to build the connector for and answer the following questions:

- Does the REST API documentation show which HTTP method to use to retrieve data, and that the response is a JSON object?
- Do the queries return data synchronously?
- Does the API support any of the following pagination mechanisms:
    - Offset count passed either by query params or request header
    - Page count passed either by query params or request header
    - Cursor field pointing to the URL of the next page of records
- Does the API support any of the following authentication mechanisms:
    - [A query param or a HTTP header](https://docs.airbyte.com/connector-development/config-based/understanding-the-yaml-file/authentication#apikeyauthenticator)
    - [Basic Auth over HTTPS](https://docs.airbyte.com/connector-development/config-based/understanding-the-yaml-file/authentication#basichttpauthenticator)
    - [OAuth 2.0](https://docs.airbyte.com/connector-development/config-based/understanding-the-yaml-file/authentication#oauth)
- Does the API support static schema?
- Does the endpoint have a strict rate limit?
  Throttling is not supported, but the connector can use exponential backoff to avoid API bans in case it gets rate limited. This can work for APIs with high rate limits, but not for those that have strict limits on a small time-window.
- Are the following features sufficient:

  | Feature                                                      | Support                                                                                                                                                                                                                                       |
              |--------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
  | Resource type                                                | Collections<br/>[Sub-collection](understanding-the-yaml-file/stream-slicers.md#substreams)                                                                                                                                                      |
  | Sync mode                                                    | Full refresh<br/>Incremental                                                                                                                                             |
  | Schema discovery                                             | Static schemas                                                                                                                                                  |
  | [Stream slicing](understanding-the-yaml-file/stream-slicers.md)                        | [Datetime](understanding-the-yaml-file/stream-slicers.md#Datetime), [lists](understanding-the-yaml-file/stream-slicers.md#list-stream-slicer), [parent-resource id](understanding-the-yaml-file/stream-slicers.md#Substream-slicer)                                                                                                                                     |
  | [Record transformation](understanding-the-yaml-file/record-selector.md)                | [Field selection](understanding-the-yaml-file/record-selector.md#selecting-a-field)<br/>[Adding fields](understanding-the-yaml-file/record-selector.md#adding-fields)<br/>[Removing fields](understanding-the-yaml-file/record-selector.md#removing-fields)<br/>[Filtering records](understanding-the-yaml-file/record-selector.md#filtering-records) |
  | [Error detection](understanding-the-yaml-file/error-handling.md)                       | [From HTTP status  code](understanding-the-yaml-file/error-handling.md#from-status-code)<br/>[From error message](understanding-the-yaml-file/error-handling.md#from-error-message)                                                                                                               |
  | [Backoff strategies](understanding-the-yaml-file/error-handling.md#Backoff-Strategies) | [Exponential](understanding-the-yaml-file/error-handling.md#Exponential-backoff)<br/>[Constant](understanding-the-yaml-file/error-handling.md#Constant-Backoff)<br/>[Derived from headers](understanding-the-yaml-file/error-handling.md#Wait-time-defined-in-header)                                                       |

If the answer to all questions is yes, you can use the low-code framework to build a connector for the source. If not, use the [Python CDK](../cdk-python/README.md).

## Prerequisites

- An API key for the source you want to build a connector for
- Python >= 3.9
- Docker
- NodeJS

## Overview of the process

To use the low-code framework to build an REST API Source connector:

1. Generate the API key for the source you want to build a connector for
2. Set up the project on your local machine
3. Set up your local development environment
4. Update the connector spec and config​uration
5. Update the connector definition
6. Test the connector
7. Add the connector to the Airbyte platform

For a step-by-step tutorial, refer to the [Getting Started tutorial](./tutorial/0-getting-started.md) or the [video tutorial](https://youtu.be/i7VSL2bDvmw)

## Configuring the YAML file

The low-code framework involves editing a boilerplate YAML file. The general structure of the YAML file is as follows:

```
version: "0.1.0"
definitions:
 <key-value pairs defining objects which will be reused in the YAML connector>
streams:
 <list stream definitions>
check:
 <definition of connection checker>
```

The following table describes the components of the YAML file:

| Component     | Description                                                                                                                                            |
|---------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| `version`     | Indicates the framework version                                                                                                                        |
| `definitions` | Describes the objects to be reused in the YAML connector                                                                                               |
| `streams`     | Lists the streams of the source                                                                                                                        |
| `check`       | Describes how to test the connection to the source by trying to read a record from a specified list of streams and failing if no records could be read |

:::tip
Streams define the schema of the data to sync, as well as how to read it from the underlying API source. A stream generally corresponds to a resource within the API. They are analogous to tables for a relational database source.
:::

For each stream, configure the following components:

| Component              | Sub-component   | Description                                                                                                                                                                                                                           |
|------------------------|-----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name                   |                 | Name of the stream                                                                                                                                                                                                                    |
| Primary key (Optional) |                 | Used to uniquely identify records, enabling deduplication. Can be a string for single primary keys, a list of strings for composite primary keys, or a list of list of strings for composite primary keys consisting of nested fields |
| Schema                 |                 | Describes the data to sync                                                                                                                                                                                                            |
| Data retriever         |                 | Describes how to retrieve data from the API                                                                                                                                                                                           |
|                        | Requester       | Describes how to prepare HTTP requests to send to the source API and defines the base URL and path, the request options provider, the HTTP method, authenticator, error handler components                                            |
|                        | Pagination      | Describes how to navigate through the API's pages                                                                                                                                                                                     |
|                        | Record Selector | Describes how to extract records from a HTTP response                                                                                                                                                                                 |
|                        | Stream Slicer   | Describes how to partition the stream, enabling incremental syncs and checkpointing                                                                                                                                                   |
| Cursor field           |                 | Field to use as stream cursor. Can either be a string, or a list of strings if the cursor is a nested field.                                                                                                                          |
| Transformations        |                 | A set of transformations to be applied on the records read from the source before emitting them to the destination                                                                                                                    |
| Checkpoint interval    |                 | Defines the interval, in number of records, at which incremental syncs should be checkpointed                                                                                                                                         |

For a deep dive into each of the components, refer to [Understanding the YAML file](./understanding-the-yaml-file/yaml-overview.md) or the [full YAML Schema definition](./source_schema.yaml)

## Tutorial

This section a tutorial that will guide you through the end-to-end process of implementing a low-code connector.

0. [Getting started](tutorial/0-getting-started.md)
1. [Creating a source](tutorial/1-create-source.md)
2. [Installing dependencies](tutorial/2-install-dependencies.md)
3. [Connecting to the API](tutorial/3-connecting-to-the-API-source.md)
4. [Reading data](tutorial/4-reading-data.md)
5. [Incremental reads](tutorial/5-incremental-reads.md)
6. [Testing](tutorial/6-testing.md)

## Sample connectors

For examples of production-ready config-based connectors, refer to:

- [Greenhouse](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-greenhouse)
- [Sendgrid](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-sendgrid/source_sendgrid/sendgrid.yaml)
- [Sentry](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-sentry/source_sentry/sentry.yaml)
