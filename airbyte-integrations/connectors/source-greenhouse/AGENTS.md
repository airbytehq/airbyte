> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-greenhouse

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Greenhouse Harvest API supports `updated_after` filtering on high-volume endpoints (applications, candidates, jobs, offers, etc.), which the connector already uses. The remaining FR parent streams are small config-style lookups (close_reasons, custom_fields, degrees, departments, etc.) that do not support date-based filtering.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| applications | medium | top-level parent | applied_at | applied_at | incremental |  |
| candidates | medium | top-level parent | updated_at | updated_at | incremental |  |
| close_reasons | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| custom_fields | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| degrees | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| demographics_answer_options | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| demographics_answers | medium | top-level parent | updated_at | updated_at | incremental |  |
| demographics_question_sets | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| demographics_questions | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| departments | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| disciplines | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| eeoc | medium | top-level parent | submitted_at | submitted_at | incremental |  |
| email_templates | medium | top-level parent | updated_at | updated_at | incremental |  |
| interviews | medium | top-level parent | updated_at | updated_at | incremental |  |
| job_posts | medium | top-level parent | updated_at | updated_at | incremental |  |
| job_stages | medium | top-level parent | updated_at | updated_at | incremental |  |
| jobs | medium | top-level parent | updated_at | updated_at | incremental |  |
| offers | medium | top-level parent | updated_at | updated_at | incremental |  |
| offices | medium | top-level parent | none | none | deferred_no_api_support |  |
| prospect_pools | medium | top-level parent | none | none | deferred_no_api_support |  |
| rejection_reasons | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| schools | medium | top-level parent | none | none | deferred_no_api_support |  |
| scorecards | medium | top-level parent | updated_at | updated_at | incremental |  |
| sources | small | top-level parent | none | none | deferred_no_api_support | Config-style lookup |
| tags | medium | top-level parent | none | none | deferred_no_api_support |  |
| user_roles | medium | top-level parent | none | none | deferred_no_api_support |  |
| users | medium | top-level parent | updated_at | updated_at | incremental |  |
| activity_feed | medium | child | none | none | deferred_child |  |
| applications_demographics_answers | medium | child | updated_at | updated_at | incremental |  |
| applications_interviews | medium | child | updated_at | updated_at | incremental |  |
| approvals | medium | child | none | none | deferred_child |  |
| demographics_answers_answer_options | medium | child | none | none | deferred_child |  |
| demographics_question_sets_questions | medium | child | none | none | deferred_child |  |
| jobs_openings | medium | child | none | none | deferred_child |  |
| jobs_stages | medium | child | updated_at | updated_at | incremental |  |
| user_permissions | medium | child | none | none | deferred_child |  |

### Future incremental stream candidates

- **No API date filter (15 streams):** `close_reasons`, `custom_fields`, `degrees`, `demographics_answer_options`, `demographics_question_sets`, `demographics_questions`, `departments`, `disciplines`, `offices`, `prospect_pools`, `rejection_reasons`, `schools`, `sources`, `tags`, `user_roles` — these streams do not have a documented date-based filter on their list endpoints. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
- **Child streams (6 streams):** `activity_feed`, `approvals`, `demographics_answers_answer_options`, `demographics_question_sets_questions`, `jobs_openings`, `user_permissions` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate whether these can be made incremental independently or via `incremental_dependency`.
