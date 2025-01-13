# Zendesk Sunshine

## Sync overview

The Zendesk Chat source supports Full Refresh and Incremental syncs.

This source can sync data for the [Zendesk Sunshine API](https://developer.zendesk.com/documentation/custom-data/custom-objects/custom-objects-handbook/).

### Output schema

This Source is capable of syncing the following core Streams:

- [ObjectTypes](https://developer.zendesk.com/api-reference/custom-data/custom-objects-api/resource_types/)
- [ObjectRecords](https://developer.zendesk.com/api-reference/custom-data/custom-objects-api/resources/)
- [RelationshipTypes](https://developer.zendesk.com/api-reference/custom-data/custom-objects-api/relationship_types/)
- [RelationshipRecords](https://developer.zendesk.com/api-reference/custom-data/custom-objects-api/relationships/)
- [ObjectTypePolicies](https://developer.zendesk.com/api-reference/custom-data/custom-objects-api/permissions/)
- [Jobs](https://developer.zendesk.com/api-reference/custom-data/custom-objects-api/jobs/)

  This stream is currently not available because it stores data temporary.

- [Limits](https://developer.zendesk.com/api-reference/custom-data/custom-objects-api/limits/)

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

- Zendesk Sunshine API Token

OR

- Zendesk Sunshine oauth2.0 application (client_id, client_secret, access_token)

### Setup guide

Please follow this [guide](https://developer.zendesk.com/documentation/custom-data/custom-objects/getting-started-with-custom-objects/#enabling-custom-objects)

Generate an API Token or oauth2.0 Access token as described in [here](https://developer.zendesk.com/api-reference/ticketing/introduction/#security-and-authentication)

We recommend creating a restricted, read-only key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.3.4 | 2025-01-11 | [51421](https://github.com/airbytehq/airbyte/pull/51421) | Update dependencies |
| 0.3.3 | 2024-12-28 | [50380](https://github.com/airbytehq/airbyte/pull/50380) | Update dependencies |
| 0.3.2 | 2024-12-14 | [49753](https://github.com/airbytehq/airbyte/pull/49753) | Update dependencies |
| 0.3.1 | 2024-12-12 | [49415](https://github.com/airbytehq/airbyte/pull/49415) | Update dependencies |
| 0.3.0 | 2024-10-31 | [47327](https://github.com/airbytehq/airbyte/pull/47327) | Migrate to Manifest-only |
| 0.2.26 | 2024-10-29 | [47802](https://github.com/airbytehq/airbyte/pull/47802) | Update dependencies |
| 0.2.25 | 2024-10-28 | [47066](https://github.com/airbytehq/airbyte/pull/47066) | Update dependencies |
| 0.2.24 | 2024-10-12 | [46784](https://github.com/airbytehq/airbyte/pull/46784) | Update dependencies |
| 0.2.23 | 2024-10-05 | [46486](https://github.com/airbytehq/airbyte/pull/46486) | Update dependencies |
| 0.2.22 | 2024-09-28 | [46102](https://github.com/airbytehq/airbyte/pull/46102) | Update dependencies |
| 0.2.21 | 2024-09-21 | [45769](https://github.com/airbytehq/airbyte/pull/45769) | Update dependencies |
| 0.2.20 | 2024-09-14 | [45546](https://github.com/airbytehq/airbyte/pull/45546) | Update dependencies |
| 0.2.19 | 2024-09-07 | [45298](https://github.com/airbytehq/airbyte/pull/45298) | Update dependencies |
| 0.2.18 | 2024-08-31 | [45008](https://github.com/airbytehq/airbyte/pull/45008) | Update dependencies |
| 0.2.17 | 2024-08-24 | [44720](https://github.com/airbytehq/airbyte/pull/44720) | Update dependencies |
| 0.2.16 | 2024-08-17 | [44219](https://github.com/airbytehq/airbyte/pull/44219) | Update dependencies |
| 0.2.15 | 2024-08-10 | [43502](https://github.com/airbytehq/airbyte/pull/43502) | Update dependencies |
| 0.2.14 | 2024-08-03 | [43246](https://github.com/airbytehq/airbyte/pull/43246) | Update dependencies |
| 0.2.13 | 2024-07-27 | [42604](https://github.com/airbytehq/airbyte/pull/42604) | Update dependencies |
| 0.2.12 | 2024-07-20 | [42371](https://github.com/airbytehq/airbyte/pull/42371) | Update dependencies |
| 0.2.11 | 2024-07-13 | [41880](https://github.com/airbytehq/airbyte/pull/41880) | Update dependencies |
| 0.2.10 | 2024-07-10 | [41496](https://github.com/airbytehq/airbyte/pull/41496) | Update dependencies |
| 0.2.9 | 2024-07-09 | [41205](https://github.com/airbytehq/airbyte/pull/41205) | Update dependencies |
| 0.2.8 | 2024-07-06 | [40850](https://github.com/airbytehq/airbyte/pull/40850) | Update dependencies |
| 0.2.7 | 2024-06-25 | [40443](https://github.com/airbytehq/airbyte/pull/40443) | Update dependencies |
| 0.2.6 | 2024-06-22 | [39956](https://github.com/airbytehq/airbyte/pull/39956) | Update dependencies |
| 0.2.5 | 2024-06-04 | [39058](https://github.com/airbytehq/airbyte/pull/39058) | [autopull] Upgrade base image to v1.2.1 |
| 0.2.4 | 2024-04-19 | [37302](https://github.com/airbytehq/airbyte/pull/37302) | Updating to 0.80.0 CDK |
| 0.2.3 | 2024-04-18 | [37302](https://github.com/airbytehq/airbyte/pull/37302) | Manage dependencies with Poetry. |
| 0.2.2 | 2024-04-15 | [37302](https://github.com/airbytehq/airbyte/pull/37302) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.1 | 2024-04-12 | [37302](https://github.com/airbytehq/airbyte/pull/37302) | schema descriptions |
| 0.2.0 | 2023-08-22 | [29310](https://github.com/airbytehq/airbyte/pull/29310) | Migrate Python CDK to Low Code |
| 0.1.2 | 2023-08-15 | [7976](https://github.com/airbytehq/airbyte/pull/7976) | Fix schemas and tests |
| 0.1.1 | 2021-11-15 | [7976](https://github.com/airbytehq/airbyte/pull/7976) | Add oauth2.0 support |
| 0.1.0 | 2021-07-08 | [4359](https://github.com/airbytehq/airbyte/pull/4359) | Initial Release |

</details>
