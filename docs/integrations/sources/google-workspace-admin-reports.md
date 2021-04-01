# Google Workspace > Admin SDK > Reports API

## Overview

This source supports Full Refresh syncs. It uses the [Reports API](https://developers.google.com/admin-sdk/reports/v1/get-start/getting-started) to gain insights on content management with Google Drive activity reports and Audit administrator actions.

### Output schema

This Source is capable of syncing the following Streams:

* [admin](https://developers.google.com/admin-sdk/reports/v1/guides/manage-audit-admin)
* [drive](https://developers.google.com/admin-sdk/reports/v1/guides/manage-audit-drive)
* [logins](https://developers.google.com/admin-sdk/reports/v1/guides/manage-audit-login)
* [mobile](https://developers.google.com/admin-sdk/reports/v1/guides/manage-audit-mobile)
* [oauth_tokens](https://developers.google.com/admin-sdk/reports/v1/guides/manage-audit-tokens)

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
| SSL connection | Yes |  |

### Performance considerations

This connector attempts to back off gracefully when it hits Reports API's rate limits. To find more information about limits, see [Reports API Limits and Quotas](https://developers.google.com/admin-sdk/reports/v1/limits) documentation.

## Getting started

### Requirements
* Credentials to a Google Service Account with delegated Domain Wide Authority
* Email address of the workspace admin which created the Service Account

### Create a Service Account with delegated domain wide authority
Follow the Google Documentation for performing [Domain Wide Delegation of Authority](https://developers.google.com/admin-sdk/reports/v1/guides/delegation) to create a Service account with delegated domain wide authority. This account must be created by an administrator of the Google Workspace. 
Please make sure to grant the following OAuth scopes to the service user: 

1. `https://www.googleapis.com/auth/admin.reports.audit.readonly`
2. `https://www.googleapis.com/auth/admin.reports.usage.readonly`

At the end of this process, you should have JSON credentials to this Google Service Account. 

You should now be ready to use the Google Workspace Admin Reports API connector in Airbyte. 
