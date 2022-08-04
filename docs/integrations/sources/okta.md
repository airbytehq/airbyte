# Okta

## Sync overview

This source can sync data for the [Okta API](https://developer.okta.com/docs/reference/). It supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

This Source is capable of syncing the following core Streams:

- [Users](https://developer.okta.com/docs/reference/api/users/#list-users)
- [User Role Assignments](https://developer.okta.com/docs/reference/api/roles/#list-roles-assigned-to-a-user)
- [Groups](https://developer.okta.com/docs/reference/api/groups/#list-groups)
- [Group Members](https://developer.okta.com/docs/reference/api/groups/#list-group-members)
- [Group Role Assignments](https://developer.okta.com/docs/reference/api/roles/#list-roles-assigned-to-a-group)
- [System Log](https://developer.okta.com/docs/reference/api/system-log/#get-started)
- [Custom Roles](https://developer.okta.com/docs/reference/api/roles/#list-roles)
- [Permissions](https://developer.okta.com/docs/reference/api/roles/#list-permissions)

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
| Namespaces        | No                   |       |

### Performance considerations

The connector is restricted by normal Okta [requests limitation](https://developer.okta.com/docs/reference/rate-limits/).

## Getting started

### Requirements

You can use [OAuth2.0](https://developer.okta.com/docs/guides/implement-grant-type/authcodepkce/main/) 
or an [API token](https://developer.okta.com/docs/guides/create-an-api-token/overview/) to authenticate your Okta account. 
If you choose to authenticate with OAuth2.0, [register](https://dev-01177082-admin.okta.com/admin/apps/active) your Okta application.

### Setup guide

1. Use API token from requirements and Okta [domain](https://developer.okta.com/docs/guides/find-your-domain/-/main/). 
2. Go to local Airbyte page.
3. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**. 
4. On the Set up the source page select **Okta** from the Source type dropdown. 
5. Paste all data to required fields.
6. Click `Set up source`.

**Note:**
Different Okta APIs require different admin privilege levels. API tokens inherit the privilege level of the admin account used to create them

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                        |
|:--------|:-----------|:---------------------------------------------------------|:-------------------------------------------------------------------------------|
| 0.1.11  | 2022-08-03 | [14739](https://github.com/airbytehq/airbyte/pull/14739) | add permissions for custom roles |
| 0.1.10  | 2022-08-01 | [15179](https://github.com/airbytehq/airbyte/pull/15179) | Fixed broken schemas for all streams
| 0.1.9   | 2022-07-25 | [15001](https://github.com/airbytehq/airbyte/pull/15001) | Return deprovisioned users                                                     |
| 0.1.8   | 2022-07-19 | [14710](https://github.com/airbytehq/airbyte/pull/14710) | Implement OAuth2.0 authorization method                                        |
| 0.1.7   | 2022-07-13 | [14556](https://github.com/airbytehq/airbyte/pull/14556) | add User_Role_Assignments and Group_Role_Assignments streams (full fetch only) |
| 0.1.6   | 2022-07-11 | [14610](https://github.com/airbytehq/airbyte/pull/14610) | add custom roles stream                                                        |
| 0.1.5   | 2022-07-04 | [14380](https://github.com/airbytehq/airbyte/pull/14380) | add Group_Members stream to okta source                                        |
| 0.1.4   | 2021-11-02 | [7584](https://github.com/airbytehq/airbyte/pull/7584)   | Fix incremental params for log stream                                          |
| 0.1.3   | 2021-09-08 | [5905](https://github.com/airbytehq/airbyte/pull/5905)   | Fix incremental stream defect                                                  |
| 0.1.2   | 2021-07-01 | [4456](https://github.com/airbytehq/airbyte/pull/4456)   | Bugfix infinite pagination in logs stream                                      |
| 0.1.1   | 2021-06-09 | [3937](https://github.com/airbytehq/airbyte/pull/3973)   | Add `AIRBYTE_ENTRYPOINT` env variable for kubernetes support                   |
| 0.1.0   | 2021-05-30 | [3563](https://github.com/airbytehq/airbyte/pull/3563)   | Initial Release                                                                |
