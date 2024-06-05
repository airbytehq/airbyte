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
| 0.2.1 | 2024-05-20 | [38426](https://github.com/airbytehq/airbyte/pull/38426) | [autopull] base image + poetry + up_to_date |
| 0.2.0 | 2023-10-23 | [31016](https://github.com/airbytehq/airbyte/pull/31016) | Migrated to Low Code CDK |
| 0.1.1 | 2023-08-30 | [29830](https://github.com/airbytehq/airbyte/pull/29830) | Change phone_number in Calls to string (bug in zendesk sell api documentation) |
| 0.1.0 | 2022-10-27 | [17888](https://github.com/airbytehq/airbyte/pull/17888) | Initial Release |

</details>