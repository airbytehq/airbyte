# Config-based connectors overview

:warning: This framework is in alpha stage. Support is not in production and is available only to select users. :warning:

The goal of this document is to give enough technical specifics to understand how config-based connectors work.
When you're ready to start building a connector, you can start with [the tutorial](./tutorial/0-getting-started.md), or dive into [more detailed documentation](./index.md).

## Overview

The CDK's config-based interface uses a declarative approach to building source connectors for REST APIs.

Config-based connectors work by parsing a YAML configuration describing the Source, then running the configured connector using a Python backend.

The process then submits HTTP requests to the API endpoint, and extracts records out of the response.

See the [connector definition section](yaml-structure.md) for more information on the YAML file describing the connector.

## Does this framework support the connector I want to build?

Not all APIs are can be built using this framework because its featureset is still limited.
This section describes guidelines for determining whether a connector for a given API can be built using the config-based framework. Please let us know through the #lowcode-earlyaccess Slack channel if you'd like to build something that falls outside what we currently support and we'd be happy to discuss and prioritize in the coming months!

Refer to the API's documentation to answer the following questions:

### Is this a HTTP REST API returning data as JSON?

The API documentation should show which HTTP method must be used to retrieve data from the API.
For example, the [documentation for the Exchange Rates Data API](https://apilayer.com/marketplace/exchangerates_data-api#documentation-tab) says the GET method should be used, and that the response is a JSON object.

Other API types such as SOAP or GraphQL are not supported.

Other encoding schemes such as CSV or Protobuf are not supported.

Integrations that require the use of an SDK are not supported.

### Do queries return the data synchronously or do they trigger a bulk workflow?

Some APIs return the data of interest as part of the response. This is the case for the [Exchange Rates Data API](https://apilayer.com/marketplace/exchangerates_data-api#documentation-tab) - each request results in a response containing the data we're interested in.

Other APIs use bulk workflows, which means a query will trigger an asynchronous process on the integration's side. [Zendesk bulk queries](https://developer.zendesk.com/api-reference/ticketing/tickets/tickets/#bulk-mark-tickets-as-spam) are an example of such integrations.

An initial request will trigger the workflow and return an ID and a job status. The actual data then needs to be fetched when the asynchronous job is completed.

Asynchronous bulk workflows are not supported.

### What is the pagination mechanism?

The only pagination mechanisms supported are

* Offset count passed either by query params or request header such as [Sendgrid](https://docs.sendgrid.com/api-reference/bounces-api/retrieve-all-bounces)
* Page count passed either by query params or request header such as [Greenhouse](https://developers.greenhouse.io/harvest.html#get-list-applications)
* Cursor field pointing to the URL of the next page of records such as [Sentry](https://docs.sentry.io/api/pagination/)

### What is the authorization mechanism?

Endpoints that require authenticating using a query param or a HTTP header, as is the case for the [Exchange Rates Data API](https://apilayer.com/marketplace/exchangerates_data-api#authentication), are supported.

Endpoints that require authenticating using Basic Auth over HTTPS, as is the case for [Greenhouse](https://developers.greenhouse.io/harvest.html#authentication), are supported.

Endpoints that require authenticating using OAuth 2.0, as is the case for [Strava](https://developers.strava.com/docs/authentication/#introduction), are supported.

Other authentication schemes such as GWT are not supported.

### Is the schema static or dynamic?

Only static schemas are supported.

Dynamically deriving the schema from querying an endpoint is not supported.

### Does the endpoint have a strict rate limit

Throttling is not supported, but the connector can use exponential backoff to avoid API bans in case it gets rate limited. This can work for APIs with high rate limits, but not for those that have strict limits on a small time-window, such as the [Reddit Ads API](https://ads-api.reddit.com/docs/#section/Rate-Limits), which limits to 1 request per second.

## Supported features

| Feature                                                      | Support                                                                                                                                                                                                                                       |
|--------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Transport protocol                                           | HTTP                                                                                                                                                                                                                                          |
| HTTP methods                                                 | GET, POST                                                                                                                                                                                                                                     |
| Data format                                                  | JSON                                                                                                                                                                                                                                          |
| Resource type                                                | Collections<br/>Sub-collection                                                                                                                                                                                                                |
| [Pagination](./pagination.md)                                | [Page limit](./pagination.md#page-increment)<br/>[Offset](./pagination.md#offset-increment)<br/>[Cursor](./pagination.md#cursor)                                                                                                              |
| [Authentication](./authentication.md)                        | [Header based](./authentication.md#ApiKeyAuthenticator)<br/>[Bearer](./authentication.md#BearerAuthenticator)<br/>[Basic](./authentication.md#BasicHttpAuthenticator)<br/>[OAuth](./authentication.md#OAuth)                                  |
| Sync mode                                                    | Full refresh<br/>Incremental                                                                                                                                                                                                                  |
| Schema discovery                                             | Only static schemas                                                                                                                                                                                                                           |
| [Stream slicing](./stream-slicers.md)                        | [Datetime](./stream-slicers.md#Datetime), [lists](./stream-slicers.md#list-stream-slicer), [parent-resource id](./stream-slicers.md#Substream-slicer)                                                                                         |
| [Record transformation](./record-selector.md)                | [Field selection](./record-selector.md#selecting-a-field)<br/>[Adding fields](./record-selector.md#adding-fields)<br/>[Removing fields](./record-selector.md#removing-fields)<br/>[Filtering records](./record-selector.md#filtering-records) |
| [Error detection](./error-handling.md)                       | [From HTTP status  code](./error-handling.md#from-status-code)<br/>[From error message](./error-handling.md#from-error-message)                                                                                                               |
| [Backoff strategies](./error-handling.md#Backoff-Strategies) | [Exponential](./error-handling.md#Exponential-backoff)<br/>[Constant](./error-handling.md#Constant-Backoff)<br/>[Derived from headers](./error-handling.md#Wait-time-defined-in-header)                                                       |

If a feature you require is not supported, you can [request the feature](../../contributing-to-airbyte/README.md#requesting-new-features) and use the [Python CDK](../cdk-python/README.md).

## Source

Config-based connectors are a declarative way to define HTTP API sources.

A source is defined by 2 components:

1. The source's `Stream`s, which define the data to read
2. A `ConnectionChecker`, which describes how to run the `check` operation to test the connection to the API source

## Stream

Streams define the schema of the data to sync, as well as how to read it from the underlying API source.
A stream generally corresponds to a resource within the API. They are analogous to tables for a relational database source.

A stream is defined by:

1. A name
2. Primary key (Optional): Used to uniquely identify records, enabling deduplication. Can be a string for single primary keys, a list of strings for composite primary keys, or a list of list of strings for composite primary keys consisting of nested fields
3. [Schema](../cdk-python/schemas.md): Describes the data to sync
4. [Data retriever](overview.md#data-retriever): Describes how to retrieve the data from the API
5. [Cursor field](../cdk-python/incremental-stream.md) (Optional): Field to use as stream cursor. Can either be a string, or a list of strings if the cursor is a nested field.
6. [Transformations](./record-selector.md#transformations) (Optional): A set of transformations to be applied on the records read from the source before emitting them to the destination
7. [Checkpoint interval](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#state--checkpointing) (Optional): Defines the interval, in number of records, at which incremental syncs should be checkpointed

More details on streams and sources can be found in the [basic concepts section](../cdk-python/basic-concepts.md).

## Data retriever

The data retriever defines how to read the data for a Stream, and acts as an orchestrator for the data retrieval flow.
There is currently only one implementation, the `SimpleRetriever`, which is defined by

1. Requester: Describes how to submit requests to the API source
2. Paginator: Describes how to navigate through the API's pages
3. Record selector: Describes how to extract records from a HTTP response
4. Stream Slicer: Describes how to partition the stream, enabling incremental syncs and checkpointing

Each of those components (and their subcomponents) are defined by an explicit interface and one or many implementations.
The developer can choose and configure the implementation they need depending on specifications of the integration they are building against.

Since the `Retriever` is defined as part of the Stream configuration, different Streams for a given Source can use different `Retriever` definitions if needed.

### Data flow

The retriever acts as a coordinator, moving the data between its components before emitting `AirbyteMessage`s that can be read by the platform.
The `SimpleRetriever`'s data flow can be described as follows:

1. Given the connection config and the current stream state, the `StreamSlicer` computes the stream slices to read.
2. Iterate over all the stream slices defined by the stream slicer.
3. For each stream slice,
    1. Submit a request as defined by the requester
    2. Select the records from the response
    3. Repeat for as long as the paginator points to a next page

More details on the record selector can be found in the [record selector section](record-selector.md).

More details on the stream slicers can be found in the [stream slicers section](stream-slicers.md).

More details on the paginator can be found in the [pagination section](pagination.md).

## Requester

The `Requester` defines how to prepare HTTP requests to send to the source API.
There is currently only one implementation, the `HttpRequester`, which is defined by

1. A base url: The root of the API source
2. A path: The specific endpoint to fetch data from for a resource
3. The HTTP method: the HTTP method to use (GET or POST)
4. A request options provider: Defines the request parameters (query parameters), headers, and request body to set on outgoing HTTP requests
5. An authenticator: Defines how to authenticate to the source
6. An error handler: Defines how to handle errors

More details on authentication can be found in the [authentication section](authentication.md).

More details on error handling can be found in the [error handling section](error-handling.md).

## Connection Checker

The `ConnectionChecker` defines how to test the connection to the integration.

The only implementation as of now is `CheckStream`, which tries to read a record from a specified list of streams and fails if no records could be read.

## Custom components

Any builtin components can be overloaded by a custom Python class.
To create a custom component, define a new class in a new file in the connector's module.
The class must implement the interface of the component it is replacing. For instance, a pagination strategy must implement `airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy.PaginationStrategy`.
The class must also be a dataclass where each field represents an argument to configure from the yaml file, and an `InitVar` named options.

For example:

```
@dataclass
class MyPaginationStrategy(PaginationStrategy):
  my_field: Union[InterpolatedString, str]
  options: InitVar[Mapping[str, Any]]

  def __post_init__(self, options: Mapping[str, Any]):
    pass

  def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
    pass

  def reset(self):
    pass
```

This class can then be referred from the yaml file using its fully qualified class name:

```yaml
pagination_strategy:
  class_name: "my_connector_module.MyPaginationStrategy"
  my_field: "hello world"
```

## Sample connectors

The following connectors can serve as example of what production-ready config-based connectors look like

- [Greenhouse](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-greenhouse)
- [Sendgrid](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-sendgrid)
- [Sentry](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-sentry)
