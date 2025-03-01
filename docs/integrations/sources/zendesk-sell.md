# Zendesk Sell

## Sync overview

The Zendesk Sell source supports Full Refresh.

This source can sync data for the [Zendesk Sell API](https://developer.zendesk.com/api-reference/sales-crm/introduction/).

### Output schema

This Source is capable of syncing the following core Streams:

- Call Outcomes
- Calls
- Collaborations
- Contacts
- Deal Sources
- Deal Unqualified Reason
- Deals
- Lead Conversions
- Lead Sources
- Lead Unqualified Reason
- Leads
- Loss Reasons
- Notes
- Orders
- Pipelines
- Products
- Stages
- Tags
- Tasks
- Text Messages
- Users
- Visit Outcomes
- Visits

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | Yes                  |       |

### Performance considerations

The connector is restricted by normal Zendesk [requests limitation](https://developer.zendesk.com/api-reference/ticketing/account-configuration/usage_limits/)

The Zendesk connector should not run into Zendesk API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- Zendesk Sell API Token

### Setup guide

Please follow this [guide](https://developer.zendesk.com/documentation/custom-data/custom-objects/getting-started-with-custom-objects/#enabling-custom-objects)

Generate an API Token or oauth2.0 Access token as described in [here](https://developer.zendesk.com/api-reference/ticketing/introduction/#security-and-authentication)

We recommend creating a restricted, read-only key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                        |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------------------------------------------------------- |
| 0.3.12 | 2025-02-23 | [54630](https://github.com/airbytehq/airbyte/pull/54630) | Update dependencies |
| 0.3.11 | 2025-02-16 | [54122](https://github.com/airbytehq/airbyte/pull/54122) | Update dependencies |
| 0.3.10 | 2025-02-08 | [53601](https://github.com/airbytehq/airbyte/pull/53601) | Update dependencies |
| 0.3.9 | 2025-02-01 | [53111](https://github.com/airbytehq/airbyte/pull/53111) | Update dependencies |
| 0.3.8 | 2025-01-25 | [52406](https://github.com/airbytehq/airbyte/pull/52406) | Update dependencies |
| 0.3.7 | 2025-01-18 | [51997](https://github.com/airbytehq/airbyte/pull/51997) | Update dependencies |
| 0.3.6 | 2025-01-11 | [51436](https://github.com/airbytehq/airbyte/pull/51436) | Update dependencies |
| 0.3.5 | 2024-12-28 | [50772](https://github.com/airbytehq/airbyte/pull/50772) | Update dependencies |
| 0.3.4 | 2024-12-21 | [50309](https://github.com/airbytehq/airbyte/pull/50309) | Update dependencies |
| 0.3.3 | 2024-12-14 | [49761](https://github.com/airbytehq/airbyte/pull/49761) | Update dependencies |
| 0.3.2 | 2024-12-12 | [47846](https://github.com/airbytehq/airbyte/pull/47846) | Update dependencies |
| 0.3.1 | 2024-10-28 | [47495](https://github.com/airbytehq/airbyte/pull/47495) | Update dependencies |
| 0.3.0 | 2024-08-22 | [44562](https://github.com/airbytehq/airbyte/pull/44562) | Refactor connector to manifest-only format |
| 0.2.14 | 2024-08-17 | [44295](https://github.com/airbytehq/airbyte/pull/44295) | Update dependencies |
| 0.2.13 | 2024-08-12 | [43802](https://github.com/airbytehq/airbyte/pull/43802) | Update dependencies |
| 0.2.12 | 2024-08-10 | [43610](https://github.com/airbytehq/airbyte/pull/43610) | Update dependencies |
| 0.2.11 | 2024-08-03 | [43162](https://github.com/airbytehq/airbyte/pull/43162) | Update dependencies |
| 0.2.10 | 2024-07-27 | [42803](https://github.com/airbytehq/airbyte/pull/42803) | Update dependencies |
| 0.2.9 | 2024-07-20 | [42148](https://github.com/airbytehq/airbyte/pull/42148) | Update dependencies |
| 0.2.8 | 2024-07-13 | [41718](https://github.com/airbytehq/airbyte/pull/41718) | Update dependencies |
| 0.2.7 | 2024-07-10 | [41544](https://github.com/airbytehq/airbyte/pull/41544) | Update dependencies |
| 0.2.6 | 2024-07-09 | [41308](https://github.com/airbytehq/airbyte/pull/41308) | Update dependencies |
| 0.2.5 | 2024-07-06 | [40983](https://github.com/airbytehq/airbyte/pull/40983) | Update dependencies |
| 0.2.4 | 2024-06-25 | [40363](https://github.com/airbytehq/airbyte/pull/40363) | Update dependencies |
| 0.2.3 | 2024-06-22 | [40023](https://github.com/airbytehq/airbyte/pull/40023) | Update dependencies |
| 0.2.2 | 2024-06-06 | [39258](https://github.com/airbytehq/airbyte/pull/39258) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.1 | 2024-05-20 | [38426](https://github.com/airbytehq/airbyte/pull/38426) | [autopull] base image + poetry + up_to_date |
| 0.2.0 | 2023-10-23 | [31016](https://github.com/airbytehq/airbyte/pull/31016) | Migrated to Low Code CDK |
| 0.1.1 | 2023-08-30 | [29830](https://github.com/airbytehq/airbyte/pull/29830) | Change phone_number in Calls to string (bug in zendesk sell api documentation) |
| 0.1.0 | 2022-10-27 | [17888](https://github.com/airbytehq/airbyte/pull/17888) | Initial Release |

</details>
