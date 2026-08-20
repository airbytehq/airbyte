# Contributing to source-greenhouse

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Harvest v3 stream behavior

This connector uses Greenhouse Harvest v3 with OAuth Authorization Code authentication and rotating refresh tokens. Cursor follow-up requests use the opaque URL from the `Link` header and must not repeat first-request-only parameters such as `per_page`, date filters, parent filters, or static filters. The `refresh_token_updater` persists each rotated refresh token. Connections idle longer than the approximately 24-hour refresh-token lifetime require manual reauthentication. Applications state is migrated from `applied_at` to `created_at` during the 1.0.0 upgrade.

| Stream | Relationship | Cursor field | Request filter | Status |
|---|---|---|---|---|
| applications | top-level | created_at | created_at | incremental |
| applications_demographics_answers | child | updated_at | updated_at, application_ids | incremental |
| applications_interviews | child | updated_at | updated_at, application_ids | incremental |
| candidates | top-level | updated_at | updated_at | incremental |
| close_reasons | top-level | none | none | full refresh |
| custom_fields | top-level | none | none | full refresh |
| degrees | top-level | none | custom_field_key=degree | full refresh |
| demographics_answers | top-level | updated_at | updated_at | incremental |
| demographics_answer_options | top-level | none | none | full refresh |
| demographics_questions | top-level | none | none | full refresh |
| demographics_answers_answer_options | child | none | demographic_question_ids | full refresh |
| demographics_question_sets | top-level | none | none | full refresh |
| demographics_question_sets_questions | child | none | demographic_question_set_ids | full refresh |
| departments | top-level | none | none | full refresh |
| jobs | top-level | updated_at | updated_at | incremental |
| jobs_openings | child | none | job_ids | full refresh |
| interviews | top-level | updated_at | updated_at | incremental |
| job_posts | top-level | updated_at | updated_at | incremental |
| job_stages | top-level | updated_at | updated_at | incremental |
| jobs_stages | child | updated_at | updated_at, job_ids | incremental |
| offers | top-level | updated_at | updated_at | incremental |
| rejection_reasons | top-level | none | none | full refresh |
| scorecards | top-level | updated_at | updated_at | incremental |
| sources | top-level | none | none | full refresh |
| users | top-level | updated_at | updated_at | incremental |
| activity_feed | child | none | candidate_ids | full refresh |
| approvals | child | none | job_ids | full refresh |
| disciplines | top-level | none | custom_field_key=discipline | full refresh |
| schools | top-level | none | custom_field_key=school_name | full refresh |
| eeoc | top-level | submitted_at | submitted_at | incremental |
| email_templates | top-level | updated_at | updated_at | incremental |
| offices | top-level | none | none | full refresh |
| prospect_pools | top-level | none | none | full refresh |
| tags | top-level | none | none | full refresh |
| user_roles | top-level | none | none | full refresh |
| user_permissions | child | none | user_ids | full refresh |

All streams use the v3 cursor paginator with a first-page `per_page` value of 500. Parent partition fields remain `application_id`, `job_id`, or `parent_id` as defined by the existing stream relationships.
