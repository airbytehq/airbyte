# Okta

## Sync overview

This source can sync data for the [Okta API](https://developer.okta.com/docs/reference/). It supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

This Source is capable of syncing the following core Streams:

* [Users](https://developer.okta.com/docs/reference/api/users/#list-users)
* [Groups](https://developer.okta.com/docs/reference/api/groups/#list-groups)
* [System Log](https://developer.okta.com/docs/reference/api/system-log/#get-started)

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `number` | `number` |  |
| `array` | `array` |  |
| `object` | `object` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Yes |  |
| Namespaces | No |  |

### Performance considerations

The connector is restricted by normal Okta [requests limitation](https://developer.okta.com/docs/reference/rate-limits/).

## Getting started

### Requirements

* Okta API Token 

### Setup guide

In order to pull data out of your Okta instance, you need to create an [API Token](https://developer.okta.com/docs/guides/create-an-api-token/overview/).

{% hint style="info" %}
Different Okta APIs require different admin privilege levels. API tokens inherit the privilege level of the admin account used to create them
{% endhint %}

1. Sign in to your Okta organization as a user with [administrator privileges](https://help.okta.com/en/prod/okta_help_CSH.htm#ext_Security_Administrators)
2. Access the API page: In the Admin Console, select API from the Security menu and then select the Tokens tab.
3. Click Create Token.
4. Name your token and click Create Token.
5. Record the token value. This is the only opportunity to see it and record it.
8. In Airbyte, create a Okta source.
9. You can now pull data from your Okta instance!


## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.3 | 2021-09-08 | [5905](https://github.com/airbytehq/airbyte/pull/5905)| Fix incremental stream defect |
| 0.1.2 | 2021-07-01 | [4456](https://github.com/airbytehq/airbyte/pull/4456)| Bugfix infinite pagination in logs stream |
| 0.1.1 | 2021-06-09 | [3937](https://github.com/airbytehq/airbyte/pull/3973) | Add `AIRBYTE_ENTRYPOINT` env variable for kubernetes support|
| 0.1.0   | 2021-05-30 | [3563](https://github.com/airbytehq/airbyte/pull/3563) | Initial Release |

