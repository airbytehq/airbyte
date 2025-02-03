# Appfollow

This page guides you through setting up the Appfollow source connector to sync data for the [Appfollow API](https://appfollow.docs.apiary.io/#introduction/api-methods).

## Prerequisite

To set up the Appfollow source connector, you'll need your Appfollow `ext_id`, `cid`, `api_secret` and `Country`.

## Set up the Appfollow source connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Appfollow** from the Source type dropdown.
4. Enter a name for your source.
5. For **ext_id**, **cid**, **api_secret** and **Country**, enter the Appfollow ext_id, cid, api_secret and country.
6. Click **Set up source**.

## Supported Streams

The Appfollow source connector supports the following streams:

- [Ratings](https://appfollow.docs.apiary.io/#reference/0/9.-ratings) \(Full Refresh sync\)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

## Supported sync modes

The Appfollow source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh

## Performance considerations

The Appfollow connector ideally should gracefully handle Appfollow API limitations under normal usage. [Create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                 |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------------------- |
| 1.1.8 | 2025-02-01 | [52942](https://github.com/airbytehq/airbyte/pull/52942) | Update dependencies |
| 1.1.7 | 2025-01-25 | [52217](https://github.com/airbytehq/airbyte/pull/52217) | Update dependencies |
| 1.1.6 | 2025-01-18 | [51711](https://github.com/airbytehq/airbyte/pull/51711) | Update dependencies |
| 1.1.5 | 2025-01-11 | [51290](https://github.com/airbytehq/airbyte/pull/51290) | Update dependencies |
| 1.1.4 | 2024-12-28 | [50477](https://github.com/airbytehq/airbyte/pull/50477) | Update dependencies |
| 1.1.3 | 2024-12-21 | [50186](https://github.com/airbytehq/airbyte/pull/50186) | Update dependencies |
| 1.1.2 | 2024-12-14 | [49557](https://github.com/airbytehq/airbyte/pull/49557) | Update dependencies |
| 1.1.1 | 2024-12-12 | [47742](https://github.com/airbytehq/airbyte/pull/47742) | Update dependencies |
| 1.1.0 | 2024-08-23 | [44598](https://github.com/airbytehq/airbyte/pull/44598) | Refactor connector to manifest-only format |
| 1.0.12 | 2024-08-17 | [44338](https://github.com/airbytehq/airbyte/pull/44338) | Update dependencies |
| 1.0.11 | 2024-08-12 | [43931](https://github.com/airbytehq/airbyte/pull/43931) | Update dependencies |
| 1.0.10 | 2024-08-10 | [43681](https://github.com/airbytehq/airbyte/pull/43681) | Update dependencies |
| 1.0.9 | 2024-08-03 | [43293](https://github.com/airbytehq/airbyte/pull/43293) | Update dependencies |
| 1.0.8 | 2024-07-27 | [42387](https://github.com/airbytehq/airbyte/pull/42387) | Update dependencies |
| 1.0.7 | 2024-07-13 | [41372](https://github.com/airbytehq/airbyte/pull/41372) | Update dependencies |
| 1.0.6 | 2024-07-09 | [41234](https://github.com/airbytehq/airbyte/pull/41234) | Update dependencies |
| 1.0.5 | 2024-07-06 | [40793](https://github.com/airbytehq/airbyte/pull/40793) | Update dependencies |
| 1.0.4 | 2024-06-25 | [40284](https://github.com/airbytehq/airbyte/pull/40284) | Update dependencies |
| 1.0.3 | 2024-06-22 | [40014](https://github.com/airbytehq/airbyte/pull/40014) | Update dependencies |
| 1.0.2 | 2024-06-04 | [38966](https://github.com/airbytehq/airbyte/pull/38966) | [autopull] Upgrade base image to v1.2.1 |
| 1.0.1 | 2024-05-20 | [38388](https://github.com/airbytehq/airbyte/pull/38388) | [autopull] base image + poetry + up_to_date |
| 1.0.0 | 2023-08-05 | [29128](https://github.com/airbytehq/airbyte/pull/29128) | Migrate to low-code and add new streams |
| 0.1.1 | 2022-08-11 | [14418](https://github.com/airbytehq/airbyte/pull/14418) | New Source: Appfollow |

</details>
