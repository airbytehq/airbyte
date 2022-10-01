# Config-based connectors overview

:warning: This framework is in [alpha](https://docs.airbyte.com/project-overview/product-release-stages/#alpha). It is still in active development and may include backward-incompatible changes. Please share feedback and requests directly with us at feedback@airbyte.io :warning:

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

Endpoints that require [authenticating using a query param or a HTTP header](./authentication.md#apikeyauthenticator), as is the case for the [Exchange Rates Data API](https://apilayer.com/marketplace/exchangerates_data-api#authentication), are supported.

Endpoints that require [authenticating using Basic Auth over HTTPS](./authentication.md#basichttpauthenticator), as is the case for [Greenhouse](https://developers.greenhouse.io/harvest.html#authentication), are supported.

Endpoints that require [authenticating using OAuth 2.0](./authentication.md#oauth), as is the case for [Strava](https://developers.strava.com/docs/authentication/#introduction), are supported.

Other authentication schemes such as GWT are not supported.

### Is the schema static or dynamic?

Only static schemas are supported.

Dynamically deriving the schema from querying an endpoint is not supported.

### Does the endpoint have a strict rate limit

Throttling is not supported, but the connector can use exponential backoff to avoid API bans in case it gets rate limited. This can work for APIs with high rate limits, but not for those that have strict limits on a small time-window, such as the [Reddit Ads API](https://ads-api.reddit.com/docs/#section/Rate-Limits), which limits to 1 request per second.

## Source

Config-based connectors are a declarative way to define HTTP API sources.

A source is defined by 2 components:

1. The source's `Stream`s, which define the data to read
2. A `ConnectionChecker`, which describes how to run the `check` operation to test the connection to the API source

## Stream

## Data retriever

The data retriever defines how to read the data for a Stream, and acts as an orchestrator for the data retrieval flow.

Schema:

```yaml
Retriever:
  type:
  oneOf:
    - "$ref": "#/definitions/SimpleRetriever"
```

### Data flow

The retriever acts as a coordinator, moving the data between its components before emitting `AirbyteMessage`s that can be read by the platform.
The `SimpleRetriever`'s data flow can be described as follows:

Schema:

```yaml
SimpleRetriever:
  type: object
  additionalProperties: false
  required:
    - name
    - primary_key
    - requester
    - record_selector
    - stream_slicer
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    name:
      type: string
    primary_key:
      "$ref": "#/definitions/PrimaryKey"
    requester:
      "$ref": "#/definitions/Requester"
    record_selector:
      "$ref": "#/definitions/HttpSelector"
    paginator:
      "$ref": "#/definitions/Paginator"
    stream_slicer:
      "$ref": "#/definitions/StreamSlicer"
PrimaryKey:
  type: object
  oneOf:
    - string
    - type: array
      items:
        type: string
    - type: array
      items:
        type: array
        items:
          type: string
```

More details on the record selector can be found in the [record selector section](record-selector.md).

More details on the stream slicers can be found in the [stream slicers section](stream-slicers.md).

More details on the paginator can be found in the [pagination section](pagination.md).

## Requester

Schema:

More details on authentication can be found in the [authentication section](authentication.md).

## Connection Checker

The `ConnectionChecker` defines how to test the connection to the integration.

The only implementation as of now is `CheckStream`, which tries to read a record from a specified list of streams and fails if no records could be read.

Schema:

```yaml
ConnectionChecker:
  type: object
  oneOf:
    - "$ref": "#/definitions/CheckStream"
CheckStream:
  type: object
  additionalProperties: false
  required:
    - stream_names
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    stream_names:
      type: array
      items:
        type: string
```

## Custom components

## More readings

- [RequestOptionsProvider](./request-options.md#request-options-provider)
- [Pagination](./pagination.md)
- [Stream slicers](./stream-slicers.md)

