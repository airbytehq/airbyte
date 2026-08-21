import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Greenhouse migration guide

## Version 1.0.0

Version 1.0.0 migrates the connector from Greenhouse Harvest v1 to Harvest v3 because Greenhouse is sunsetting Harvest v1 and v2 together on 2026-08-31. This is a breaking release: refresh the source schema and reset affected streams after upgrading.

### Authentication

Harvest v3 uses OAuth 2.0 Authorization Code authentication and refresh tokens instead of Harvest API keys. In Airbyte Cloud, enter the OAuth client ID and client secret and click **Authenticate** to complete the consent flow. In self-managed Airbyte, use the consent flow to mint a refresh token and provide it with the client ID and client secret. Reauthentication is required after upgrading to 1.0.0.

### Stream and schema changes

All 36 streams now use their Harvest v3 collection endpoints. The v3 response schemas remove several nested v1 objects and add v3 identifiers, timestamps, and relationship fields. Examples include:

- `applications` uses `updated_at` for incremental state instead of `applied_at` and exposes flat job, stage, recruiter, coordinator, and source identifiers.
- `candidates` no longer embeds applications and uses `private`, `preferred_name`, `last_activity_at`, and linked user identifiers.
- `applications_interviews` uses flat schedule, organizer, and interview identifiers.
- `jobs_openings`, `offers`, and `users` use v3 relationship identifiers instead of the v1 nested objects.
- `offices.location` is a string in v3 rather than the v1 object.
- `activity_feed` changes record grain. In v1 it returned one row per candidate whose only columns were the `activities`, `emails`, and `notes` arrays, and the stream had no primary key. It now reads `GET /v3/notes` and emits one flat row per note, with `id` as the primary key. Every existing column is replaced and the row count grows to the number of notes per candidate - drop and re-create the destination table for this stream rather than refreshing the schema in place.

#### Removed and renamed top-level fields

| Stream | Removed in v3 | Renamed in v3 |
|---|---|---|
| activity_feed | `activities`, `emails`, `notes` | |
| applications | `attachments`, `credited_to`, `current_stage`, `jobs`, `location`, `prospect_detail`, `prospective_department`, `prospective_office`, `rejection_details`, `rejection_reason`, `source` | `applied_at` -> `updated_at` |
| applications_interviews | `end`, `interview`, `interviewers`, `organizer`, `start` | |
| approvals | `approver_groups`, `requested_by_user_id` | |
| candidates | `application_ids`, `applications`, `attachments`, `coordinator`, `educations`, `employments`, `keyed_custom_fields`, `photo_url`, `recruiter` | `is_private` -> `private`, `last_activity` -> `last_activity_at` |
| custom_fields | `departments`, `offices` | `priority` -> `sort_order` |
| degrees, disciplines, schools | | `priority` -> `sort_order` |
| demographics_answer_options, demographics_answers_answer_options, demographics_questions, demographics_question_sets_questions | `translations` | |
| departments | `child_department_external_ids`, `child_ids`, `parent_department_external_id` | |
| email_templates | `cc`, `from`, `type`, `user` | |
| interviews | `end`, `interview`, `interviewers`, `organizer`, `start` | |
| job_posts | `external`, `location` | |
| job_stages, jobs_stages | `interviews` | `priority` -> `sort_order` |
| jobs | `departments`, `hiring_team`, `keyed_custom_fields`, `offices`, `openings` | flattened to `department_id`, `office_ids` |
| jobs_openings | `close_reason`, `keyed_custom_fields`, `status` | |
| offers | `keyed_custom_fields`, `opening`, `sent_at`, `starts_at` | |
| offices | `child_ids`, `child_office_external_ids`, `parent_office_external_id` | `primary_contact_user_id` -> `primary_in_house_contact_user_id`; `location` object -> string |
| prospect_pools | `prospect_stages` | |
| scorecards | `attributes`, `candidate_id`, `interview`, `interview_step`, `overall_recommendation`, `questions`, `ratings` | `interviewer` -> `interviewer_id`, `submitted_by` -> `submitter_id` |
| user_permissions | `user_role_id` | |
| user_roles | `type` | |
| users | `departments`, `offices` | `disabled` -> `deactivated`, `primary_email_address` -> `primary_email` |

Refresh the schema in every destination and reset streams whose records or fields are used downstream. Timestamp and date fields now carry `format: date-time` / `format: date`, so destinations type them as TIMESTAMP/DATE rather than string.

`custom_fields.custom_field_options` is not removed in v3, only relocated: Harvest v3 serves it from `GET /v3/custom_field_options`. Enable the new `custom_field_options` stream and join it back to `custom_fields` on `custom_field_id` to rebuild the nested v1 array.

### Pagination and incremental state

Harvest v3 returns opaque cursor URLs in the `Link` response header. The connector sends `per_page=500`, incremental filters, parent filters, and static filters only on the first request; cursor follow-up requests use only the cursor URL. The legacy `applied_at` watermark is discarded during the 1.0.0 upgrade because it is v3's `created_at`; `applications` and its child streams backfill once on the new `updated_at` cursor.

### Rate limits

The connector uses Greenhouse's v3 rate-limit headers and a moving 30-second window. Existing connections may take longer or process fewer concurrent requests while the connector stays within the documented account limit.

Greenhouse refresh tokens expire after 24 hours of non-use and rotate on every refresh, so set every Greenhouse connection to sync more often than once a day. A connection left paused, disabled, or failing for more than 24 hours requires re-running the consent flow from the source settings.

<MigrationGuide />
