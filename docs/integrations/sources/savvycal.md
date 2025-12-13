# SavvyCal
Sync your scheduled meetings and scheduling links from SavvyCal!

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Go to SavvyCal → Settings → Developer → Personal Tokens and make a new token. Then, copy the private key. https://savvycal.com/developers |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| events | id | DefaultPaginator | ✅ |  ❌  |
| scheduling_links | id | DefaultPaginator | ✅ |  ❌  |
| timezones | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.42 | 2025-12-09 | [70732](https://github.com/airbytehq/airbyte/pull/70732) | Update dependencies |
| 0.0.41 | 2025-11-25 | [69990](https://github.com/airbytehq/airbyte/pull/69990) | Update dependencies |
| 0.0.40 | 2025-11-18 | [69692](https://github.com/airbytehq/airbyte/pull/69692) | Update dependencies |
| 0.0.39 | 2025-10-29 | [68889](https://github.com/airbytehq/airbyte/pull/68889) | Update dependencies |
| 0.0.38 | 2025-10-21 | [68412](https://github.com/airbytehq/airbyte/pull/68412) | Update dependencies |
| 0.0.37 | 2025-10-14 | [67905](https://github.com/airbytehq/airbyte/pull/67905) | Update dependencies |
| 0.0.36 | 2025-10-07 | [67229](https://github.com/airbytehq/airbyte/pull/67229) | Update dependencies |
| 0.0.35 | 2025-09-30 | [66864](https://github.com/airbytehq/airbyte/pull/66864) | Update dependencies |
| 0.0.34 | 2025-09-23 | [66625](https://github.com/airbytehq/airbyte/pull/66625) | Update dependencies |
| 0.0.33 | 2025-09-09 | [66121](https://github.com/airbytehq/airbyte/pull/66121) | Update dependencies |
| 0.0.32 | 2025-08-24 | [65495](https://github.com/airbytehq/airbyte/pull/65495) | Update dependencies |
| 0.0.31 | 2025-08-09 | [64846](https://github.com/airbytehq/airbyte/pull/64846) | Update dependencies |
| 0.0.30 | 2025-08-02 | [64460](https://github.com/airbytehq/airbyte/pull/64460) | Update dependencies |
| 0.0.29 | 2025-07-26 | [63946](https://github.com/airbytehq/airbyte/pull/63946) | Update dependencies |
| 0.0.28 | 2025-07-12 | [63045](https://github.com/airbytehq/airbyte/pull/63045) | Update dependencies |
| 0.0.27 | 2025-07-05 | [62705](https://github.com/airbytehq/airbyte/pull/62705) | Update dependencies |
| 0.0.26 | 2025-06-28 | [62272](https://github.com/airbytehq/airbyte/pull/62272) | Update dependencies |
| 0.0.25 | 2025-06-14 | [61457](https://github.com/airbytehq/airbyte/pull/61457) | Update dependencies |
| 0.0.24 | 2025-05-24 | [60464](https://github.com/airbytehq/airbyte/pull/60464) | Update dependencies |
| 0.0.23 | 2025-05-10 | [60066](https://github.com/airbytehq/airbyte/pull/60066) | Update dependencies |
| 0.0.22 | 2025-05-04 | [59591](https://github.com/airbytehq/airbyte/pull/59591) | Update dependencies |
| 0.0.21 | 2025-04-27 | [58964](https://github.com/airbytehq/airbyte/pull/58964) | Update dependencies |
| 0.0.20 | 2025-04-19 | [58428](https://github.com/airbytehq/airbyte/pull/58428) | Update dependencies |
| 0.0.19 | 2025-04-12 | [57451](https://github.com/airbytehq/airbyte/pull/57451) | Update dependencies |
| 0.0.18 | 2025-03-29 | [56790](https://github.com/airbytehq/airbyte/pull/56790) | Update dependencies |
| 0.0.17 | 2025-03-22 | [56233](https://github.com/airbytehq/airbyte/pull/56233) | Update dependencies |
| 0.0.16 | 2025-03-08 | [55517](https://github.com/airbytehq/airbyte/pull/55517) | Update dependencies |
| 0.0.15 | 2025-03-01 | [55041](https://github.com/airbytehq/airbyte/pull/55041) | Update dependencies |
| 0.0.14 | 2025-02-23 | [54585](https://github.com/airbytehq/airbyte/pull/54585) | Update dependencies |
| 0.0.13 | 2025-02-15 | [53960](https://github.com/airbytehq/airbyte/pull/53960) | Update dependencies |
| 0.0.12 | 2025-02-08 | [53448](https://github.com/airbytehq/airbyte/pull/53448) | Update dependencies |
| 0.0.11 | 2025-02-01 | [52993](https://github.com/airbytehq/airbyte/pull/52993) | Update dependencies |
| 0.0.10 | 2025-01-25 | [51855](https://github.com/airbytehq/airbyte/pull/51855) | Update dependencies |
| 0.0.9 | 2025-01-11 | [51307](https://github.com/airbytehq/airbyte/pull/51307) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50734](https://github.com/airbytehq/airbyte/pull/50734) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50242](https://github.com/airbytehq/airbyte/pull/50242) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49688](https://github.com/airbytehq/airbyte/pull/49688) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49342](https://github.com/airbytehq/airbyte/pull/49342) | Update dependencies |
| 0.0.4 | 2024-12-11 | [49044](https://github.com/airbytehq/airbyte/pull/49044) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-11-04 | [47816](https://github.com/airbytehq/airbyte/pull/47816) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47558](https://github.com/airbytehq/airbyte/pull/47558) | Update dependencies |
| 0.0.1 | 2024-09-01 | | Initial release by [@natikgadzhi](https://github.com/natikgadzhi) via Connector Builder |

</details>
