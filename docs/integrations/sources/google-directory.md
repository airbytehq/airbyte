# Google Directory

## Overview

The Directory source supports Full Refresh syncs. It uses [Google Directory API](https://developers.google.com/admin-sdk/directory/v1/get-start/getting-started).

### Output schema

This Source is capable of syncing the following Streams:

* [users](https://developers.google.com/admin-sdk/directory/v1/guides/manage-users#get_all_users)
* [groups](https://developers.google.com/admin-sdk/directory/v1/guides/manage-groups#get_all_domain_groups)
* [group members](https://developers.google.com/admin-sdk/directory/v1/guides/manage-group-members#get_all_members)

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
| Incremental Sync | No |  |
| Replicate Incremental Deletes | Coming soon |  |
| SSL connection | Yes |  |
| Namespaces | No |  |

### Performance considerations

This connector attempts to back off gracefully when it hits Directory API's rate limits. To find more information about limits, see [Google Directory's Limits and Quotas](https://developers.google.com/admin-sdk/directory/v1/limits) documentation.

## Getting started

### Requirements

* Credentials to a Google Service Account with delegated Domain Wide Authority
* Email address of the workspace admin which created the Service Account

### Create a Service Account with delegated domain wide authority

Follow the Google Documentation for performing [Domain Wide Delegation of Authority](https://developers.google.com/admin-sdk/directory/v1/guides/delegation) to create a Service account with delegated domain wide authority. This account must be created by an administrator of the Google Workspace. Please make sure to grant the following OAuth scopes to the service user:

1. `https://www.googleapis.com/auth/admin.directory.user.readonly`
2. `https://www.googleapis.com/auth/admin.directory.group.readonly`

At the end of this process, you should have JSON credentials to this Google Service Account.

You should now be ready to use the Google Directory connector in Airbyte.


## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.6  | 2021-11-02 | [7464](https://github.com/airbytehq/airbyte/pull/7464) | Migrate to the CDK |
| 0.1.5  | 2021-10-20 | [6930](https://github.com/airbytehq/airbyte/pull/6930) | Fix crash when a group don't have members |
| 0.1.4  | 2021-10-19 | [7167](https://github.com/airbytehq/airbyte/pull/7167) | Add organizations and phones to `users` schema |
