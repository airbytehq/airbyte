# Oura

## Sync overview

This source can sync various data from the [Oura](https://ouraring.com/) ring.
It currently only supports authentication through personal access tokens, and
is therefore not suitable for syncing data from multiple Oura rings.

### Output schema

This source is capable of syncing the following streams:

- `daily_activity`
- `daily_readiness`
- `daily_sleep`
- `heart_rate`
- `sessions`
- `sleep_periods`
- `tags`
- `workouts`

### Features

| Feature           | Supported? \(Yes/No\) | Notes                             |
|:------------------|:----------------------|:----------------------------------|
| Full Refresh Sync | Yes                   |                                   |
| Incremental Sync  | No                    |                                   |
| Multiple rings    | No                    | May be implemented in the future. |

### Performance considerations

There are no documented rate limits for the Oura V2 API at the time of writing.
However, users must have an up-to-date version of the Oura app installed to use
the API.

## Getting started

### Requirements

1. Purchase an Oura ring.
2. Create a personal access token via the
   [Oura developer portal](https://cloud.ouraring.com/personal-access-tokens).

### Setup guide

The following fields are required fields for the connector to work:

- `api_key`: Your Oura API key.
- (optional) `start_datetime`: The start date and time for the sync.
- (optional) `end_datetime`: The end date and time for the sync.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                     |
|:--------|:-----------|:---------------------------------------------------------|:--------------------------------------------|
| 0.2.10 | 2025-01-18 | [51860](https://github.com/airbytehq/airbyte/pull/51860) | Update dependencies |
| 0.2.9 | 2025-01-11 | [51342](https://github.com/airbytehq/airbyte/pull/51342) | Update dependencies |
| 0.2.8 | 2024-12-28 | [50736](https://github.com/airbytehq/airbyte/pull/50736) | Update dependencies |
| 0.2.7 | 2024-12-21 | [50226](https://github.com/airbytehq/airbyte/pull/50226) | Update dependencies |
| 0.2.6 | 2024-12-14 | [49658](https://github.com/airbytehq/airbyte/pull/49658) | Update dependencies |
| 0.2.5 | 2024-12-12 | [49319](https://github.com/airbytehq/airbyte/pull/49319) | Update dependencies |
| 0.2.4 | 2024-12-11 | [49050](https://github.com/airbytehq/airbyte/pull/49050) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.3 | 2024-11-04 | [48189](https://github.com/airbytehq/airbyte/pull/48189) | Update dependencies |
| 0.2.2 | 2024-10-29 | [47800](https://github.com/airbytehq/airbyte/pull/47800) | Update dependencies |
| 0.2.1 | 2024-10-28 | [47576](https://github.com/airbytehq/airbyte/pull/47576) | Update dependencies |
| 0.2.0 | 2024-08-19 | [44409](https://github.com/airbytehq/airbyte/pull/44409) | Refactor connector to manifest-only format |
| 0.1.14 | 2024-08-17 | [44271](https://github.com/airbytehq/airbyte/pull/44271) | Update dependencies |
| 0.1.13 | 2024-08-12 | [43788](https://github.com/airbytehq/airbyte/pull/43788) | Update dependencies |
| 0.1.12 | 2024-08-10 | [43633](https://github.com/airbytehq/airbyte/pull/43633) | Update dependencies |
| 0.1.11 | 2024-08-03 | [43287](https://github.com/airbytehq/airbyte/pull/43287) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42356](https://github.com/airbytehq/airbyte/pull/42356) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41850](https://github.com/airbytehq/airbyte/pull/41850) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41519](https://github.com/airbytehq/airbyte/pull/41519) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41264](https://github.com/airbytehq/airbyte/pull/41264) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40951](https://github.com/airbytehq/airbyte/pull/40951) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40450](https://github.com/airbytehq/airbyte/pull/40450) | Update dependencies |
| 0.1.4 | 2024-06-22 | [40097](https://github.com/airbytehq/airbyte/pull/40097) | Update dependencies |
| 0.1.3 | 2024-06-04 | [39072](https://github.com/airbytehq/airbyte/pull/39072) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.2 | 2024-05-30 | [38399](https://github.com/airbytehq/airbyte/pull/38399) | [autopull] base image + poetry + up_to_date |
| 0.1.1 | 2024-05-28 | [38688](https://github.com/airbytehq/airbyte/pull/38688) | Make connector builder compatible |
| 0.1.0 | 2022-10-20 | [18224](https://github.com/airbytehq/airbyte/pull/18224) | New source |

</details>
