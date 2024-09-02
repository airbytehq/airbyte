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
| 0.1.14 | 2024-08-31 | [45004](https://github.com/airbytehq/airbyte/pull/45004) | Update dependencies |
| 0.1.13 | 2024-08-24 | [44685](https://github.com/airbytehq/airbyte/pull/44685) | Update dependencies |
| 0.1.12 | 2024-08-17 | [44356](https://github.com/airbytehq/airbyte/pull/44356) | Update dependencies |
| 0.1.11 | 2024-08-10 | [43609](https://github.com/airbytehq/airbyte/pull/43609) | Update dependencies |
| 0.1.10 | 2024-08-03 | [43122](https://github.com/airbytehq/airbyte/pull/43122) | Update dependencies |
| 0.1.9 | 2024-07-27 | [42598](https://github.com/airbytehq/airbyte/pull/42598) | Update dependencies |
| 0.1.8 | 2024-07-20 | [42217](https://github.com/airbytehq/airbyte/pull/42217) | Update dependencies |
| 0.1.7 | 2024-07-13 | [41870](https://github.com/airbytehq/airbyte/pull/41870) | Update dependencies |
| 0.1.6 | 2024-07-10 | [41554](https://github.com/airbytehq/airbyte/pull/41554) | Update dependencies |
| 0.1.5 | 2024-07-09 | [41114](https://github.com/airbytehq/airbyte/pull/41114) | Update dependencies |
| 0.1.4 | 2024-07-06 | [40978](https://github.com/airbytehq/airbyte/pull/40978) | Update dependencies |
| 0.1.3 | 2024-06-25 | [40423](https://github.com/airbytehq/airbyte/pull/40423) | Update dependencies |
| 0.1.2 | 2024-06-22 | [40018](https://github.com/airbytehq/airbyte/pull/40018) | Update dependencies |
| 0.1.1 | 2024-05-20 | [38378](https://github.com/airbytehq/airbyte/pull/38378) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2022-11-30 | [#19923](https://github.com/airbytehq/airbyte/pull/19923) | 🎉 New source: Unleash [low-code CDK] |

</details>
