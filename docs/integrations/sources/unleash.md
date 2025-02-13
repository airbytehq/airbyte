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
| 0.2.10 | 2025-02-08 | [53524](https://github.com/airbytehq/airbyte/pull/53524) | Update dependencies |
| 0.2.9 | 2025-02-01 | [53051](https://github.com/airbytehq/airbyte/pull/53051) | Update dependencies |
| 0.2.8 | 2025-01-25 | [52420](https://github.com/airbytehq/airbyte/pull/52420) | Update dependencies |
| 0.2.7 | 2025-01-18 | [52014](https://github.com/airbytehq/airbyte/pull/52014) | Update dependencies |
| 0.2.6 | 2025-01-11 | [51405](https://github.com/airbytehq/airbyte/pull/51405) | Update dependencies |
| 0.2.5 | 2024-12-28 | [50802](https://github.com/airbytehq/airbyte/pull/50802) | Update dependencies |
| 0.2.4 | 2024-12-21 | [50369](https://github.com/airbytehq/airbyte/pull/50369) | Update dependencies |
| 0.2.3 | 2024-12-14 | [49764](https://github.com/airbytehq/airbyte/pull/49764) | Update dependencies |
| 0.2.2 | 2024-12-12 | [49413](https://github.com/airbytehq/airbyte/pull/49413) | Update dependencies |
| 0.2.1 | 2024-12-11 | [48326](https://github.com/airbytehq/airbyte/pull/48326) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.0 | 2024-10-06 | [46525](https://github.com/airbytehq/airbyte/pull/46525) | Converting to manifest-only format |
| 0.1.18 | 2024-10-05 | [46490](https://github.com/airbytehq/airbyte/pull/46490) | Update dependencies |
| 0.1.17 | 2024-09-28 | [46113](https://github.com/airbytehq/airbyte/pull/46113) | Update dependencies |
| 0.1.16 | 2024-09-21 | [45817](https://github.com/airbytehq/airbyte/pull/45817) | Update dependencies |
| 0.1.15 | 2024-09-14 | [45295](https://github.com/airbytehq/airbyte/pull/45295) | Update dependencies |
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
