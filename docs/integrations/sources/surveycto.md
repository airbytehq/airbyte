# SurveyCTO

This page guides you through the process of setting up the SurveyCTO source connector.

## Prerequisites

- Server Name `The name of the ServerCTO server`
- Your SurveyCTO `Username`
- Your SurveyCTO `Password`
- Form ID `Unique Identifier for one of your forms`
- Start Date `Start Date default`

## How to setup a SurveyCTO Account

- create the account
- create your form
- publish your form
- give your user an API consumer permission to the existing role or create a user with that role and permission.

## Set up the SurveyCTO source connection

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Survey CTO** from the Source type dropdown.
4. Enter a name for your source.
5. Enter a Server name for your SurveyCTO account.
6. Enter a Username for SurveyCTO account.
7. Enter a Password for SurveyCTO account.
8. Form ID's (We can multiple forms id here to pull from)
9. Start Date (This can be pass to pull the data from particular date)
10. Click **Set up source**.

## Supported sync modes

The SurveyCTO source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- (Recommended)[ Incremental Sync - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

The SurveyCTO source connector supports the following streams:

- Surveycto

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                    |
| ------- | ---------- | -------------------------------------------------------- | -------------------------- |
| 0.1.22 | 2024-09-28 | [46112](https://github.com/airbytehq/airbyte/pull/46112) | Update dependencies |
| 0.1.21 | 2024-09-21 | [45818](https://github.com/airbytehq/airbyte/pull/45818) | Update dependencies |
| 0.1.20 | 2024-09-14 | [45551](https://github.com/airbytehq/airbyte/pull/45551) | Update dependencies |
| 0.1.19 | 2024-09-07 | [45258](https://github.com/airbytehq/airbyte/pull/45258) | Update dependencies |
| 0.1.18 | 2024-08-31 | [45026](https://github.com/airbytehq/airbyte/pull/45026) | Update dependencies |
| 0.1.17 | 2024-08-24 | [44743](https://github.com/airbytehq/airbyte/pull/44743) | Update dependencies |
| 0.1.16 | 2024-08-17 | [44345](https://github.com/airbytehq/airbyte/pull/44345) | Update dependencies |
| 0.1.15 | 2024-08-10 | [43478](https://github.com/airbytehq/airbyte/pull/43478) | Update dependencies |
| 0.1.14 | 2024-08-03 | [43190](https://github.com/airbytehq/airbyte/pull/43190) | Update dependencies |
| 0.1.13 | 2024-07-27 | [42602](https://github.com/airbytehq/airbyte/pull/42602) | Update dependencies |
| 0.1.12 | 2024-07-20 | [42309](https://github.com/airbytehq/airbyte/pull/42309) | Update dependencies |
| 0.1.11 | 2024-07-13 | [41743](https://github.com/airbytehq/airbyte/pull/41743) | Update dependencies |
| 0.1.10 | 2024-07-10 | [41597](https://github.com/airbytehq/airbyte/pull/41597) | Update dependencies |
| 0.1.9 | 2024-07-09 | [41117](https://github.com/airbytehq/airbyte/pull/41117) | Update dependencies |
| 0.1.8 | 2024-07-06 | [40782](https://github.com/airbytehq/airbyte/pull/40782) | Update dependencies |
| 0.1.7 | 2024-06-26 | [40531](https://github.com/airbytehq/airbyte/pull/40531) | Update dependencies |
| 0.1.6 | 2024-06-25 | [40466](https://github.com/airbytehq/airbyte/pull/40466) | Update dependencies |
| 0.1.5 | 2024-06-22 | [40130](https://github.com/airbytehq/airbyte/pull/40130) | Update dependencies |
| 0.1.4 | 2024-06-04 | [38993](https://github.com/airbytehq/airbyte/pull/38993) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.3 | 2024-05-20 | [38439](https://github.com/airbytehq/airbyte/pull/38439) | [autopull] base image + poetry + up_to_date |
| 0.1.2 | 2023-07-27 | [28512](https://github.com/airbytehq/airbyte/pull/28512) | Added Check Connection |
| 0.1.1 | 2023-04-25 | [24784](https://github.com/airbytehq/airbyte/pull/24784) | Fix incremental sync |
| 0.1.0 | 2022-11-16 | [19371](https://github.com/airbytehq/airbyte/pull/19371) | SurveyCTO Source Connector |

</details>
