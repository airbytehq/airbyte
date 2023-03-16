# Unleash

## Overview

[Unleash API](https://docs.getunleash.io/reference/api/legacy/unleash) is a web service for accessing the data from your Unleash feature experiments. To get started, You need a key to successfully authenticate against the API. Unleash is implemented with the [Airbyte Low-Code CDK](https://docs.airbyte.com/connector-development/config-based/low-code-cdk-overview).

The Unleash source can sync data from the [Unleash API](https://docs.getunleash.io/reference/api/legacy/unleash). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch.

## Output Format

#### Each content item has the following structure:-

```yaml
{
    "name": "string",
    "description": "string"
    "project": "string"
    "type": "string"
    "enabled": "boolean"
    "stale": "boolean"
    "strategies": "array"
    "strategy": "string"
    "parameters": "object"
    "impressionData": "boolean"
    "variants": "array"
}
```

**Description:-**

**webPublicationDate**: The combined date and time of publication
**webUrl**: The URL of the html content
**apiUrl**: The URL of the raw content

## Core Streams

Connector supports the `features` stream that returns all pieces of content in the API.

## Rate Limiting

The key that you are assigned is rate-limited and as such any applications that depend on making large numbers of requests on a polling basis are likely to exceed their daily quota and thus be prevented from making further requests until the next period begins.

## Authentication and Permissions

To access the API, you will need to sign up for an API key, which should be sent with every request. Visit [this](https://docs.getunleash.io/how-to/how-to-create-api-tokens) link to get an API key.
You can see the type of payload the API returns by visiting [this](https://docs.getunleash.io/reference/api/legacy/unleash/client/features).

See [this](https://docs.airbyte.io/integrations/sources/unleash) link for the connector docs.
