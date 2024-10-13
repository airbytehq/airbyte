# Employment-Hero
This directory contains the manifest-only connector for `source-employment-hero`.

## Documentation reference:
Visit `https://developer.employmenthero.com/api-references/#icon-book-open-introduction` for API documentation

## Authentication setup
`Employement Hero` uses Bearer token authentication, since code granted OAuth is not directly supported right now, Visit your developer profile for getting your OAuth keys. Refer `https://secure.employmenthero.com/app/v2/organisations/xxxxx/developer_portal/api` for more details.

## Getting your bearer token via postman

You can make a POST request from Postman to exchange your OAuth credentials for an `access token` to make requests.

First make an app to get the client ID and secret for authentication:

1. Go to developers portal Page:
- Visit `https://secure.employmenthero.com/app/v2/organisations/xxxxx/developer_portal/api`, select `Add Application` and input an app name. Select the `scopes` and set the redirect URI as `https://oauth.pstmn.io/v1/callback`.

2. Copy Your App Credentials:
 - After creating the app, you will see the Client ID and Client Secret.
 - Client ID: Copy this value as it will be your Client ID in Postman.
 - Client Secret: Copy this value as it will be your Client Secret in Postman.

3. Visit Postman via web or app and make a new request with following guidelines:
 - Open a new request - Goto Authorization tab - Select OAuth 2.0
 - Auth URL - `https://oauth.employmenthero.com/oauth2/authorize`
 - Access Token URL - `https://oauth.employmenthero.com/oauth2/token`
 - Set your client id and secret and leave scope and state as blank

Hit Get new Access token and approve via browser, Postman will collect a new `access_token` in the console response.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `organization_configids` | `array` | Organization ID. Organization ID which could be found as result of `organizations` stream to be used in other substreams |  |
| `employees_configids` | `array` | Employees ID. Employees IDs in the given organisation found in `employees` stream for passing to sub-streams |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| organisations | id | DefaultPaginator | ✅ |  ❌  |
| employees | id | DefaultPaginator | ✅ |  ❌  |
| leave_requests | id | DefaultPaginator | ✅ |  ❌  |
| employee_certifications | id | DefaultPaginator | ✅ |  ❌  |
| pay_details | id | DefaultPaginator | ✅ |  ❌  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| policies | id | DefaultPaginator | ✅ |  ❌  |
| certifications | id | DefaultPaginator | ✅ |  ❌  |
| custom_fields | id | DefaultPaginator | ✅ |  ❌  |
| employee_custom_fields | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.1 | 2024-09-25 | [45888](https://github.com/airbytehq/airbyte/pull/45888) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>