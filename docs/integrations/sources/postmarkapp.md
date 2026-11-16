# Postmarkapp

## Overview

The Postmarkapp source syncs data from the [Postmark API](https://postmarkapp.com/developer). It reads delivery statistics, message streams, outbound messages, and bounces for one Postmark server, plus the domains and servers in your Postmark account.

## Prerequisites

The connector requires two Postmark API tokens. Both are required, because some streams use server-level endpoints and others use account-level endpoints.

- **Server API token** (`X-Postmark-Server-Token`): In Postmark, open the server you want to sync and go to the **API Tokens** tab. The server-level streams read data for this server only.
- **Account API token** (`X-Postmark-Account-Token`): In Postmark, go to the **API Tokens** tab of your account. Only the account owner can access this token.

For details, see [Postmark API authentication](https://postmarkapp.com/developer/api/overview#authentication).

## Setup guide

1. In Airbyte, go to **Sources** and click **New source**.
2. Select **Postmarkapp** from the list of sources.
3. Enter a name for the source.
4. In **X-Postmark-Server-Token**, enter your server API token.
5. In **X-Postmark-Account-Token**, enter your account API token.
6. Click **Set up source**. Airbyte tests the connection by reading the `message-streams` stream.

## Supported streams

| Stream | Postmark endpoint | Token used | Primary key |
| :----- | :---------------- | :--------- | :---------- |
| `deliverystats` | [Get delivery stats](https://postmarkapp.com/developer/api/bounce-api#delivery-stats) | Server | `Name` |
| `message-streams` | [List message streams](https://postmarkapp.com/developer/api/message-streams-api#list-message-streams) | Server | `ID` |
| `messages` | [Outbound message search](https://postmarkapp.com/developer/api/messages-api#outbound-message-search) | Server | `MessageID` |
| `bounces` | [Get bounces](https://postmarkapp.com/developer/api/bounce-api#bounces) | Server | `ID` |
| `domains` | [List domains](https://postmarkapp.com/developer/api/domains-api#list-domains) | Account | `ID` |
| `servers` | [List servers](https://postmarkapp.com/developer/api/servers-api#list-servers) | Account | `ID` |

The `deliverystats` stream returns one record per bounce type, with the count of bounces of that type for the server.

## Supported sync modes

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| Namespaces        | No         |

## Limitations

- **Message retention**: Postmark keeps outbound messages and bounces only for your server's retention period, which is 45 days by default and configurable from 7 to 365 days. The `messages` and `bounces` streams can't return records older than that.
- **10,000-record search limit**: The Postmark outbound message search and bounce search endpoints return at most 10,000 records per search. The connector doesn't filter these searches by date, so if a server has more than 10,000 retained messages or bounces, the `messages` and `bounces` streams can't read all of them.
- **Pagination**: The connector requests 500 records per page, the maximum Postmark allows.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.2.11 | 2026-11-13 | [91434](https://github.com/airbytehq/airbyte/pull/91434) | Upgrade to `source-declarative-manifest` 7.47.0 and fix offset pagination so every stream starts at the first record and stops on a short page |
| 0.2.10 | 2025-02-15 | [53947](https://github.com/airbytehq/airbyte/pull/53947) | Update dependencies |
| 0.2.9 | 2025-02-08 | [53462](https://github.com/airbytehq/airbyte/pull/53462) | Update dependencies |
| 0.2.8 | 2025-02-01 | [52967](https://github.com/airbytehq/airbyte/pull/52967) | Update dependencies |
| 0.2.7 | 2025-01-25 | [51879](https://github.com/airbytehq/airbyte/pull/51879) | Update dependencies |
| 0.2.6 | 2025-01-11 | [51372](https://github.com/airbytehq/airbyte/pull/51372) | Update dependencies |
| 0.2.5 | 2024-12-28 | [50703](https://github.com/airbytehq/airbyte/pull/50703) | Update dependencies |
| 0.2.4 | 2024-12-21 | [50281](https://github.com/airbytehq/airbyte/pull/50281) | Update dependencies |
| 0.2.3 | 2024-12-14 | [49667](https://github.com/airbytehq/airbyte/pull/49667) | Update dependencies |
| 0.2.2 | 2024-12-12 | [49046](https://github.com/airbytehq/airbyte/pull/49046) | Update dependencies |
| 0.2.1 | 2024-10-28 | [47539](https://github.com/airbytehq/airbyte/pull/47539) | Update dependencies |
| 0.2.0 | 2024-10-06 | [46522](https://github.com/airbytehq/airbyte/pull/46522) | Migrate to Manifest-only |
| 0.1.21 | 2024-10-05 | [46509](https://github.com/airbytehq/airbyte/pull/46509) | Update dependencies |
| 0.1.20 | 2024-09-28 | [45793](https://github.com/airbytehq/airbyte/pull/45793) | Update dependencies |
| 0.1.19 | 2024-09-14 | [45535](https://github.com/airbytehq/airbyte/pull/45535) | Update dependencies |
| 0.1.18 | 2024-09-07 | [45259](https://github.com/airbytehq/airbyte/pull/45259) | Update dependencies |
| 0.1.17 | 2024-08-31 | [44975](https://github.com/airbytehq/airbyte/pull/44975) | Update dependencies |
| 0.1.16 | 2024-08-24 | [44705](https://github.com/airbytehq/airbyte/pull/44705) | Update dependencies |
| 0.1.15 | 2024-08-17 | [44309](https://github.com/airbytehq/airbyte/pull/44309) | Update dependencies |
| 0.1.14 | 2024-08-10 | [43592](https://github.com/airbytehq/airbyte/pull/43592) | Update dependencies |
| 0.1.13 | 2024-08-03 | [43265](https://github.com/airbytehq/airbyte/pull/43265) | Update dependencies |
| 0.1.12 | 2024-07-27 | [42648](https://github.com/airbytehq/airbyte/pull/42648) | Update dependencies |
| 0.1.11 | 2024-07-20 | [42190](https://github.com/airbytehq/airbyte/pull/42190) | Update dependencies |
| 0.1.10 | 2024-07-13 | [41820](https://github.com/airbytehq/airbyte/pull/41820) | Update dependencies |
| 0.1.9 | 2024-07-10 | [41564](https://github.com/airbytehq/airbyte/pull/41564) | Update dependencies |
| 0.1.8 | 2024-07-09 | [41184](https://github.com/airbytehq/airbyte/pull/41184) | Update dependencies |
| 0.1.7 | 2024-07-06 | [40762](https://github.com/airbytehq/airbyte/pull/40762) | Update dependencies |
| 0.1.6 | 2024-06-25 | [40483](https://github.com/airbytehq/airbyte/pull/40483) | Update dependencies |
| 0.1.5 | 2024-06-22 | [39970](https://github.com/airbytehq/airbyte/pull/39970) | Update dependencies |
| 0.1.4 | 2024-06-04 | [39062](https://github.com/airbytehq/airbyte/pull/39062) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.3 | 2024-04-19 | [37232](https://github.com/airbytehq/airbyte/pull/37232) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry. |
| 0.1.2 | 2024-04-15 | [37232](https://github.com/airbytehq/airbyte/pull/37232) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1 | 2024-04-12 | [37232](https://github.com/airbytehq/airbyte/pull/37232) | schema descriptions |
| 0.1.0   | 2022-11-09 | 18220                                                    | 🎉 New Source: Postmarkapp API [low-code CDK]                                   |

</details>
