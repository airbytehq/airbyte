# Google Directory

## Overview

The Directory source supports Full Refresh syncs. It uses [Google Directory API](https://developers.google.com/admin-sdk/directory/v1/get-start/getting-started).

### Output schema

This Source is capable of syncing the following core Streams:

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

### Performance considerations

This connector attempts to back off gracefully when it hits Directory API's rate limits. To find more information about limits, see [Google Directory's Limits and Quotas](https://developers.google.com/admin-sdk/directory/v1/limits) documentation.

## Getting started

### Authorization Scopes

Each stream requires the following OAuth scopes

1. Users https://www.googleapis.com/auth/admin.directory.user.readonly
2. Groups https://www.googleapis.com/auth/admin.directory.group.readonly
3. Group members https://www.googleapis.com/auth/admin.directory.group.readonly

