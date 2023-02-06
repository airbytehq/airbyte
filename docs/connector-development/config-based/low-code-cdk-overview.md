# Low-code connector development

Airbyte’s low-code framework enables you to build source connectors for REST APIs via a [connector builder UI](connector-builder-ui.md) or by modifying boilerplate YAML files via terminal or text editor.

:::caution
The low-code framework is in [alpha](https://docs.airbyte.com/project-overview/product-release-stages/#alpha), which means it’s still in active development and may include backward-incompatible changes. Share feedback and requests with us on our [Slack channel](https://slack.airbyte.com/) or email us at [feedback@airbyte.io](mailto:feedback@airbyte.io)
:::

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

1. Generate the API key or credentials for the source you want to build a connector for
2. Set up the project on your local machine
3. Set up your local development environment
4. Use the connector builder UI to define the connector YAML manifest and test the connector
5. Specify stream schemas
6. Add the connector to the Airbyte platform

For a step-by-step tutorial, refer to the [Getting Started tutorial](./tutorial/0-getting-started.md) or the [video tutorial](https://youtu.be/i7VSL2bDvmw)
 
## Connector Builder UI
The main concept powering the lowcode connector framework is the Connector Manifest, a YAML file which describes the features and functionality of the connector. The structure of this YAML file is described in more detail [here](./understanding-the-yaml-file/yaml-overview). 

We recommend iterating on this YAML file is via the [connector builder UI](./connector-builder-ui) as it makes it easy to inspect and debug your connector in greater detail than you would be able to through the commandline. While you can still iterate via the commandline (and the docs contain instructions for how to do it), we're investing heavily in making the UI give you iteration superpowers, so we recommend you check it out!

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
spec: 
  <connector spec>
```

The following table describes the components of the YAML file:

| Component     | Description                                                                                                                                            |
|---------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| `version`     | Indicates the framework version                                                                                                                        |
| `definitions` | Describes the objects to be reused in the YAML connector                                                                                               |
| `streams`     | Lists the streams of the source                                                                                                                        |
| `check`       | Describes how to test the connection to the source by trying to read a record from a specified list of streams and failing if no records could be read |
| `spec`       | A [connector specification](../../understanding-airbyte/airbyte-protocol#actor-specification) which describes the required and optional parameters which can be input by the end user to configure this connector |

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

For a deep dive into each of the components, refer to [Understanding the YAML file](./understanding-the-yaml-file/yaml-overview.md) or the [full YAML Schema definition](../../../airbyte-cdk/python/airbyte_cdk/sources/declarative/declarative_component_schema.yaml)

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
