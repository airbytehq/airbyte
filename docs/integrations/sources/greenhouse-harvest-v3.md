# Greenhouse Harvest V3
Greenhouse v3 connection

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | OAuth Client ID.  |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| applications | id | DefaultPaginator | ✅ |  ✅  |
| scorecards | id | DefaultPaginator | ✅ |  ✅  |
| scorecard_question_answers | id | DefaultPaginator | ✅ |  ✅  |
| scorecard_questions | id | DefaultPaginator | ✅ |  ✅  |
| candidates | id | DefaultPaginator | ✅ |  ✅  |
| candidate_educations | id | DefaultPaginator | ✅ |  ✅  |
| candidate_employments | id | DefaultPaginator | ✅ |  ✅  |
| candidate_tags | id | DefaultPaginator | ✅ |  ✅  |
| jobs | id | DefaultPaginator | ✅ |  ✅  |
| job_posts | id | DefaultPaginator | ✅ |  ✅  |
| job_interview_stages | id | DefaultPaginator | ✅ |  ✅  |
| openings | id | DefaultPaginator | ✅ |  ✅  |
| offers | id | DefaultPaginator | ✅ |  ✅  |
| prospect_pools | id | DefaultPaginator | ✅ |  ✅  |
| interviews | id | DefaultPaginator | ✅ |  ✅  |
| scorecard_candidate_attributes | id | DefaultPaginator | ✅ |  ✅  |
| departments | id | DefaultPaginator | ✅ |  ✅  |
| offices | id | DefaultPaginator | ✅ |  ✅  |
| users | id | DefaultPaginator | ✅ |  ✅  |
| user_job_permissions | id | DefaultPaginator | ✅ |  ✅  |
| user_roles | id | DefaultPaginator | ✅ |  ✅  |
| future_job_permissions | id | DefaultPaginator | ✅ |  ✅  |
| approval_flows | id | DefaultPaginator | ✅ |  ✅  |
| approver_groups | id | DefaultPaginator | ✅ |  ✅  |
| close_reasons | id | DefaultPaginator | ✅ |  ✅  |
| rejection_reasons | id | DefaultPaginator | ✅ |  ✅  |
| rejection_details | id | DefaultPaginator | ✅ |  ✅  |
| sources | id | DefaultPaginator | ✅ |  ✅  |
| email_templates | id | DefaultPaginator | ✅ |  ✅  |
| custom_fields | id | DefaultPaginator | ✅ |  ✅  |
| custom_field_options | id | DefaultPaginator | ✅ |  ✅  |
| tracking_links | id | DefaultPaginator | ✅ |  ✅  |
| eeoc | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-07-22 | | Initial release by [@NumberPiOso](https://github.com/NumberPiOso) via Connector Builder |

</details>
