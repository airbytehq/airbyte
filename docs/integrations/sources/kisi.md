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
| 0.0.2 | 2024-10-28 | [47606](https://github.com/airbytehq/airbyte/pull/47606) | Update dependencies |
| 0.0.1 | 2024-10-18 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
