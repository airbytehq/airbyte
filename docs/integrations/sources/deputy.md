# Deputy
A manifest-only source for Deputy
https://www.deputy.com/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `install` | `string` | Installation Subdomain. The specific subdomain for the customer&#39;s Deputy installation. Your deputy url is of the form https://{install}.{geo}.deputy.com  |  |
| `geo` | `string` | Geographical Subdomain. The geographical subdomain indicating the region of the Deputy installation. Your Deputy url is of the form https://{install}.{geo}.deputy.com |  |
| `client_id` | `string` | OAuth Client ID.  |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |
| `refresh_token` | `string` | OAuth Refresh Token.  |  |
| `redirect_uri` | `string` | Redirect URI. The redirect URL that has been set for your application |  |
| `oauth_access_token` | `string` | Access token. The current access token. This field might be overridden by the connector based on the token refresh endpoint response. |  |
| `oauth_token_expiry_date` | `string` | Token expiry date. The date the current access token expires in. This field might be overridden by the connector based on the token refresh endpoint response. |  |
| `start_time` | `string` | Start Time. The earliest time date based/historical streams need to be streamed from | 2024-01-01T00:00:00Z |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| check_stream | UserId.EmployeeId | No pagination | ✅ |  ❌  |
| employees | id | DefaultPaginator | ✅ |  ❌  |
| timesheets | Id | DefaultPaginator | ✅ |  ❌  |
| employee_pay_conditions | Id | DefaultPaginator | ✅ |  ❌  |
| shifts | Id | DefaultPaginator | ✅ |  ❌  |
| contacts | Id | DefaultPaginator | ✅ |  ❌  |
| geos | Id | DefaultPaginator | ✅ |  ❌  |
| leaves | Id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-08 | | Initial release by [@pabloescoder](https://github.com/pabloescoder) via Connector Builder |

</details>
