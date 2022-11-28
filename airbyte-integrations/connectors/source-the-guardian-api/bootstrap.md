# The Guardian API

## Overview

[The Guardian Open Platform](https://open-platform.theguardian.com/) is a public web service for accessing all the content the Guardian creates, categorised by tags and section. To get started, You need a key to successfully authenticate against the API. The Guardian API Connector is implemented with the [Airbyte Low-Code CDK](https://docs.airbyte.com/connector-development/config-based/low-code-cdk-overview).

## Output Format

#### Each content item has the following structure:-

```yaml
{
    "id": "string",
    "type": "string"
    "sectionId": "string"
    "sectionName": "string"
    "webPublicationDate": "string"
    "webTitle": "string"
    "webUrl": "string"
    "apiUrl": "string"
    "isHosted": "boolean"
    "pillarId": "string"
    "pillarName": "string"
}
```

**Description:-**

**webPublicationDate**: The combined date and time of publication
**webUrl**: The URL of the html content
**apiUrl**: The URL of the raw content

## Core Streams

Connector supports the `content` stream that returns all pieces of content in the API.

## Rate Limiting

The key that you are assigned is rate-limited and as such any applications that depend on making large numbers of requests on a polling basis are likely to exceed their daily quota and thus be prevented from making further requests until the next period begins.

## Authentication and Permissions

To access the API, you will need to sign up for an API key, which should be sent with every request. Visit [this](https://open-platform.theguardian.com/access) link to get an API key.
The easiest way to see what data is included is to explore the data. You can build complex queries quickly and browse the results. Visit [this](https://open-platform.theguardian.com/explore) link to explore the data.

See [this](https://docs.airbyte.io/integrations/sources/the-guardian-api) link for the connector docs.
