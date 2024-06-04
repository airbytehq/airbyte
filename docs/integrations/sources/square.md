# Square

This page contains the setup guide and reference information for the Square source connector.

## Prerequisites

To set up the Square source connector with Airbyte, you'll need to create your Square Application and use Personal token or Oauth access token.

## Setup guide

### Step 1: Set up Square

1. Create [Square Application](https://developer.squareup.com/apps)
2. Obtain [Personal token](https://developer.squareup.com/docs/build-basics/access-tokens) or [Oauth access token](https://developer.squareup.com/docs/oauth-api/create-urls-for-square-authorization).

### Step 2: Set up the Square connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, enter the name for the Square connector and select **Square** from the Source type dropdown.
4. Choose authentication method:
   - Api-Key
     - Fill in API key token with "Access token" from Square Application settings page (Credentials on the left)
   - Oauth authentication
     - Fill in Client ID and Client secret with data from Square Application settings page (Oauth on the left)
     - Fill in refresh token with one obtained during the authentication process
5. Choose if your account is sandbox
6. Choose start date
7. Choose if you would like to include Deleted objects (for streams: Items, Categories, Discounts, Taxes)

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. On the Set up the source page, enter the name for the Square connector and select **Square** from the Source type dropdown.
4. Choose authentication method:
   - Api-Key
     - Fill in API key token with "Access token" from Square Application settings page (Credentials on the left)
   - Oauth authentication
     - Fill in Client ID and Client secret with data from Square Application settings page (Oauth on the left)
     - Fill in refresh token with one obtained during the authentication process
5. Choose if your account is sandbox
6. Choose start date
7. Choose if you would like to include Deleted objects (for streams: Items, Categories, Discounts, Taxes)

## Supported sync modes

The Square source connector supports the following [ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

- [Items](https://developer.squareup.com/explorer/square/catalog-api/search-catalog-objects) \(Incremental\)
- [Categories](https://developer.squareup.com/explorer/square/catalog-api/search-catalog-objects) \(Incremental\)
- [Discounts](https://developer.squareup.com/explorer/square/catalog-api/search-catalog-objects) \(Incremental\)
- [Taxes](https://developer.squareup.com/explorer/square/catalog-api/search-catalog-objects) \(Incremental\)
- [ModifierLists](https://developer.squareup.com/explorer/square/catalog-api/search-catalog-objects) \(Incremental\)
- [Payments](https://developer.squareup.com/reference/square_2022-10-19/payments-api/list-payments) \(Incremental\)
- [Refunds](https://developer.squareup.com/reference/square_2022-10-19/refunds-api/list-payment-refunds) \(Incremental\)
- [Locations](https://developer.squareup.com/explorer/square/locations-api/list-locations)
- [Team Members](https://developer.squareup.com/reference/square_2022-10-19/team-api/search-team-members)
- [List Team Member Wages](https://developer.squareup.com/explorer/square/labor-api/list-team-member-wages)
- [Customers](https://developer.squareup.com/explorer/square/customers-api/list-customers)
- [Shifts](https://developer.squareup.com/reference/square/labor-api/search-shifts)
- [Inventory](https://developer.squareup.com/reference/square/inventory-api/batch-retrieve-inventory-counts)
- [Orders](https://developer.squareup.com/reference/square/orders-api/search-orders)
- [Cash drawers](https://developer.squareup.com/explorer/square/cash-drawers-api/list-cash-drawer-shifts)
- [Loyalty](https://developer.squareup.com/explorer/square/loyalty-api/search-loyalty-accounts)

## Connector-specific features & highlights

Useful links:

- [Square API Explorer](https://developer.squareup.com/explorer/square)
- [Square API Docs](https://developer.squareup.com/reference/square)
- [Square Developer Dashboard](https://developer.squareup.com/apps)

## Performance considerations (if any)

No defined API rate limits were found in Square documentation however considering [this information](https://stackoverflow.com/questions/28033966/whats-the-rate-limit-on-the-square-connect-api/28053836#28053836) it has 10 QPS limits. The connector doesn't handle rate limits exceptions, but no errors were raised during testing.
Exponential [Backoff](https://developer.squareup.com/forums/t/current-square-api-rate-limit/449) strategy recommended.

## Data type map

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `integer`        | `integer`    |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |
| `boolean`        | `boolean`    |       |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                   |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------ |
| 1.6.2   | 2024-05-03 | [37800](https://github.com/airbytehq/airbyte/pull/37800) | Migrate to Poetry. Replace custom components with default classes         |
| 1.6.1   | 2023-11-07 | [31481](https://github.com/airbytehq/airbyte/pull/31481) | Fix duplicate records for `Payments` and `Refunds` stream                 |
| 1.6.0   | 2023-10-18 | [31115](https://github.com/airbytehq/airbyte/pull/31115) | Add `customer_id` field to `Payments` and `Orders` streams                |
| 1.5.0   | 2023-10-16 | [31045](https://github.com/airbytehq/airbyte/pull/31045) | Added New Stream bank_accounts                                            |
| 1.4.0   | 2023-10-13 | [31106](https://github.com/airbytehq/airbyte/pull/31106) | Add new stream Loyalty                                                    |
| 1.3.0   | 2023-10-12 | [31107](https://github.com/airbytehq/airbyte/pull/31107) | Add new stream Inventory                                                  |
| 1.2.0   | 2023-10-10 | [31065](https://github.com/airbytehq/airbyte/pull/31065) | Add new stream Cash drawers shifts                                        |
| 1.1.3   | 2023-10-10 | [30960](https://github.com/airbytehq/airbyte/pull/30960) | Update `airbyte-cdk` version to `>=0.51.31`                               |
| 1.1.2   | 2023-07-10 | [28019](https://github.com/airbytehq/airbyte/pull/28019) | fix display order of spec fields                                          |
| 1.1.1   | 2023-06-28 | [27762](https://github.com/airbytehq/airbyte/pull/27762) | Update following state breaking changes                                   |
| 1.1.0   | 2023-05-24 | [26485](https://github.com/airbytehq/airbyte/pull/26485) | Remove deprecated authSpecification in favour of advancedAuth             |
| 1.0.1   | 2023-05-03 | [25784](https://github.com/airbytehq/airbyte/pull/25784) | Fix Authenticator                                                         |
| 1.0.0   | 2023-05-03 | [25784](https://github.com/airbytehq/airbyte/pull/25784) | Fix Authenticator                                                         |
| 0.2.2   | 2023-03-22 | [22867](https://github.com/airbytehq/airbyte/pull/22867) | Specified date formatting in specification                                |
| 0.2.1   | 2023-03-06 | [23231](https://github.com/airbytehq/airbyte/pull/23231) | Publish using low-code CDK Beta version                                   |
| 0.2.0   | 2022-11-14 | [19369](https://github.com/airbytehq/airbyte/pull/19369) | Migrate to low code (YAML); update API to version 2022-10-19; update docs |
| 0.1.4   | 2021-12-02 | [6842](https://github.com/airbytehq/airbyte/pull/6842)   | Added oauth support                                                       |
| 0.1.3   | 2021-12-06 | [8425](https://github.com/airbytehq/airbyte/pull/8425)   | Update title, description fields in spec                                  |
| 0.1.2   | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499)   | Remove base-python dependencies                                           |
| 0.1.1   | 2021-07-09 | [4645](https://github.com/airbytehq/airbyte/pull/4645)   | Update \_send_request method due to Airbyte CDK changes                   |
| 0.1.0   | 2021-06-30 | [4439](https://github.com/airbytehq/airbyte/pull/4439)   | Initial release supporting the Square API                                 |

</details>