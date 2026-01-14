# Gong

## Sync overview

The Gong source supports both Full Refresh and Incremental syncs. This source can sync data for the [Gong API](https://help.gong.io/docs/what-the-gong-api-provides).

### Output schema

This source syncs the following streams:

| Stream | Sync Mode | Description |
| :----- | :-------- | :---------- |
| [answered scorecards](https://gong.app.gong.io/settings/api/documentation#post-/v2/stats/activity/scorecards) | Incremental | Scorecard responses with review timestamps |
| [calls](https://gong.app.gong.io/settings/api/documentation#get-/v2/calls) | Incremental | Call metadata including participants, duration, and timestamps |
| [extensive calls](https://gong.app.gong.io/settings/api/documentation#post-/v2/calls/extensive) | Incremental | Detailed call data including transcripts, topics, and interaction stats |
| [scorecards](https://gong.app.gong.io/settings/api/documentation#get-/v2/settings/scorecards) | Full Refresh | Scorecard definitions and configurations |
| [users](https://gong.app.gong.io/settings/api/documentation#get-/v2/users) | Full Refresh | User profiles and settings |

### Features

| Feature                   | Supported? | Notes |
| :------------------------ | :--------- | :---- |
| Full Refresh Sync         | Yes        |       |
| Incremental - Append Sync | Yes        | Supported for calls, extensive calls, and answered scorecards |
| Namespaces                | No         |       |

### Performance considerations

The Gong connector should not run into Gong API limitations under normal usage. Gong limits API access to 3 calls per second and 10,000 calls per day. If you exceed these limits, the API returns HTTP status code 429 with a Retry-After header indicating when to retry.

## Requirements

- **Gong API keys**. You must be a Gong administrator to obtain API credentials. Navigate to Settings, then API in your Gong account to generate an access key and secret. See the [Gong API documentation](https://help.gong.io/docs/receive-access-to-the-api) for detailed instructions.
- **Start Date** (optional). The date from which to fetch data in ISO-8601 format (for example, `2024-01-01T00:00:00Z`). This applies to incremental streams. If not specified, the connector fetches data from the last 90 days.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.4.14 | 2026-01-13 | [71344](https://github.com/airbytehq/airbyte/pull/71344) | Add 404 error handlers and fix CDK import path |
| 0.4.13 | 2025-08-09 | [64594](https://github.com/airbytehq/airbyte/pull/64594) | Update dependencies |
| 0.4.12 | 2025-08-02 | [64200](https://github.com/airbytehq/airbyte/pull/64200) | Update dependencies |
| 0.4.11 | 2025-07-19 | [63504](https://github.com/airbytehq/airbyte/pull/63504) | Update dependencies |
| 0.4.10 | 2025-07-12 | [63139](https://github.com/airbytehq/airbyte/pull/63139) | Update dependencies |
| 0.4.9 | 2025-07-05 | [62641](https://github.com/airbytehq/airbyte/pull/62641) | Update dependencies |
| 0.4.8 | 2025-06-21 | [61866](https://github.com/airbytehq/airbyte/pull/61866) | Update dependencies |
| 0.4.7 | 2025-06-14 | [61085](https://github.com/airbytehq/airbyte/pull/61085) | Update dependencies |
| 0.4.6 | 2025-05-24 | [60651](https://github.com/airbytehq/airbyte/pull/60651) | Update dependencies |
| 0.4.5 | 2025-05-10 | [59892](https://github.com/airbytehq/airbyte/pull/59892) | Update dependencies |
| 0.4.4 | 2025-05-03 | [59272](https://github.com/airbytehq/airbyte/pull/59272) | Update dependencies |
| 0.4.3 | 2025-04-26 | [57696](https://github.com/airbytehq/airbyte/pull/57696) | Update dependencies |
| 0.4.2 | 2025-04-05 | [57039](https://github.com/airbytehq/airbyte/pull/57039) | Update dependencies |
| 0.4.1 | 2025-03-29 | [56494](https://github.com/airbytehq/airbyte/pull/56494) | Update dependencies |
| 0.4.0 | 2025-03-25 | [55803](https://github.com/airbytehq/airbyte/pull/55803) | add incremental extensiveCalls |
| 0.3.16 | 2025-03-22 | [55969](https://github.com/airbytehq/airbyte/pull/55969) | Update dependencies |
| 0.3.15 | 2025-03-08 | [55269](https://github.com/airbytehq/airbyte/pull/55269) | Update dependencies |
| 0.3.14 | 2025-03-01 | [54962](https://github.com/airbytehq/airbyte/pull/54962) | Update dependencies |
| 0.3.13 | 2025-02-22 | [54394](https://github.com/airbytehq/airbyte/pull/54394) | Update dependencies |
| 0.3.12 | 2025-02-15 | [53718](https://github.com/airbytehq/airbyte/pull/53718) | Update dependencies |
| 0.3.11 | 2025-02-08 | [53334](https://github.com/airbytehq/airbyte/pull/53334) | Update dependencies |
| 0.3.10 | 2025-02-01 | [52824](https://github.com/airbytehq/airbyte/pull/52824) | Update dependencies |
| 0.3.9 | 2025-01-25 | [52342](https://github.com/airbytehq/airbyte/pull/52342) | Update dependencies |
| 0.3.8 | 2025-01-18 | [51704](https://github.com/airbytehq/airbyte/pull/51704) | Update dependencies |
| 0.3.7 | 2025-01-11 | [51059](https://github.com/airbytehq/airbyte/pull/51059) | Update dependencies |
| 0.3.6 | 2024-12-28 | [50521](https://github.com/airbytehq/airbyte/pull/50521) | Update dependencies |
| 0.3.5 | 2024-12-21 | [50017](https://github.com/airbytehq/airbyte/pull/50017) | Update dependencies |
| 0.3.4 | 2024-12-14 | [49538](https://github.com/airbytehq/airbyte/pull/49538) | Update dependencies |
| 0.3.3 | 2024-12-12 | [49155](https://github.com/airbytehq/airbyte/pull/49155) | Update dependencies |
| 0.3.2 | 2024-11-14 | [36604](https://github.com/airbytehq/airbyte/pull/36604) | Add incremental Feature |
| 0.3.1 | 2024-10-29 | [47824](https://github.com/airbytehq/airbyte/pull/47824) | Update dependencies |
| 0.3.0 | 2024-09-04 | [45117](https://github.com/airbytehq/airbyte/pull/45117) | Add new stream `extensive calls` |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-15 | [44144](https://github.com/airbytehq/airbyte/pull/44144) | Refactor connector to manifest-only format |
| 0.1.17 | 2024-08-10 | [43481](https://github.com/airbytehq/airbyte/pull/43481) | Update dependencies |
| 0.1.16 | 2024-08-03 | [43275](https://github.com/airbytehq/airbyte/pull/43275) | Update dependencies |
| 0.1.15 | 2024-07-27 | [42614](https://github.com/airbytehq/airbyte/pull/42614) | Update dependencies |
| 0.1.14 | 2024-07-20 | [42149](https://github.com/airbytehq/airbyte/pull/42149) | Update dependencies |
| 0.1.13 | 2024-07-13 | [41794](https://github.com/airbytehq/airbyte/pull/41794) | Update dependencies |
| 0.1.12 | 2024-07-10 | [41408](https://github.com/airbytehq/airbyte/pull/41408) | Update dependencies |
| 0.1.11 | 2024-07-09 | [41110](https://github.com/airbytehq/airbyte/pull/41110) | Update dependencies |
| 0.1.10 | 2024-07-06 | [40890](https://github.com/airbytehq/airbyte/pull/40890) | Update dependencies |
| 0.1.9 | 2024-06-26 | [40374](https://github.com/airbytehq/airbyte/pull/40374) | Update dependencies |
| 0.1.8 | 2024-06-22 | [40175](https://github.com/airbytehq/airbyte/pull/40175) | Update dependencies |
| 0.1.7 | 2024-06-06 | [39226](https://github.com/airbytehq/airbyte/pull/39226) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.6 | 2024-05-28 | [38596](https://github.com/airbytehq/airbyte/pull/38596) | Make connector compatible with builder |
| 0.1.5 | 2024-04-19 | [37169](https://github.com/airbytehq/airbyte/pull/37169) | Updating to 0.80.0 CDK |
| 0.1.4 | 2024-04-18 | [37169](https://github.com/airbytehq/airbyte/pull/37169) | Manage dependencies with Poetry. |
| 0.1.3 | 2024-04-15 | [37169](https://github.com/airbytehq/airbyte/pull/37169) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.2 | 2024-04-12 | [37169](https://github.com/airbytehq/airbyte/pull/37169) | schema descriptions |
| 0.1.1 | 2024-02-05 | [34847](https://github.com/airbytehq/airbyte/pull/34847) | Adjust stream schemas and make ready for airbyte-lib |
| 0.1.0 | 2022-10-27 | [18819](https://github.com/airbytehq/airbyte/pull/18819) | Add Gong Source Connector |

</details>
