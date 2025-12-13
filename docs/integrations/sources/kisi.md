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
| 0.0.47 | 2025-12-09 | [70781](https://github.com/airbytehq/airbyte/pull/70781) | Update dependencies |
| 0.0.46 | 2025-11-25 | [70037](https://github.com/airbytehq/airbyte/pull/70037) | Update dependencies |
| 0.0.45 | 2025-11-18 | [69483](https://github.com/airbytehq/airbyte/pull/69483) | Update dependencies |
| 0.0.44 | 2025-10-29 | [68758](https://github.com/airbytehq/airbyte/pull/68758) | Update dependencies |
| 0.0.43 | 2025-10-21 | [68313](https://github.com/airbytehq/airbyte/pull/68313) | Update dependencies |
| 0.0.42 | 2025-10-14 | [67960](https://github.com/airbytehq/airbyte/pull/67960) | Update dependencies |
| 0.0.41 | 2025-10-07 | [67373](https://github.com/airbytehq/airbyte/pull/67373) | Update dependencies |
| 0.0.40 | 2025-09-30 | [66786](https://github.com/airbytehq/airbyte/pull/66786) | Update dependencies |
| 0.0.39 | 2025-09-24 | [66647](https://github.com/airbytehq/airbyte/pull/66647) | Update dependencies |
| 0.0.38 | 2025-09-09 | [66079](https://github.com/airbytehq/airbyte/pull/66079) | Update dependencies |
| 0.0.37 | 2025-08-23 | [65381](https://github.com/airbytehq/airbyte/pull/65381) | Update dependencies |
| 0.0.36 | 2025-08-09 | [64615](https://github.com/airbytehq/airbyte/pull/64615) | Update dependencies |
| 0.0.35 | 2025-08-02 | [64285](https://github.com/airbytehq/airbyte/pull/64285) | Update dependencies |
| 0.0.34 | 2025-07-26 | [63900](https://github.com/airbytehq/airbyte/pull/63900) | Update dependencies |
| 0.0.33 | 2025-07-19 | [63468](https://github.com/airbytehq/airbyte/pull/63468) | Update dependencies |
| 0.0.32 | 2025-07-12 | [63150](https://github.com/airbytehq/airbyte/pull/63150) | Update dependencies |
| 0.0.31 | 2025-07-05 | [62572](https://github.com/airbytehq/airbyte/pull/62572) | Update dependencies |
| 0.0.30 | 2025-06-21 | [61783](https://github.com/airbytehq/airbyte/pull/61783) | Update dependencies |
| 0.0.29 | 2025-06-14 | [61116](https://github.com/airbytehq/airbyte/pull/61116) | Update dependencies |
| 0.0.28 | 2025-05-24 | [60636](https://github.com/airbytehq/airbyte/pull/60636) | Update dependencies |
| 0.0.27 | 2025-05-10 | [59894](https://github.com/airbytehq/airbyte/pull/59894) | Update dependencies |
| 0.0.26 | 2025-05-03 | [59256](https://github.com/airbytehq/airbyte/pull/59256) | Update dependencies |
| 0.0.25 | 2025-04-26 | [58774](https://github.com/airbytehq/airbyte/pull/58774) | Update dependencies |
| 0.0.24 | 2025-04-19 | [58159](https://github.com/airbytehq/airbyte/pull/58159) | Update dependencies |
| 0.0.23 | 2025-04-12 | [57678](https://github.com/airbytehq/airbyte/pull/57678) | Update dependencies |
| 0.0.22 | 2025-04-05 | [57109](https://github.com/airbytehq/airbyte/pull/57109) | Update dependencies |
| 0.0.21 | 2025-03-29 | [56695](https://github.com/airbytehq/airbyte/pull/56695) | Update dependencies |
| 0.0.20 | 2025-03-22 | [56007](https://github.com/airbytehq/airbyte/pull/56007) | Update dependencies |
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
