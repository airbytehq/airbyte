# Rippling

## Sync overview

This source can sync data from [Rippling](https://developer.rippling.com/docs/rippling-api/2e740d9c3405b-rippling-s-api). Currently, this connector only supports full refresh syncs. That is, every time a sync is run, all the records are fetched from the source.

### Output schema

This source is capable of syncing the following streams:

- [`employees`](https://api.rippling.com/platform/api/employees/include_terminated)
- [`leave_requests`](https://api.rippling.com/platform/api/leave_requests)
- [`leave_balances`](https://api.rippling.com/platform/api/leave_balances)
- [`company_leave_types`](https://api.rippling.com/platform/api/company_leave_types)

### Features

| Feature           | Supported? \(Yes/No\) | Notes |
| :---------------- | :-------------------- | :---- |
| Full Refresh Sync | Yes                   |       |
| Incremental Sync  | No                    |       |

## Getting started

### Requirements

1. Generate an API key as described in [Rippling's Customer guide](https://developer.rippling.com/docs/rippling-api/8f924ad751580-customers)
2. Give the API read access on all resources

### Setup guide

The following fields are required fields for the connector to work:

- `api_key`: Your Rippling API Token.

As an optional field, you can also provide:

- `employee_filters`: A comma separated string of the employee filters you do not want to sync. Example: `compensation,ein`

## Changelog

| Version | Date       | Pull Request                                             | Subject    |
| :------ | :--------- | :------------------------------------------------------- | :--------- |
| 0.1.0   | 2023-06-12 | [27242](https://github.com/airbytehq/airbyte/pull/27242) | New source |
