# Display & Video 360

Google DoubleClick Bid Manager (DBM) is the API that enables developers to manage Queries and retrieve Reports from Display & Video 360.

DoubleClick Bid Manager API `v1.1` is the latest available and recommended version.

[Link](https://developers.google.com/bid-manager/guides/getting-started-api) to the official documentation

## Features

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |

## Supported Tables

This source is capable of syncing the following tables and their data:

- Audience Composition
- Floodlight
- Reach
- Standard
- Unique Reach Audience

**Note**: It is recommended to first build the desired report in the UI to avoid any errors, since there are several limilations and requirements pertaining to reporting types, filters, dimensions, and metrics (such as valid combinations of metrics and dimensions).

#### Available filters and metrics:

Available filters and metrics are provided in this [page](https://developers.google.com/bid-manager/v1.1/filters-metrics).

## Getting Started \(Airbyte-Cloud\)

1. Click `Authenticate your Display & Video 360 account` to sign in with Google and authorize your account.
2. Get the partner ID for your account.
3. Fill out a start date, and optionally, an end date and filters (check the [Queries documentation](https://developers.google.com/bid-manager/v1.1/queries)) .
4. You're done.

## Getting Started \(Airbyte Open-Source\)

#### Requirements

You can use the [setup tool](https://console.developers.google.com/start/api?id=doubleclickbidmanager&credential=client_key) to create credentials and enable the DBM API in the Google API Console.

- access_token
- refresh_token
- token_uri
- client_id
- client_secret
- start_date
- end_date
- partner_id
- filters

#### Setup guide

- [Getting Started guide](https://developers.google.com/bid-manager/guides/getting-started-api)

- [Using OAuth 2.0 to Access Google APIs](https://developers.google.com/identity/protocols/oauth2/web-server#enable-apis)

## Rate Limiting & Performance Considerations \(Airbyte Open Source\)

This source is constrained by the limits set by the DBM API. You can read more about those limits in the [Display & Video 360 docs](https://developers.google.com/bid-manager/guides/scheduled-reports/best-practices#consider_reporting_quotas).

## Changelog

| Version | Date       | Pull Request                                             | Subject                                      |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------- |
| 0.1.0   | 2022-09-28 | [11828](https://github.com/airbytehq/airbyte/pull/11828) | Release Native Display & Video 360 Connector |
