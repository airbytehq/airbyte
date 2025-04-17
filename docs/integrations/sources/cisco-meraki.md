# Cisco Meraki
Website: https://account.meraki.com/secure/login/dashboard_login
API documentation: https://developer.cisco.com/meraki/api-v1/introduction/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your Meraki API key. Obtain it by logging into your Meraki Dashboard at https://dashboard.meraki.com/, navigating to &#39;My Profile&#39; via the avatar icon in the top right corner, and generating the API key. Save this key securely as it represents your admin credentials. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| organizations | id | DefaultPaginator | ✅ |  ❌  |
| datacenters | uuid | DefaultPaginator | ✅ |  ❌  |
| organization_networks | id | DefaultPaginator | ✅ |  ❌  |
| organization_devices | uuid | DefaultPaginator | ✅ |  ❌  |
| organization_apiRequests | uuid | DefaultPaginator | ✅ |  ✅  |
| organization_admins | id | DefaultPaginator | ✅ |  ✅  |
| organization_saml | uuid | DefaultPaginator | ✅ |  ❌  |
| organization_network_settings | uuid | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.3 | 2025-04-12 | [57783](https://github.com/airbytehq/airbyte/pull/57783) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57222](https://github.com/airbytehq/airbyte/pull/57222) | Update dependencies |
| 0.0.1 | 2025-04-01 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
