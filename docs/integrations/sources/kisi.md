# Kisi
This is the setup for the Kisi source connector that ingests data from the Kisi API.

Kisi's sturdy hardware and user-friendly software work in perfect harmony to enhance the security of your spaces. Remotely manage your locations, streamline operations, and stay compliant while enjoying mobile unlocks. https://www.getkisi.com/

In order to use this source, you must first create an account with Kisi.
On the top right corner, click on your name and click on My Account.
Next, select the API tab and click on Add API key. Enter your name, your Kisi password, and your verification code and click Add. Copy the API key shown on the screen.

You can learn more about the API key here https://api.kisi.io/docs#/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your KISI API Key |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | id | DefaultPaginator | ✅ |  ❌  |
| user_export_reporters | id | DefaultPaginator | ✅ |  ❌  |
| scheduled_reports | id | DefaultPaginator | ✅ |  ❌  |
| role_assignments | id | DefaultPaginator | ✅ |  ❌  |
| places | id | DefaultPaginator | ✅ |  ❌  |
| reports | id | DefaultPaginator | ✅ |  ❌  |
| organizations | id | DefaultPaginator | ✅ |  ❌  |
| members | id | DefaultPaginator | ✅ |  ❌  |
| logins | id | DefaultPaginator | ✅ |  ❌  |
| locks | id | DefaultPaginator | ✅ |  ❌  |
| groups | id | DefaultPaginator | ✅ |  ❌  |
| floors | id | DefaultPaginator | ✅ |  ❌  |
| elevators | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.19 | 2025-03-08 | [55494](https://github.com/airbytehq/airbyte/pull/55494) | Update dependencies |
| 0.0.18 | 2025-03-01 | [54811](https://github.com/airbytehq/airbyte/pull/54811) | Update dependencies |
| 0.0.17 | 2025-02-22 | [54352](https://github.com/airbytehq/airbyte/pull/54352) | Update dependencies |
| 0.0.16 | 2025-02-15 | [53865](https://github.com/airbytehq/airbyte/pull/53865) | Update dependencies |
| 0.0.15 | 2025-02-08 | [53266](https://github.com/airbytehq/airbyte/pull/53266) | Update dependencies |
| 0.0.14 | 2025-02-01 | [52771](https://github.com/airbytehq/airbyte/pull/52771) | Update dependencies |
| 0.0.13 | 2025-01-25 | [52222](https://github.com/airbytehq/airbyte/pull/52222) | Update dependencies |
| 0.0.12 | 2025-01-18 | [51786](https://github.com/airbytehq/airbyte/pull/51786) | Update dependencies |
| 0.0.11 | 2025-01-11 | [51153](https://github.com/airbytehq/airbyte/pull/51153) | Update dependencies |
| 0.0.10 | 2024-12-28 | [50636](https://github.com/airbytehq/airbyte/pull/50636) | Update dependencies |
| 0.0.9 | 2024-12-21 | [50078](https://github.com/airbytehq/airbyte/pull/50078) | Update dependencies |
| 0.0.8 | 2024-12-14 | [49627](https://github.com/airbytehq/airbyte/pull/49627) | Update dependencies |
| 0.0.7 | 2024-12-12 | [49273](https://github.com/airbytehq/airbyte/pull/49273) | Update dependencies |
| 0.0.6 | 2024-12-11 | [48983](https://github.com/airbytehq/airbyte/pull/48983) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.5 | 2024-11-05 | [48356](https://github.com/airbytehq/airbyte/pull/48356) | Revert to source-declarative-manifest v5.17.0 |
| 0.0.4 | 2024-11-05 | [48332](https://github.com/airbytehq/airbyte/pull/48332) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47914](https://github.com/airbytehq/airbyte/pull/47914) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47606](https://github.com/airbytehq/airbyte/pull/47606) | Update dependencies |
| 0.0.1 | 2024-10-18 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
