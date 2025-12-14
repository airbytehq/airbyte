# Dropbox Sign
Dropbox Sign is a simple, easy-to-use way to get documents signed securely online.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Find it at https://app.hellosign.com/home/myAccount#api |  |
| `start_date` | `string` | Start date.  |  |

See the [API docs](https://developers.hellosign.com/api/reference/authentication/#api-key-management) for details on generating an API Key.

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| signature_requests | signature_request_id | DefaultPaginator | ✅ |  ✅  |
| templates | template_id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.42 | 2025-12-09 | [70565](https://github.com/airbytehq/airbyte/pull/70565) | Update dependencies |
| 0.0.41 | 2025-11-25 | [70184](https://github.com/airbytehq/airbyte/pull/70184) | Update dependencies |
| 0.0.40 | 2025-11-18 | [69387](https://github.com/airbytehq/airbyte/pull/69387) | Update dependencies |
| 0.0.39 | 2025-10-29 | [68748](https://github.com/airbytehq/airbyte/pull/68748) | Update dependencies |
| 0.0.38 | 2025-10-21 | [68576](https://github.com/airbytehq/airbyte/pull/68576) | Update dependencies |
| 0.0.37 | 2025-10-14 | [67724](https://github.com/airbytehq/airbyte/pull/67724) | Update dependencies |
| 0.0.36 | 2025-10-07 | [67280](https://github.com/airbytehq/airbyte/pull/67280) | Update dependencies |
| 0.0.35 | 2025-09-30 | [65845](https://github.com/airbytehq/airbyte/pull/65845) | Update dependencies |
| 0.0.34 | 2025-08-23 | [65242](https://github.com/airbytehq/airbyte/pull/65242) | Update dependencies |
| 0.0.33 | 2025-08-16 | [64757](https://github.com/airbytehq/airbyte/pull/64757) | Update dependencies |
| 0.0.32 | 2025-08-02 | [64331](https://github.com/airbytehq/airbyte/pull/64331) | Update dependencies |
| 0.0.31 | 2025-07-26 | [63935](https://github.com/airbytehq/airbyte/pull/63935) | Update dependencies |
| 0.0.30 | 2025-07-19 | [63598](https://github.com/airbytehq/airbyte/pull/63598) | Update dependencies |
| 0.0.29 | 2025-07-12 | [63019](https://github.com/airbytehq/airbyte/pull/63019) | Update dependencies |
| 0.0.28 | 2025-07-05 | [62813](https://github.com/airbytehq/airbyte/pull/62813) | Update dependencies |
| 0.0.27 | 2025-06-28 | [62364](https://github.com/airbytehq/airbyte/pull/62364) | Update dependencies |
| 0.0.26 | 2025-06-22 | [62007](https://github.com/airbytehq/airbyte/pull/62007) | Update dependencies |
| 0.0.25 | 2025-06-14 | [61182](https://github.com/airbytehq/airbyte/pull/61182) | Update dependencies |
| 0.0.24 | 2025-05-24 | [60345](https://github.com/airbytehq/airbyte/pull/60345) | Update dependencies |
| 0.0.23 | 2025-05-10 | [59416](https://github.com/airbytehq/airbyte/pull/59416) | Update dependencies |
| 0.0.22 | 2025-04-26 | [58899](https://github.com/airbytehq/airbyte/pull/58899) | Update dependencies |
| 0.0.21 | 2025-04-19 | [57775](https://github.com/airbytehq/airbyte/pull/57775) | Update dependencies |
| 0.0.20 | 2025-04-05 | [57230](https://github.com/airbytehq/airbyte/pull/57230) | Update dependencies |
| 0.0.19 | 2025-03-29 | [56527](https://github.com/airbytehq/airbyte/pull/56527) | Update dependencies |
| 0.0.18 | 2025-03-22 | [55916](https://github.com/airbytehq/airbyte/pull/55916) | Update dependencies |
| 0.0.17 | 2025-03-08 | [55326](https://github.com/airbytehq/airbyte/pull/55326) | Update dependencies |
| 0.0.16 | 2025-03-01 | [54961](https://github.com/airbytehq/airbyte/pull/54961) | Update dependencies |
| 0.0.15 | 2025-02-22 | [54445](https://github.com/airbytehq/airbyte/pull/54445) | Update dependencies |
| 0.0.14 | 2025-02-15 | [53779](https://github.com/airbytehq/airbyte/pull/53779) | Update dependencies |
| 0.0.13 | 2025-02-08 | [53321](https://github.com/airbytehq/airbyte/pull/53321) | Update dependencies |
| 0.0.12 | 2025-02-01 | [52850](https://github.com/airbytehq/airbyte/pull/52850) | Update dependencies |
| 0.0.11 | 2025-01-25 | [52321](https://github.com/airbytehq/airbyte/pull/52321) | Update dependencies |
| 0.0.10 | 2025-01-18 | [51662](https://github.com/airbytehq/airbyte/pull/51662) | Update dependencies |
| 0.0.9 | 2025-01-11 | [51076](https://github.com/airbytehq/airbyte/pull/51076) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50553](https://github.com/airbytehq/airbyte/pull/50553) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50021](https://github.com/airbytehq/airbyte/pull/50021) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49528](https://github.com/airbytehq/airbyte/pull/49528) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49181](https://github.com/airbytehq/airbyte/pull/49181) | Update dependencies |
| 0.0.4 | 2024-12-11 | [48946](https://github.com/airbytehq/airbyte/pull/48946) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-11-04 | [47831](https://github.com/airbytehq/airbyte/pull/47831) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47607](https://github.com/airbytehq/airbyte/pull/47607) | Update dependencies |
| 0.0.1 | 2024-09-20 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
