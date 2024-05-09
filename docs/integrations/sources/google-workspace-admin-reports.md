# Google Workspace Admin Reports

## Overview

This source supports Full Refresh syncs. It uses the [Reports API](https://developers.google.com/admin-sdk/reports/v1/get-start/getting-started) to gain insights on content management with Google Drive activity reports and Audit administrator actions.

### Output schema

This Source is capable of syncing the following Streams:

- [admin](https://developers.google.com/admin-sdk/reports/v1/guides/manage-audit-admin)
- [drive](https://developers.google.com/admin-sdk/reports/v1/guides/manage-audit-drive)
- [logins](https://developers.google.com/admin-sdk/reports/v1/guides/manage-audit-login)
- [mobile](https://developers.google.com/admin-sdk/reports/v1/guides/manage-audit-mobile)
- [oauth_tokens](https://developers.google.com/admin-sdk/reports/v1/guides/manage-audit-tokens)

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
| Incremental Sync  | No                   |       |
| SSL connection    | Yes                  |       |
| Namespaces        | No                   |       |

### Performance considerations

This connector attempts to back off gracefully when it hits Reports API's rate limits. To find more information about limits, see [Reports API Limits and Quotas](https://developers.google.com/admin-sdk/reports/v1/limits) documentation.

## Getting started

### Requirements

- Credentials to a Google Service Account with delegated Domain Wide Authority
- Email address of the workspace admin which created the Service Account

### Create a Service Account with delegated domain wide authority

Follow the Google Documentation for performing [Domain Wide Delegation of Authority](https://developers.google.com/admin-sdk/reports/v1/guides/delegation) to create a Service account with delegated domain wide authority. This account must be created by an administrator of the Google Workspace. Please make sure to grant the following OAuth scopes to the service user:

1. `https://www.googleapis.com/auth/admin.reports.audit.readonly`
2. `https://www.googleapis.com/auth/admin.reports.usage.readonly`

At the end of this process, you should have JSON credentials to this Google Service Account.

You should now be ready to use the Google Workspace Admin Reports API connector in Airbyte.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                   |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------------- |
| 0.1.8   | 2022-02-24 | [10244](https://github.com/airbytehq/airbyte/pull/10244) | Add Meet Stream                           |
| 0.1.7   | 2021-12-06 | [8524](https://github.com/airbytehq/airbyte/pull/8524)   | Update connector fields title/description |
| 0.1.6   | 2021-11-02 | [7623](https://github.com/airbytehq/airbyte/pull/7623)   | Migrate to the CDK                        |
| 0.1.5   | 2021-10-07 | [6878](https://github.com/airbytehq/airbyte/pull/6878)   | Improve testing & output schemas          |
