# Unleash

## Overview

The Unleash source can sync data from the [Unleash API](https://docs.getunleash.io/reference/api/legacy/unleash). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch.

## Requirements

To access the API, you will need to sign up for an API token, which should be sent with every request. Visit [this](https://docs.getunleash.io/how-to/how-to-create-api-tokens) link for a tutorial on how to generate an API key.

## This Source Supports the Following Streams

- features

## Output schema

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

For more information around the returned payload, [see that page](https://docs.getunleash.io/reference/api/legacy/unleash/client/features)

## Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

## Getting started

1. Generate an API Token following [those instructions](https://docs.getunleash.io/how-to/how-to-create-api-tokens)
2. Add a new data source and select **Unleash**
3. Setup your connection with your API Token and your API URL (you will find it in your API access tab, above your list of API Tokens)
4. (Optional) Use the `project name` and/or the `experiment name prefix` fields to filter the data extracted along those dimensions
5. Click **Set up source**

## Performance considerations

The API key that you are assigned is rate-limited.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                               |
| :------ | :--------- | :-------------------------------------------------------- | :------------------------------------ |
| 0.1.0   | 2022-11-30 | [#19923](https://github.com/airbytehq/airbyte/pull/19923) | 🎉 New source: Unleash [low-code CDK] |

</details>