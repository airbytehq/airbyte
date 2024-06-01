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

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.2.4   | 2024-04-19 | [37302](https://github.com/airbytehq/airbyte/pull/37302) | Updating to 0.80.0 CDK                                                          |
| 0.2.3   | 2024-04-18 | [37302](https://github.com/airbytehq/airbyte/pull/37302) | Manage dependencies with Poetry.                                                |
| 0.2.2   | 2024-04-15 | [37302](https://github.com/airbytehq/airbyte/pull/37302) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.1   | 2024-04-12 | [37302](https://github.com/airbytehq/airbyte/pull/37302) | schema descriptions                                                             |
| 0.2.0   | 2023-08-22 | [29310](https://github.com/airbytehq/airbyte/pull/29310) | Migrate Python CDK to Low Code                                                  |
| 0.1.2   | 2023-08-15 | [7976](https://github.com/airbytehq/airbyte/pull/7976)   | Fix schemas and tests                                                           |
| 0.1.1   | 2021-11-15 | [7976](https://github.com/airbytehq/airbyte/pull/7976)   | Add oauth2.0 support                                                            |
| 0.1.0   | 2021-07-08 | [4359](https://github.com/airbytehq/airbyte/pull/4359)   | Initial Release                                                                 |
