# Klarna

This page contains the setup guide and reference information for the Klarna source connector.

## Prerequisites

The [Klarna Settlements API](https://developers.klarna.com/api/#settlements-api) is used to get the payouts and transactions for a Klarna account.

## Setup guide

### Step 1: Set up Klarna

In order to get an `Username (UID)` and `Password` please go to [this](https://docs.klarna.com/) page here you should find **Merchant Portal** button. Using this button you could log in to your production / playground in proper region. After registration / login you may find and create `Username (UID)` and `Password` in settings tab.

:::note

Klarna Source Connector does not support OAuth at this time due to limitations outside of control.

:::

## Step 2: Set up the Klarna connector in Airbyte

### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard
2. Set the name for your source
3. Choose if your account is sandbox
4. Enter your username
5. Enter your password
6. Enter the date you want your sync to start from
7. Click **Set up source**

## Supported sync modes

The Klarna source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | No         |

## Supported Streams

This Source is capable of syncing the following Klarna Settlements Streams:

- [Payouts](https://developers.klarna.com/api/#settlements-api-get-all-payouts)
- [Transactions](https://developers.klarna.com/api/#settlements-api-get-transactions)

## Performance considerations

Klarna API has [rate limiting](https://developers.klarna.com/api/#api-rate-limiting)

**Production environments**: the API rate limit is 20 create-sessions per second on average measured over a 1-minute period. For the other operations, the API limit is 200 requests per second on average, measured over a 1 minute period
**Playground environments**: the API rate limit is one quarter (1/4th) of the rate limits of production environments.

Connector will handle an issue with rate limiting as Klarna returns 429 status code when limits are reached

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.3.8 | 2025-01-11 | [51169](https://github.com/airbytehq/airbyte/pull/51169) | Update dependencies |
| 0.3.7 | 2024-12-28 | [50659](https://github.com/airbytehq/airbyte/pull/50659) | Update dependencies |
| 0.3.6 | 2024-12-21 | [50146](https://github.com/airbytehq/airbyte/pull/50146) | Update dependencies |
| 0.3.5 | 2024-12-14 | [49639](https://github.com/airbytehq/airbyte/pull/49639) | Update dependencies |
| 0.3.4 | 2024-12-12 | [49230](https://github.com/airbytehq/airbyte/pull/49230) | Update dependencies |
| 0.3.3 | 2024-10-29 | [47478](https://github.com/airbytehq/airbyte/pull/47478) | Update dependencies |
| 0.3.2 | 2024-10-21 | [47195](https://github.com/airbytehq/airbyte/pull/47195) | Update dependencies |
| 0.3.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.3.0 | 2024-08-15 | [44136](https://github.com/airbytehq/airbyte/pull/44136) | Refactor connector to manifest-only format |
| 0.2.16 | 2024-08-10 | [43550](https://github.com/airbytehq/airbyte/pull/43550) | Update dependencies |
| 0.2.15 | 2024-08-03 | [43266](https://github.com/airbytehq/airbyte/pull/43266) | Update dependencies |
| 0.2.14 | 2024-07-27 | [42818](https://github.com/airbytehq/airbyte/pull/42818) | Update dependencies |
| 0.2.13 | 2024-07-20 | [42276](https://github.com/airbytehq/airbyte/pull/42276) | Update dependencies |
| 0.2.12 | 2024-07-13 | [41874](https://github.com/airbytehq/airbyte/pull/41874) | Update dependencies |
| 0.2.11 | 2024-07-10 | [41483](https://github.com/airbytehq/airbyte/pull/41483) | Update dependencies |
| 0.2.10 | 2024-07-09 | [41267](https://github.com/airbytehq/airbyte/pull/41267) | Update dependencies |
| 0.2.9 | 2024-07-06 | [40819](https://github.com/airbytehq/airbyte/pull/40819) | Update dependencies |
| 0.2.8 | 2024-06-25 | [40504](https://github.com/airbytehq/airbyte/pull/40504) | Update dependencies |
| 0.2.7 | 2024-06-22 | [40151](https://github.com/airbytehq/airbyte/pull/40151) | Update dependencies |
| 0.2.6 | 2024-06-07 | [38709](https://github.com/airbytehq/airbyte/pull/38709) | Updating US endpoints |
| 0.2.5 | 2024-06-04 | [39045](https://github.com/airbytehq/airbyte/pull/39045) | [autopull] Upgrade base image to v1.2.1 |
| 0.2.4 | 2024-04-19 | [37182](https://github.com/airbytehq/airbyte/pull/37182) | Updating to 0.80.0 CDK |
| 0.2.3 | 2024-04-18 | [37182](https://github.com/airbytehq/airbyte/pull/37182) | Manage dependencies with Poetry. |
| 0.2.2 | 2024-04-15 | [37182](https://github.com/airbytehq/airbyte/pull/37182) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.1 | 2024-04-12 | [37182](https://github.com/airbytehq/airbyte/pull/37182) | schema descriptions |
| 0.2.0 | 2023-10-23 | [31003](https://github.com/airbytehq/airbyte/pull/31003) | Migrate to low-code |
| 0.1.0 | 2022-10-24 | [18385](https://github.com/airbytehq/airbyte/pull/18385) | Klarna Settlements Payout and Transactions API |

</details>
