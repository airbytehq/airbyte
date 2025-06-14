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
