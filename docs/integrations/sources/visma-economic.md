# Visma e-conomic

## Sync overview

This source collects data from [Visma e-conomic](https://developer.visma.com/api/e-conomic/).
At the moment the source only implements full refresh, meaning you will sync all records with every new sync.

## Prerequisites

- Your Visma e-conomic Agreement Grant Token
- Your Visma e-conomic App Secret Token

[This page](https://www.e-conomic.com/developer/connect) guides you through the different ways of connecting to the api.
In sort your options are:

- Developer agreement
- Create a free [sandbox account](https://www.e-conomic.dk/regnskabsprogram/demo-alle), valid for 14 days.
- Demo tokens: `app_secret_token=demo` and `agreement_grant_token=demo`

## Set up the Visma e-conomic source connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Stripe** from the Source type dropdown.
4. Enter a name for your source.
5. Enter **Agreement Grant Token**.
6. Enter **Secret Key**.

## This Source Supports the Following Streams

- [accounts](https://restdocs.e-conomic.com/#get-accounts)
- [customers](https://restdocs.e-conomic.com/#get-customers)
- [invoices booked](https://restdocs.e-conomic.com/#get-invoices-booked)
- [invoices booked document](https://restdocs.e-conomic.com/#get-invoices-booked-bookedinvoicenumber)
- [invoices paid](https://restdocs.e-conomic.com/#get-invoices-paid)
- [invoices total](https://restdocs.e-conomic.com/#get-invoices-totals)
- [products](https://restdocs.e-conomic.com/#get-products)

For more information about the api see the [E-conomic REST API Documentation](https://restdocs.e-conomic.com/#tl-dr).

### [Sync models](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes)

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.3.14 | 2025-02-22 | [54497](https://github.com/airbytehq/airbyte/pull/54497) | Update dependencies |
| 0.3.13 | 2025-02-15 | [54079](https://github.com/airbytehq/airbyte/pull/54079) | Update dependencies |
| 0.3.12 | 2025-02-08 | [53576](https://github.com/airbytehq/airbyte/pull/53576) | Update dependencies |
| 0.3.11 | 2025-02-01 | [53085](https://github.com/airbytehq/airbyte/pull/53085) | Update dependencies |
| 0.3.10 | 2025-01-25 | [52395](https://github.com/airbytehq/airbyte/pull/52395) | Update dependencies |
| 0.3.9 | 2025-01-18 | [51957](https://github.com/airbytehq/airbyte/pull/51957) | Update dependencies |
| 0.3.8 | 2025-01-11 | [51445](https://github.com/airbytehq/airbyte/pull/51445) | Update dependencies |
| 0.3.7 | 2024-12-28 | [50787](https://github.com/airbytehq/airbyte/pull/50787) | Update dependencies |
| 0.3.6 | 2024-12-21 | [50319](https://github.com/airbytehq/airbyte/pull/50319) | Update dependencies |
| 0.3.5 | 2024-12-14 | [49733](https://github.com/airbytehq/airbyte/pull/49733) | Update dependencies |
| 0.3.4 | 2024-12-12 | [48198](https://github.com/airbytehq/airbyte/pull/48198) | Update dependencies |
| 0.3.3 | 2024-10-29 | [47761](https://github.com/airbytehq/airbyte/pull/47761) | Update dependencies |
| 0.3.2 | 2024-10-28 | [47543](https://github.com/airbytehq/airbyte/pull/47543) | Update dependencies |
| 0.3.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.3.0 | 2024-08-14 | [44052](https://github.com/airbytehq/airbyte/pull/44052) | Refactor connector to manifest-only format |
| 0.2.15 | 2024-08-10 | [43690](https://github.com/airbytehq/airbyte/pull/43690) | Update dependencies |
| 0.2.14 | 2024-08-03 | [43165](https://github.com/airbytehq/airbyte/pull/43165) | Update dependencies |
| 0.2.13 | 2024-07-27 | [42808](https://github.com/airbytehq/airbyte/pull/42808) | Update dependencies |
| 0.2.12 | 2024-07-20 | [42181](https://github.com/airbytehq/airbyte/pull/42181) | Update dependencies |
| 0.2.11 | 2024-07-13 | [41456](https://github.com/airbytehq/airbyte/pull/41456) | Update dependencies |
| 0.2.10 | 2024-07-09 | [41292](https://github.com/airbytehq/airbyte/pull/41292) | Update dependencies |
| 0.2.9 | 2024-07-06 | [40905](https://github.com/airbytehq/airbyte/pull/40905) | Update dependencies |
| 0.2.8 | 2024-06-25 | [40492](https://github.com/airbytehq/airbyte/pull/40492) | Update dependencies |
| 0.2.7 | 2024-06-22 | [40194](https://github.com/airbytehq/airbyte/pull/40194) | Update dependencies |
| 0.2.6 | 2024-06-04 | [38982](https://github.com/airbytehq/airbyte/pull/38982) | [autopull] Upgrade base image to v1.2.1 |
| 0.2.5 | 2024-05-28 | [38691](https://github.com/airbytehq/airbyte/pull/38691) | Make compatibility with builder |
| 0.2.4 | 2024-04-19 | [37283](https://github.com/airbytehq/airbyte/pull/37283) | Updating to 0.80.0 CDK |
| 0.2.3 | 2024-04-18 | [37283](https://github.com/airbytehq/airbyte/pull/37283) | Manage dependencies with Poetry. |
| 0.2.2 | 2024-04-15 | [37283](https://github.com/airbytehq/airbyte/pull/37283) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.1 | 2024-04-12 | [37283](https://github.com/airbytehq/airbyte/pull/37283) | schema descriptions |
| 0.2.0 | 2023-10-20 | [30991](https://github.com/airbytehq/airbyte/pull/30991) | Migrate to Low-code Framework |
| 0.1.0 | 2022-11-08 | [18595](https://github.com/airbytehq/airbyte/pull/18595) | Adding Visma e-conomic as a source |

</details>
