# Braintree

This page contains the setup guide and reference information for the [Braintree](https://www.braintreepayments.com/) source connector.

## Prerequisites

To set up the Braintree source connector, you need the following [Braintree API credentials](https://developer.paypal.com/braintree/articles/control-panel/important-gateway-credentials#api-credentials):

- [Merchant ID](https://developer.paypal.com/braintree/articles/control-panel/important-gateway-credentials#merchant-id)
- [Public key](https://developer.paypal.com/braintree/articles/control-panel/important-gateway-credentials#public-key)
- [Private key](https://developer.paypal.com/braintree/articles/control-panel/important-gateway-credentials#private-key)
- The [environment](https://developer.paypal.com/braintree/articles/control-panel/important-gateway-credentials#environment) the credentials belong to: production or sandbox

Braintree API keys belong to an individual Control Panel user and have the same [role permissions](https://developer.paypal.com/braintree/articles/control-panel/users-roles/role-permissions) as that user. Braintree doesn't offer a separate read-only key type. Production and sandbox gateways each have their own merchant ID and API keys, so use credentials from the same environment you select in Airbyte.

Braintree [recommends](https://developer.paypal.com/braintree/docs/start/go-live/python#create-an-api-user) creating a dedicated API user, rather than using an individual employee's keys, so that the connection doesn't break if that employee's user is suspended or deleted. If you use a custom role instead of Account Admin, the role needs permissions that allow the API searches the connector runs. For example:

| Stream        | Role permission                                 |
| :------------ | :---------------------------------------------- |
| Transactions  | Download Transactions with Masked Payment Data  |
| Customers     | Download Vault Records with Masked Payment Data |
| Subscriptions | Download Subscription Records                   |

If a stream fails with an authorization error, check the role permissions of the user that owns the API keys.

### Find your credentials

1. Log in to the [production](https://www.braintreegateway.com/login) or [sandbox](https://sandbox.braintreegateway.com/login) Control Panel as the user whose API keys you want to use.
2. Click the gear icon in the top-right corner, then click **Business**. Your merchant ID is at the top of the page. It's also the string that follows `/merchants/` in the Control Panel URL.
3. Click the gear icon, then click **API**. Scroll to **API Keys**. If no keys appear, click **Generate New API Key**.
4. Copy the public key. In the **Private Key** column, click **View** to reveal the private key, then copy it.

## Set up the Braintree connector in Airbyte

1. In Airbyte, click **Sources**, then click **New source**.
2. Select **Braintree**.
3. Enter a name for the source.
4. For **Merchant ID**, enter your Braintree merchant ID. This is the gateway-wide merchant ID, not a merchant account ID.
5. For **Public Key**, enter your Braintree public key.
6. For **Private Key**, enter your Braintree private key.
7. For **Start Date**, enter a UTC date and time in the format `YYYY-MM-DDTHH:mm:ssZ`, for example `2024-01-01T00:00:00Z`. The Customers, Disputes, Subscriptions, and Transactions streams only sync records on or after this date. The other streams ignore it.
8. For **Environment**, select **Production** or **Sandbox** to match your credentials. The **Development** option sends requests to `localhost:3000` and the **Qa** option sends requests to Braintree's QA gateway, so they aren't useful for most users.
9. Click **Set up source**.

## Supported sync modes

The Braintree source connector supports the following sync modes:

- [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite)
- [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped)

Incremental sync is only available for some streams. See the table in the next section.

## Supported streams

| Stream | Braintree resource | Primary key | Incremental | Cursor field |
| :----- | :----------------- | :---------- | :---------- | :----------- |
| `customer_stream` | [Customer](https://developer.paypal.com/braintree/docs/reference/request/customer/search) | `id` | Yes | `created_at` |
| `discount_stream` | [Discount](https://developer.paypal.com/braintree/docs/reference/response/discount) | `id` | No | None |
| `dispute_stream` | [Dispute](https://developer.paypal.com/braintree/docs/reference/request/dispute/search) | `id` | Yes | `received_date` |
| `merchant_account_stream` | [Merchant account](https://developer.paypal.com/braintree/docs/reference/response/merchant-account) | `id` | No | None |
| `plan_stream` | [Plan](https://developer.paypal.com/braintree/docs/reference/response/plan) | `id` | No | None |
| `subscription_stream` | [Subscription](https://developer.paypal.com/braintree/docs/reference/request/subscription/search) | `id` | Yes | `created_at` |
| `transaction_stream` | [Transaction](https://developer.paypal.com/braintree/docs/reference/request/transaction/search) | `id` | Yes | `created_at` |

The incremental streams filter on the date a record was created, or for disputes, the date it was received. Incremental syncs don't pick up later updates to records that were already synced, such as a transaction's status changing from authorized to settled. To capture those changes, run a full refresh sync.

## Limitations and performance considerations

- Braintree caps the number of records a single search returns: 50,000 for transaction searches and 10,000 for all other searches. For details, see [Search limit](https://developer.paypal.com/braintree/docs/reference/general/searching/search-results/python#search-limit).
- Braintree doesn't publish fixed rate limits. It returns a [Too Many Requests error](https://developer.paypal.com/braintree/docs/reference/general/exceptions/python#too-many-requests-error) when request volume for an account reaches unsafe levels. The connector should not run into these limits under normal usage. If you see rate limit errors that aren't retried successfully, [create an issue](https://github.com/airbytehq/airbyte/issues).

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                              |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------- |
| 0.3.50 | 2026-11-03 | [90880](https://github.com/airbytehq/airbyte/pull/90880) | Upgrade base image to python-connector-base 4.0.2 (Python 3.11) and airbyte-cdk to 1.x, since airbyte-cdk 0.50 cannot run on Python 3.11 |
| 0.3.49 | 2026-11-03 | [90476](https://github.com/airbytehq/airbyte/pull/90476) | Update dependencies |
| 0.3.48 | 2026-10-27 | [89807](https://github.com/airbytehq/airbyte/pull/89807) | Update dependencies |
| 0.3.47 | 2026-10-20 | [89116](https://github.com/airbytehq/airbyte/pull/89116) | Update dependencies |
| 0.3.46 | 2026-10-13 | [88530](https://github.com/airbytehq/airbyte/pull/88530) | Update dependencies |
| 0.3.45 | 2026-10-06 | [87755](https://github.com/airbytehq/airbyte/pull/87755) | Update dependencies |
| 0.3.44 | 2026-09-29 | [87077](https://github.com/airbytehq/airbyte/pull/87077) | Update dependencies |
| 0.3.43 | 2026-09-22 | [86546](https://github.com/airbytehq/airbyte/pull/86546) | Update dependencies |
| 0.3.42 | 2026-09-15 | [85966](https://github.com/airbytehq/airbyte/pull/85966) | Update dependencies |
| 0.3.41 | 2026-09-01 | [85242](https://github.com/airbytehq/airbyte/pull/85242) | Update dependencies |
| 0.3.40 | 2026-08-25 | [85008](https://github.com/airbytehq/airbyte/pull/85008) | Update dependencies |
| 0.3.39 | 2026-08-18 | [84498](https://github.com/airbytehq/airbyte/pull/84498) | Update dependencies |
| 0.3.38 | 2026-08-11 | [83845](https://github.com/airbytehq/airbyte/pull/83845) | Update dependencies |
| 0.3.37 | 2026-08-04 | [83373](https://github.com/airbytehq/airbyte/pull/83373) | Update dependencies |
| 0.3.36 | 2026-07-28 | [82804](https://github.com/airbytehq/airbyte/pull/82804) | Update dependencies |
| 0.3.35 | 2026-07-14 | [81738](https://github.com/airbytehq/airbyte/pull/81738) | Update dependencies |
| 0.3.34 | 2026-07-07 | [81438](https://github.com/airbytehq/airbyte/pull/81438) | Update dependencies |
| 0.3.33 | 2026-06-23 | [80373](https://github.com/airbytehq/airbyte/pull/80373) | Update dependencies |
| 0.3.32 | 2026-06-09 | [79226](https://github.com/airbytehq/airbyte/pull/79226) | Update dependencies |
| 0.3.31 | 2026-06-02 | [78571](https://github.com/airbytehq/airbyte/pull/78571) | Update dependencies |
| 0.3.30 | 2026-04-28 | [77150](https://github.com/airbytehq/airbyte/pull/77150) | Update dependencies |
| 0.3.29 | 2026-04-21 | [65051](https://github.com/airbytehq/airbyte/pull/65051) | Update dependencies |
| 0.3.28 | 2025-02-01 | [52894](https://github.com/airbytehq/airbyte/pull/52894) | Update dependencies |
| 0.3.27 | 2025-01-25 | [51769](https://github.com/airbytehq/airbyte/pull/51769) | Update dependencies |
| 0.3.26 | 2025-01-11 | [51238](https://github.com/airbytehq/airbyte/pull/51238) | Update dependencies |
| 0.3.25 | 2024-12-28 | [50500](https://github.com/airbytehq/airbyte/pull/50500) | Update dependencies |
| 0.3.24 | 2024-12-21 | [50211](https://github.com/airbytehq/airbyte/pull/50211) | Update dependencies |
| 0.3.23 | 2024-12-14 | [49556](https://github.com/airbytehq/airbyte/pull/49556) | Update dependencies |
| 0.3.22 | 2024-12-12 | [49032](https://github.com/airbytehq/airbyte/pull/49032) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.3.21 | 2024-11-04 | [48212](https://github.com/airbytehq/airbyte/pull/48212) | Update dependencies |
| 0.3.20 | 2024-10-21 | [47062](https://github.com/airbytehq/airbyte/pull/47062) | Update dependencies |
| 0.3.19 | 2024-10-12 | [46849](https://github.com/airbytehq/airbyte/pull/46849) | Update dependencies |
| 0.3.18 | 2024-10-05 | [46496](https://github.com/airbytehq/airbyte/pull/46496) | Update dependencies |
| 0.3.17 | 2024-09-28 | [46180](https://github.com/airbytehq/airbyte/pull/46180) | Update dependencies |
| 0.3.16 | 2024-09-21 | [45810](https://github.com/airbytehq/airbyte/pull/45810) | Update dependencies |
| 0.3.15 | 2024-09-14 | [45555](https://github.com/airbytehq/airbyte/pull/45555) | Update dependencies |
| 0.3.14 | 2024-09-07 | [45310](https://github.com/airbytehq/airbyte/pull/45310) | Update dependencies |
| 0.3.13 | 2024-08-31 | [45041](https://github.com/airbytehq/airbyte/pull/45041) | Update dependencies |
| 0.3.12 | 2024-08-24 | [44287](https://github.com/airbytehq/airbyte/pull/44287) | Update dependencies |
| 0.3.11 | 2024-08-12 | [43953](https://github.com/airbytehq/airbyte/pull/43953) | Corrects timezone handling |
| 0.3.10 | 2024-08-10 | [43666](https://github.com/airbytehq/airbyte/pull/43666) | Update dependencies |
| 0.3.9 | 2024-08-03 | [43225](https://github.com/airbytehq/airbyte/pull/43225) | Update dependencies |
| 0.3.8 | 2024-07-29 | [42848](https://github.com/airbytehq/airbyte/pull/42848) | Corrects pagination issues |
| 0.3.7 | 2024-07-27 | [42796](https://github.com/airbytehq/airbyte/pull/42796) | Update dependencies |
| 0.3.6 | 2024-07-20 | [42372](https://github.com/airbytehq/airbyte/pull/42372) | Update dependencies |
| 0.3.5 | 2024-07-18 | [42096](https://github.com/airbytehq/airbyte/pull/42096) | Adds pagination to get more than 50 records per sync |
| 0.3.4 | 2024-07-13 | [41340](https://github.com/airbytehq/airbyte/pull/41340) | Update dependencies |
| 0.3.3 | 2024-07-09 | [41312](https://github.com/airbytehq/airbyte/pull/41312) | Update dependencies |
| 0.3.2 | 2024-07-06 | [40863](https://github.com/airbytehq/airbyte/pull/40863) | Update dependencies |
| 0.3.1 | 2024-07-02 | [40693](https://github.com/airbytehq/airbyte/pull/40693) | Corrects subscription stream fields |
| 0.2.1 | 2023-11-08 | [31489](https://github.com/airbytehq/airbyte/pull/31489) | Fix transaction stream custom fields |
| 0.2.0 | 2023-07-17 | [29200](https://github.com/airbytehq/airbyte/pull/29200) | Migrate connector to low-code framework |
| 0.1.5 | 2023-05-24 | [26340](https://github.com/airbytehq/airbyte/pull/26340) | Fix error in `check_connection` in integration tests |
| 0.1.4 | 2023-03-13 | [23548](https://github.com/airbytehq/airbyte/pull/23548) | Update braintree python library version to 4.18.1 |
| 0.1.3 | 2021-12-23 | [8434](https://github.com/airbytehq/airbyte/pull/8434) | Update fields in source-connectors specifications |
| 0.1.2 | 2021-12-22 | [9042](https://github.com/airbytehq/airbyte/pull/9042) | Fix `$ref` in schema and spec |
| 0.1.1 | 2021-10-27 | [7432](https://github.com/airbytehq/airbyte/pull/7432) | Dispute model should accept multiple Evidences |
| 0.1.0 | 2021-08-17 | [5362](https://github.com/airbytehq/airbyte/pull/5362) | Initial version |

</details>
