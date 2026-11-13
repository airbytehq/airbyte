# Chargify

This page contains the setup guide and reference information for the Chargify source connector. Chargify is now called Maxio Advanced Billing, and its API documentation is hosted on the [Maxio developer portal](https://developers.maxio.com/http/getting-started/how-to-get-started).

## Prerequisites

- A Chargify (Maxio Advanced Billing) site
- An API key for that site. Managing API keys requires the **manages product catalog, settings, and integrations** permission, which admins have by default.

## Setup guide

### Step 1: Create an API key

1. In Chargify, select **Config** > **Integrations** > **API Keys**.
2. Click **New API Key**, optionally enter a description, and click **Create**.
3. Copy the key.

For more information, see [Manage Advanced Billing API Keys](https://docs.maxio.com/configuration/advanced-billing/advanced-billing-api-keys).

### Step 2: Set up the connector in Airbyte

1. In Airbyte, create a new source and select **Chargify**.
2. For **API Key**, enter the API key you created.
3. For **Domain**, enter the hostname of your Chargify site without `https://` or a trailing path, for example `acme.chargify.com`. The connector sends requests to `https://<domain>/`.
4. For **Username**, enter any value. This field is required, but the connector doesn't use it. The connector authenticates with HTTP Basic authentication, using the API key as the username and `x` as the password.
5. Leave **Password** empty. The connector doesn't use it.
6. Click **Set up source**.

## Supported sync modes

The Chargify source connector supports the following sync modes:

- [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite)
- [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append)

The connector doesn't support incremental syncs, so each sync reads every record from every selected stream.

## Supported streams

| Stream | Primary key | API endpoint |
| :----- | :---------- | :----------- |
| customers | `id` | [List customers](https://developers.maxio.com/http/advanced-billing-api/api-endpoints/customers/list-customers) |
| subscriptions | `id` | [List subscriptions](https://developers.maxio.com/http/advanced-billing-api/api-endpoints/subscriptions/list-subscriptions) |
| invoices | `uid` | [List invoices](https://developers.maxio.com/http/advanced-billing-api/api-endpoints/invoices/list-invoices) |
| coupons | `id` | [List coupons](https://developers.maxio.com/http/advanced-billing-api/api-endpoints/coupons/list-coupons) |
| transactions | `id` | Transactions |

All streams use page-number pagination with 200 records per page.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                     |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------ |
| 0.5.23 | 2026-11-10 | [91317](https://github.com/airbytehq/airbyte/pull/91317) | Upgrade base image to `source-declarative-manifest:7.47.0` |
| 0.5.22 | 2025-05-10 | [59941](https://github.com/airbytehq/airbyte/pull/59941) | Update dependencies |
| 0.5.21 | 2025-05-03 | [59395](https://github.com/airbytehq/airbyte/pull/59395) | Update dependencies |
| 0.5.20 | 2025-04-26 | [58707](https://github.com/airbytehq/airbyte/pull/58707) | Update dependencies |
| 0.5.19 | 2025-04-19 | [58365](https://github.com/airbytehq/airbyte/pull/58365) | Update dependencies |
| 0.5.18 | 2025-04-12 | [57796](https://github.com/airbytehq/airbyte/pull/57796) | Update dependencies |
| 0.5.17 | 2025-04-05 | [57153](https://github.com/airbytehq/airbyte/pull/57153) | Update dependencies |
| 0.5.16 | 2025-03-29 | [56610](https://github.com/airbytehq/airbyte/pull/56610) | Update dependencies |
| 0.5.15 | 2025-03-22 | [56094](https://github.com/airbytehq/airbyte/pull/56094) | Update dependencies |
| 0.5.14 | 2025-03-08 | [55413](https://github.com/airbytehq/airbyte/pull/55413) | Update dependencies |
| 0.5.13 | 2025-03-01 | [54845](https://github.com/airbytehq/airbyte/pull/54845) | Update dependencies |
| 0.5.12 | 2025-02-22 | [54242](https://github.com/airbytehq/airbyte/pull/54242) | Update dependencies |
| 0.5.11 | 2025-02-15 | [53890](https://github.com/airbytehq/airbyte/pull/53890) | Update dependencies |
| 0.5.10 | 2025-02-08 | [53438](https://github.com/airbytehq/airbyte/pull/53438) | Update dependencies |
| 0.5.9 | 2025-02-01 | [52891](https://github.com/airbytehq/airbyte/pull/52891) | Update dependencies |
| 0.5.8 | 2025-01-25 | [52183](https://github.com/airbytehq/airbyte/pull/52183) | Update dependencies |
| 0.5.7 | 2025-01-18 | [51752](https://github.com/airbytehq/airbyte/pull/51752) | Update dependencies |
| 0.5.6 | 2025-01-11 | [51252](https://github.com/airbytehq/airbyte/pull/51252) | Update dependencies |
| 0.5.5 | 2024-12-28 | [50463](https://github.com/airbytehq/airbyte/pull/50463) | Update dependencies |
| 0.5.4 | 2024-12-21 | [50187](https://github.com/airbytehq/airbyte/pull/50187) | Update dependencies |
| 0.5.3 | 2024-12-14 | [49589](https://github.com/airbytehq/airbyte/pull/49589) | Update dependencies |
| 0.5.2 | 2024-12-12 | [49300](https://github.com/airbytehq/airbyte/pull/49300) | Update dependencies |
| 0.5.1 | 2024-12-11 | [48959](https://github.com/airbytehq/airbyte/pull/48959) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.5.0 | 2024-08-23 | [44602](https://github.com/airbytehq/airbyte/pull/44602) | Refactor connector to manifest-only format |
| 0.4.15 | 2024-08-17 | [44230](https://github.com/airbytehq/airbyte/pull/44230) | Update dependencies |
| 0.4.14 | 2024-08-12 | [43775](https://github.com/airbytehq/airbyte/pull/43775) | Update dependencies |
| 0.4.13 | 2024-08-10 | [43612](https://github.com/airbytehq/airbyte/pull/43612) | Update dependencies |
| 0.4.12 | 2024-08-03 | [43222](https://github.com/airbytehq/airbyte/pull/43222) | Update dependencies |
| 0.4.11 | 2024-07-27 | [42765](https://github.com/airbytehq/airbyte/pull/42765) | Update dependencies |
| 0.4.10 | 2024-07-20 | [42300](https://github.com/airbytehq/airbyte/pull/42300) | Update dependencies |
| 0.4.9 | 2024-07-13 | [41811](https://github.com/airbytehq/airbyte/pull/41811) | Update dependencies |
| 0.4.8 | 2024-07-10 | [41375](https://github.com/airbytehq/airbyte/pull/41375) | Update dependencies |
| 0.4.7 | 2024-07-09 | [41130](https://github.com/airbytehq/airbyte/pull/41130) | Update dependencies |
| 0.4.6 | 2024-07-06 | [40962](https://github.com/airbytehq/airbyte/pull/40962) | Update dependencies |
| 0.4.5 | 2024-06-25 | [40314](https://github.com/airbytehq/airbyte/pull/40314) | Update dependencies |
| 0.4.4 | 2024-06-22 | [40123](https://github.com/airbytehq/airbyte/pull/40123) | Update dependencies |
| 0.4.3 | 2024-06-15 | [38814](https://github.com/airbytehq/airbyte/pull/38814) | Make connector compatible with builder |
| 0.4.2 | 2024-06-06 | [39306](https://github.com/airbytehq/airbyte/pull/39306) | [autopull] Upgrade base image to v1.2.2 |
| 0.4.1 | 2024-05-20 | [38444](https://github.com/airbytehq/airbyte/pull/38444) | [autopull] base image + poetry + up_to_date |
| 0.4.0 | 2023-10-16 | [31116](https://github.com/airbytehq/airbyte/pull/31116) | Add Coupons, Transactions, Invoices Streams |
| 0.3.0 | 2023-08-10 | [29130](https://github.com/airbytehq/airbyte/pull/29130) | Migrate Python CDK to Low Code |
| 0.2.0 | 2023-08-08 | [29218](https://github.com/airbytehq/airbyte/pull/29218) | Fix schema |
| 0.1.0 | 2022-03-16 | [10853](https://github.com/airbytehq/airbyte/pull/10853) | Initial release |

</details>
