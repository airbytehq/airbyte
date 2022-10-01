# Getting Started with Low-Code CDK

:warning: This framework is in [alpha](https://docs.airbyte.com/project-overview/product-release-stages/#alpha). It is still in active development and may include backward-incompatible changes. Please share feedback and requests directly with us at feedback@airbyte.io :warning:

## What connectors can I build using the low-code framework?

Refer to the REST API documentation for the source you want to build the connector for and answer the following questions:

- Does the REST API documentation show which HTTP method to use to retrieve data, and that the response is a JSON object?
- Do the queries return data synchronously
- Does the API support any of the following pagination mechanisms:
    - Offset count passed either by query params or request header
    - Page count passed either by query params or request header
    - Cursor field pointing to the URL of the next page of records
- Does the API support any of the following authentication mechanisms:
    - Endpoints that require authenticating using a query param or a HTTP header
    - Endpoints that require authenticating using Basic Auth over HTTPS
    - Endpoints that require authenticating using OAuth 2.0
- Is the schema of the API static?
- Does the endpoint have a strict rate limit?
    - Throttling is not supported, but the connector can use exponential backoff to avoid API bans in case it gets rate limited. This can work for APIs with high rate limits, but not for those that have strict limits on a small time-window.
- Are the following features sufficient to implement your connector?

### Supported features

| Feature                                                                           | Support                                                                                                                                                                                                                                       |
|-----------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Transport protocol                                                                | HTTP                                                                                                                                                                                                                                          |
| HTTP methods                                                                      | GET, POST                                                                                                                                                                                                                                     |
| Data format                                                                       | JSON                                                                                                                                                                                                                                          |
| Resource type                                                                     | Collections<br/>[Sub-collection](./substreams.md)                                                                                                                                                                                             |
| [Pagination](./understanding-the-yaml-file.md#configuring-the-paginator)          | [Page limit](./pagination.md#page-increment)<br/>[Offset](./pagination.md#offset-increment)<br/>[Cursor](./pagination.md#cursor)                                                                                                              |
| [Authentication](./understanding-the-yaml-file.md#configuring-the-authentication) | [Header based](./authentication.md#ApiKeyAuthenticator)<br/>[Bearer](./authentication.md#BearerAuthenticator)<br/>[Basic](./authentication.md#BasicHttpAuthenticator)<br/>[OAuth](./authentication.md#OAuth)                                  |
| Sync mode                                                                         | Full refresh<br/>Incremental                                                                                                                                                                                                                  |
| Schema discovery                                                                  | Static schemas                                                                                                                                                                                                                                |
| [Stream slicing](./stream-slicers.md)                                             | [Datetime](./stream-slicers.md#Datetime), [lists](./stream-slicers.md#list-stream-slicer), [parent-resource id](./stream-slicers.md#Substream-slicer)                                                                                         |
| [Record transformation](./record-selector.md)                                     | [Field selection](./record-selector.md#selecting-a-field)<br/>[Adding fields](./record-selector.md#adding-fields)<br/>[Removing fields](./record-selector.md#removing-fields)<br/>[Filtering records](./record-selector.md#filtering-records) |
| [Error detection](./error-handling.md)                                            | [From HTTP status  code](./error-handling.md#from-status-code)<br/>[From error message](./error-handling.md#from-error-message)                                                                                                               |
| [Backoff strategies](./error-handling.md#Backoff-Strategies)                      | [Exponential](./error-handling.md#Exponential-backoff)<br/>[Constant](./error-handling.md#Constant-Backoff)<br/>[Derived from headers](./error-handling.md#Wait-time-defined-in-header)                                                       |

If the answer to all questions is yes, you can use the low-code framework to build a connector for the source.
If not, you can use the CDK, and [request the feature](../../contributing-to-airbyte/README.md#requesting-new-features) and use the [Python CDK](../cdk-python/README.md).

## Prerequisites

- An API key for the source you want to build a connector for
- Python >= 3.9
- Docker
- NodeJS

## Overview of the process

1. Generate the API key for the source you want to build a connector for
2. Set up the project on your local machine
3. Set up your local development environment
4. Update the connector spec and config​uration
5. Update the connector definition
6. Test the connector
7. Add the connector to the Airbyte platform

For a step-by-step tutorial, refer to the [Getting Started tutorial](./tutorial/0-getting-started.md).

## Configuring the YAML file

The low-code framework involves editing a boilerplate YAML file. The general structure of the YAML file is as follows:

```yaml
version: "0.1.0"
definitions:
  <key-value pairs defining objects which will be reused in the YAML connector>
streams:
  <list stream definitions>
check:
  <definition of connection checker>
```

| Component                                                    | Description                                                                                                                                                                                                                                   |
|--------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `version`                                                    | Indicates the framework version                                                                                                                                                                                                                                          |
| `definitions`                                                 | Describes the objects to be reused in the YAML connector                                                                                                                                                                                                                                     |
| `streams`                                                  | Lists the streams of the source                                                                                                                                                                                                                                          |
| `check`                                                | Describes how to test the connection to the source by trying to read a record from a specified list of streams and failing if no records could be read                                                                                                                                                                                            |

*Tip: Streams define the schema of the data to sync, as well as how to read it from the underlying API source. A stream generally corresponds to a resource within the API. They are analogous to tables for a relational database source.*

For each stream, configure the following components:

| Component              | Sub-component         | Description                                                                                                                                                                                                                          |
|------------------------|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name                   |                       | Name of the stream                                                                                                                                                                                                                   |
| Primary Key (Optional) |                       | Used to uniquely identify records, enabling deduplication. Can be a string for single primary keys, a list of strings for composite primary keys, or a list of list of strings for composite primary keys consisting of nested fields |
| Data retriever         |                       | Describes how to retrieve data from the API                                                                                                                                                                                          |
|                        | Requester             | Describes how to prepare HTTP requests to send to the source API and defines the base URL and path, the request options provider, the HTTP method, authenticator, error handler components                                           |
|                        | Pagination (Optional) | Describes how to navigate through the API's pages                                                                                                                                                                                    |
|                        | Record selector       | Describes how to extract records from a HTTP response                                                                                                                                                                                |
|                        | Stream slicer         | Describes how to partition the stream, enabling incremental syncs and checkpointing                                                                                                                                                  |
| Cursor field           |                       | Field to use as stream cursor. Can either be a string, or a list of strings if the cursor is a nested field.                                                                                                                         |
| Transformations        |                       | A set of transformations to be applied on the records read from the source before emitting them to the destination                                                                                                                   |
| Checkpoint interval    |                       | Defines the interval, in number of records, at which incremental syncs should be checkpointed|

More details on the streams's definition can be found [here](./understanding-the-yaml-file.md#defining-the-stream)

The complete schema of the file can be found [here](./source_schema.yaml)

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

The following connectors can serve as example of what production-ready config-based connectors look like

- [Greenhouse](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-greenhouse)
- [Sendgrid](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-sendgrid/source_sendgrid/sendgrid.yaml)
- [Sentry](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-sentry/source_sentry/sentry.yaml)
