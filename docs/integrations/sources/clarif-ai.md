# Clarifai

Clarifai is the leading computer vision platform to quickly build and deploy AI on-prem, air-gapped, at the edge, or in the cloud.

API Documentation: https://docs.clarifai.com/api-guide/api-overview/helpful-api-resources/using-postman-with-clarifai-apis

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. The personal access token found at `https://clarifai.com/settings/security` |  |
| `user_id` | `string` | User ID. User ID found in settings |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| applications | id | DefaultPaginator | ✅ |   ❌  |
| datasets | id | DefaultPaginator | ✅ |   ❌  |
| models | id | DefaultPaginator | ✅ |   ❌  |
| model_versions | id | DefaultPaginator | ✅ |   ❌  |
| worklows | id | DefaultPaginator | ✅ |   ❌  |
| app_inputs | id | DefaultPaginator | ✅ |   ❌  |
| app_inputs_jobs | id | DefaultPaginator | ✅ |   ❌ |
| app_concepts | id | DefaultPaginator | ✅ |   ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.44 | 2025-12-09 | [70643](https://github.com/airbytehq/airbyte/pull/70643) | Update dependencies |
| 0.0.43 | 2025-11-25 | [69923](https://github.com/airbytehq/airbyte/pull/69923) | Update dependencies |
| 0.0.42 | 2025-11-18 | [69613](https://github.com/airbytehq/airbyte/pull/69613) | Update dependencies |
| 0.0.41 | 2025-10-29 | [68894](https://github.com/airbytehq/airbyte/pull/68894) | Update dependencies |
| 0.0.40 | 2025-10-21 | [68548](https://github.com/airbytehq/airbyte/pull/68548) | Update dependencies |
| 0.0.39 | 2025-10-14 | [68079](https://github.com/airbytehq/airbyte/pull/68079) | Update dependencies |
| 0.0.38 | 2025-10-07 | [67186](https://github.com/airbytehq/airbyte/pull/67186) | Update dependencies |
| 0.0.37 | 2025-09-30 | [66252](https://github.com/airbytehq/airbyte/pull/66252) | Update dependencies |
| 0.0.36 | 2025-09-09 | [65827](https://github.com/airbytehq/airbyte/pull/65827) | Update dependencies |
| 0.0.35 | 2025-08-23 | [65270](https://github.com/airbytehq/airbyte/pull/65270) | Update dependencies |
| 0.0.34 | 2025-08-09 | [64670](https://github.com/airbytehq/airbyte/pull/64670) | Update dependencies |
| 0.0.33 | 2025-08-02 | [64371](https://github.com/airbytehq/airbyte/pull/64371) | Update dependencies |
| 0.0.32 | 2025-07-26 | [63996](https://github.com/airbytehq/airbyte/pull/63996) | Update dependencies |
| 0.0.31 | 2025-07-19 | [63571](https://github.com/airbytehq/airbyte/pull/63571) | Update dependencies |
| 0.0.30 | 2025-07-12 | [62968](https://github.com/airbytehq/airbyte/pull/62968) | Update dependencies |
| 0.0.29 | 2025-07-05 | [62772](https://github.com/airbytehq/airbyte/pull/62772) | Update dependencies |
| 0.0.28 | 2025-06-28 | [62367](https://github.com/airbytehq/airbyte/pull/62367) | Update dependencies |
| 0.0.27 | 2025-06-21 | [61970](https://github.com/airbytehq/airbyte/pull/61970) | Update dependencies |
| 0.0.26 | 2025-06-14 | [61206](https://github.com/airbytehq/airbyte/pull/61206) | Update dependencies |
| 0.0.25 | 2025-05-24 | [60419](https://github.com/airbytehq/airbyte/pull/60419) | Update dependencies |
| 0.0.24 | 2025-05-10 | [60046](https://github.com/airbytehq/airbyte/pull/60046) | Update dependencies |
| 0.0.23 | 2025-05-03 | [59448](https://github.com/airbytehq/airbyte/pull/59448) | Update dependencies |
| 0.0.22 | 2025-04-26 | [58892](https://github.com/airbytehq/airbyte/pull/58892) | Update dependencies |
| 0.0.21 | 2025-04-19 | [58322](https://github.com/airbytehq/airbyte/pull/58322) | Update dependencies |
| 0.0.20 | 2025-04-12 | [57777](https://github.com/airbytehq/airbyte/pull/57777) | Update dependencies |
| 0.0.19 | 2025-04-05 | [57260](https://github.com/airbytehq/airbyte/pull/57260) | Update dependencies |
| 0.0.18 | 2025-03-29 | [56151](https://github.com/airbytehq/airbyte/pull/56151) | Update dependencies |
| 0.0.17 | 2025-03-08 | [55381](https://github.com/airbytehq/airbyte/pull/55381) | Update dependencies |
| 0.0.16 | 2025-03-01 | [54837](https://github.com/airbytehq/airbyte/pull/54837) | Update dependencies |
| 0.0.15 | 2025-02-22 | [54282](https://github.com/airbytehq/airbyte/pull/54282) | Update dependencies |
| 0.0.14 | 2025-02-15 | [53918](https://github.com/airbytehq/airbyte/pull/53918) | Update dependencies |
| 0.0.13 | 2025-02-08 | [53396](https://github.com/airbytehq/airbyte/pull/53396) | Update dependencies |
| 0.0.12 | 2025-02-01 | [52949](https://github.com/airbytehq/airbyte/pull/52949) | Update dependencies |
| 0.0.11 | 2025-01-25 | [52156](https://github.com/airbytehq/airbyte/pull/52156) | Update dependencies |
| 0.0.10 | 2025-01-18 | [51775](https://github.com/airbytehq/airbyte/pull/51775) | Update dependencies |
| 0.0.9 | 2025-01-11 | [51265](https://github.com/airbytehq/airbyte/pull/51265) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50482](https://github.com/airbytehq/airbyte/pull/50482) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50178](https://github.com/airbytehq/airbyte/pull/50178) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49583](https://github.com/airbytehq/airbyte/pull/49583) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49295](https://github.com/airbytehq/airbyte/pull/49295) | Update dependencies |
| 0.0.4 | 2024-12-11 | [48898](https://github.com/airbytehq/airbyte/pull/48898) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-11-05 | [48355](https://github.com/airbytehq/airbyte/pull/48355) | Revert to source-declarative-manifest v5.17.0 |
| 0.0.2 | 2024-11-05 | [48321](https://github.com/airbytehq/airbyte/pull/48321) | Update dependencies |
| 0.0.1 | 2024-10-21 | | Initial release by [@gemsteam](https://github.com/gemsteam) via Connector Builder |

</details>
