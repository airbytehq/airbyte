# SignNow
Website: https://app.signnow.com/
API Reference: https://docs.signnow.com/docs/signnow/welcome

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `start_date` | `string` | Start date.  |  |
| `api_key_id` | `string` | Api key which could be found in API section after enlarging keys section  |  |
| `auth_token` | `string` | The authorization token is needed for `signing_links` stream which could be seen from enlarged view of `https://app.signnow.com/webapp/api-dashboard/keys`  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| user | id | No pagination | ✅ |  ✅  |
| user_modified_documents | id | No pagination | ✅ |  ✅  |
| user_documents | id | No pagination | ✅ |  ✅  |
| crm_contacts | id | DefaultPaginator | ✅ |  ✅  |
| favourites | id | DefaultPaginator | ✅ |  ❌  |
| logs | uuid | DefaultPaginator | ✅ |  ✅  |
| folder | id | DefaultPaginator | ✅ |  ✅  |
| teams | id | DefaultPaginator | ✅ |  ✅  |
| team_admins | uuid | DefaultPaginator | ✅ |  ✅  |
| brands | unique_id | DefaultPaginator | ✅ |  ❌  |
| crm_users | id | DefaultPaginator | ✅ |  ❌  |
| crm_groups | id | DefaultPaginator | ✅ |  ✅  |
| signing_links | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.27 | 2025-12-09 | [70722](https://github.com/airbytehq/airbyte/pull/70722) | Update dependencies |
| 0.0.26 | 2025-11-25 | [70080](https://github.com/airbytehq/airbyte/pull/70080) | Update dependencies |
| 0.0.25 | 2025-11-18 | [69485](https://github.com/airbytehq/airbyte/pull/69485) | Update dependencies |
| 0.0.24 | 2025-10-29 | [68817](https://github.com/airbytehq/airbyte/pull/68817) | Update dependencies |
| 0.0.23 | 2025-10-21 | [68237](https://github.com/airbytehq/airbyte/pull/68237) | Update dependencies |
| 0.0.22 | 2025-10-14 | [67802](https://github.com/airbytehq/airbyte/pull/67802) | Update dependencies |
| 0.0.21 | 2025-10-07 | [67435](https://github.com/airbytehq/airbyte/pull/67435) | Update dependencies |
| 0.0.20 | 2025-09-30 | [66909](https://github.com/airbytehq/airbyte/pull/66909) | Update dependencies |
| 0.0.19 | 2025-09-24 | [66257](https://github.com/airbytehq/airbyte/pull/66257) | Update dependencies |
| 0.0.18 | 2025-09-09 | [66124](https://github.com/airbytehq/airbyte/pull/66124) | Update dependencies |
| 0.0.17 | 2025-08-23 | [65417](https://github.com/airbytehq/airbyte/pull/65417) | Update dependencies |
| 0.0.16 | 2025-08-09 | [64816](https://github.com/airbytehq/airbyte/pull/64816) | Update dependencies |
| 0.0.15 | 2025-08-02 | [64463](https://github.com/airbytehq/airbyte/pull/64463) | Update dependencies |
| 0.0.14 | 2025-07-26 | [64008](https://github.com/airbytehq/airbyte/pull/64008) | Update dependencies |
| 0.0.13 | 2025-07-12 | [63064](https://github.com/airbytehq/airbyte/pull/63064) | Update dependencies |
| 0.0.12 | 2025-07-05 | [62744](https://github.com/airbytehq/airbyte/pull/62744) | Update dependencies |
| 0.0.11 | 2025-06-28 | [62273](https://github.com/airbytehq/airbyte/pull/62273) | Update dependencies |
| 0.0.10 | 2025-06-21 | [61802](https://github.com/airbytehq/airbyte/pull/61802) | Update dependencies |
| 0.0.9 | 2025-06-14 | [61619](https://github.com/airbytehq/airbyte/pull/61619) | Update dependencies |
| 0.0.8 | 2025-05-24 | [60524](https://github.com/airbytehq/airbyte/pull/60524) | Update dependencies |
| 0.0.7 | 2025-05-10 | [60056](https://github.com/airbytehq/airbyte/pull/60056) | Update dependencies |
| 0.0.6 | 2025-05-04 | [59603](https://github.com/airbytehq/airbyte/pull/59603) | Update dependencies |
| 0.0.5 | 2025-04-27 | [59012](https://github.com/airbytehq/airbyte/pull/59012) | Update dependencies |
| 0.0.4 | 2025-04-19 | [58433](https://github.com/airbytehq/airbyte/pull/58433) | Update dependencies |
| 0.0.3 | 2025-04-12 | [58000](https://github.com/airbytehq/airbyte/pull/58000) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57430](https://github.com/airbytehq/airbyte/pull/57430) | Update dependencies |
| 0.0.1 | 2025-04-02 | [56977](https://github.com/airbytehq/airbyte/pull/56977) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
