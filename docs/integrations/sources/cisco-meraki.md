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
| 0.0.24 | 2025-12-09 | [70646](https://github.com/airbytehq/airbyte/pull/70646) | Update dependencies |
| 0.0.23 | 2025-11-25 | [69936](https://github.com/airbytehq/airbyte/pull/69936) | Update dependencies |
| 0.0.22 | 2025-11-18 | [69627](https://github.com/airbytehq/airbyte/pull/69627) | Update dependencies |
| 0.0.21 | 2025-10-29 | [68918](https://github.com/airbytehq/airbyte/pull/68918) | Update dependencies |
| 0.0.20 | 2025-10-21 | [68494](https://github.com/airbytehq/airbyte/pull/68494) | Update dependencies |
| 0.0.19 | 2025-10-14 | [68055](https://github.com/airbytehq/airbyte/pull/68055) | Update dependencies |
| 0.0.18 | 2025-10-07 | [67176](https://github.com/airbytehq/airbyte/pull/67176) | Update dependencies |
| 0.0.17 | 2025-09-30 | [65834](https://github.com/airbytehq/airbyte/pull/65834) | Update dependencies |
| 0.0.16 | 2025-08-23 | [65279](https://github.com/airbytehq/airbyte/pull/65279) | Update dependencies |
| 0.0.15 | 2025-08-09 | [64665](https://github.com/airbytehq/airbyte/pull/64665) | Update dependencies |
| 0.0.14 | 2025-08-02 | [64315](https://github.com/airbytehq/airbyte/pull/64315) | Update dependencies |
| 0.0.13 | 2025-07-26 | [63950](https://github.com/airbytehq/airbyte/pull/63950) | Update dependencies |
| 0.0.12 | 2025-07-19 | [63578](https://github.com/airbytehq/airbyte/pull/63578) | Update dependencies |
| 0.0.11 | 2025-07-12 | [62987](https://github.com/airbytehq/airbyte/pull/62987) | Update dependencies |
| 0.0.10 | 2025-07-05 | [62805](https://github.com/airbytehq/airbyte/pull/62805) | Update dependencies |
| 0.0.9 | 2025-06-28 | [62350](https://github.com/airbytehq/airbyte/pull/62350) | Update dependencies |
| 0.0.8 | 2025-06-21 | [61952](https://github.com/airbytehq/airbyte/pull/61952) | Update dependencies |
| 0.0.7 | 2025-06-14 | [61234](https://github.com/airbytehq/airbyte/pull/61234) | Update dependencies |
| 0.0.6 | 2025-05-24 | [60415](https://github.com/airbytehq/airbyte/pull/60415) | Update dependencies |
| 0.0.5 | 2025-05-10 | [59926](https://github.com/airbytehq/airbyte/pull/59926) | Update dependencies |
| 0.0.4 | 2025-05-03 | [58314](https://github.com/airbytehq/airbyte/pull/58314) | Update dependencies |
| 0.0.3 | 2025-04-12 | [57783](https://github.com/airbytehq/airbyte/pull/57783) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57222](https://github.com/airbytehq/airbyte/pull/57222) | Update dependencies |
| 0.0.1 | 2025-04-01 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
