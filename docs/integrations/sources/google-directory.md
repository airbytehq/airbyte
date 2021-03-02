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
| Incremental Sync | Coming soon |  |
| Replicate Incremental Deletes | Coming soon |  |
| SSL connection | Yes |  |

### Performance considerations

Directory API: [Limits and Quotas](https://developers.google.com/admin-sdk/directory/v1/limits)

## Getting started

### Authorization Scopes

Each stream requires one of the following OAuth scopes

1. Users
   1. https://www.googleapis.com/auth/admin.directory.user
   2. https://www.googleapis.com/auth/admin.directory.user.readonly
   3. https://www.googleapis.com/auth/cloud-platform
2. Groups
   1. https://apps-apis.google.com/a/feeds/groups/
   2. https://www.googleapis.com/auth/admin.directory.group
   3. https://www.googleapis.com/auth/admin.directory.group.readonly
3. Group members
   1. https://apps-apis.google.com/a/feeds/groups/
   2. https://www.googleapis.com/auth/admin.directory.group
   3. https://www.googleapis.com/auth/admin.directory.group.member
   4. https://www.googleapis.com/auth/admin.directory.group.member.readonly
   5. https://www.googleapis.com/auth/admin.directory.group.readonly

