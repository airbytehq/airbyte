import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Greenhouse Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 migrates the connector from Greenhouse Harvest v1 to Harvest v3 because Greenhouse is sunsetting Harvest v1 and v2 together on 2026-08-31. This is a breaking release; see the recommended upgrade path below before upgrading.

### Recommended upgrade path: create a new connection

**No stream in 1.0.0 is a one-to-one replacement for its Harvest v1 equivalent.** The migration changes authentication, the endpoint each stream reads, pagination, incremental cursors and state, and the record shape of every stream, so the rows and columns that 1.0.0 produces do not line up with the rows and columns already in your destination.

Because of that, we highly recommend creating a **brand-new connection** with `source-greenhouse` 1.0.0 and a new destination namespace or table prefix, instead of upgrading the existing connection and refreshing its data. That keeps the historical Harvest v1 data already in your destination intact while v3 data lands cleanly alongside it, and it lets you reconcile the two before retiring the old tables. Refreshing an existing connection instead replaces that history with v3-shaped records, and any downstream model built on the v1 columns breaks at the same moment.

Steps:

1. Create a new Greenhouse source on 1.0.0 and complete the OAuth consent flow (see [Authentication](#authentication)).
2. Create a new connection to your destination, writing to a different namespace or stream prefix than the existing Greenhouse connection.
3. Enable the streams you need, optionally setting **Start date** to bound the initial backfill (omitting it replicates all history, matching the previous behavior).
4. Sync, then update downstream models against the v3 columns — see [Stream and schema changes](#stream-and-schema-changes) for the removed and renamed fields.
5. Disable the old connection once the new one has caught up, and keep its destination tables for as long as you need the v1 history.

If you upgrade the existing connection in place instead, you must re-authenticate with OAuth, refresh the schema, and reset the affected streams; `applications` will backfill once because its legacy `applied_at` watermark is discarded.

### Authentication

Harvest v3 uses OAuth 2.0 Authorization Code authentication and refresh tokens instead of Harvest API keys. In Airbyte Cloud, enter the OAuth client ID and client secret and click **Authenticate** to complete the consent flow. In self-managed Airbyte, use the consent flow to mint a refresh token and provide it with the client ID and client secret. Reauthentication is required after upgrading to 1.0.0.

Version 1.0.0 introduces a new optional `start_date` configuration value for incremental streams. When it is omitted, the connector preserves the previous full-history behavior.

Greenhouse issues OAuth client credentials to partners on request by email. Start that external request before the 2026-08-31 Harvest v1/v2 sunset; see the [Greenhouse connector setup](./greenhouse.md#set-up-the-greenhouse-connector-in-airbyte) for the complete setup steps.

### Stream and schema changes

The 33 remaining existing streams now use their Harvest v3 collection endpoints, and this release adds one new `custom_field_options` stream. The v3 response schemas remove several nested v1 objects and add v3 identifiers, timestamps, and relationship fields. Examples include:

- `applications` uses `updated_at` for incremental state instead of `applied_at` and exposes flat job, stage, recruiter, coordinator, and source identifiers.
- `candidates` no longer embeds applications and uses `private`, `preferred_name`, `last_activity_at`, and linked user identifiers.
- `jobs_openings`, `offers`, and `users` use v3 relationship identifiers instead of the v1 nested objects.
- `offices.location` is a string in v3 rather than the v1 object.
- `activity_feed` changes record grain. In v1 it returned one row per candidate whose only columns were the `activities`, `emails`, and `notes` arrays, and the stream had no primary key. It now reads `GET /v3/notes` and emits one flat row per note, with `id` as the primary key. Every existing column is replaced and the row count grows to the number of notes per candidate - drop and re-create the destination table for this stream rather than refreshing the schema in place.

#### Dropped and renamed top-level fields

Version 1.0.0 removes the redundant `applications_demographics_answers`, `applications_interviews`, and `jobs_stages` streams. Their top-level replacements are `demographics_answers`, `interviews`, and `job_stages`, respectively.

| Stream | Dropped from this stream in v3 | Renamed in v3 |
|---|---|---|
| activity_feed | `activities`, `emails`, `notes` | |
| applications | `attachments`, `credited_to`, `current_stage`, `jobs`, `location`, `prospect_detail`, `prospective_department`, `prospective_office`, `rejection_details`, `source` | `applied_at` -> `updated_at`; `rejection_reason` object -> `rejection_reason_id` (join to the `rejection_reasons` stream on `id`) |
| approvals | `approver_groups`, `requested_by_user_id` | |
| candidates | `application_ids`, `applications`, `attachments`, `coordinator`, `educations`, `employments`, `keyed_custom_fields`, `photo_url`, `recruiter` | `is_private` -> `private`, `last_activity` -> `last_activity_at` |
| custom_fields | `departments`, `offices` | `priority` -> `sort_order` |
| degrees, disciplines, schools | | `priority` -> `sort_order` |
| demographics_answer_options, demographics_answers_answer_options, demographics_questions, demographics_question_sets_questions | `translations` | |
| departments | `child_department_external_ids`, `child_ids`, `parent_department_external_id` | |
| email_templates | `cc`, `from`, `type`, `user` | |
| interviews | `end`, `interview`, `interviewers`, `organizer`, `start` | |
| job_posts | `external`, `location` | |
| job_stages | `interviews` | `priority` -> `sort_order` |
| jobs | `departments`, `hiring_team`, `keyed_custom_fields`, `offices`, `openings` | flattened to `department_id`, `office_ids` |
| jobs_openings | `close_reason`, `keyed_custom_fields`, `status` | |
| offers | `keyed_custom_fields`, `opening`, `sent_at`, `starts_at` | |
| offices | `child_ids`, `child_office_external_ids`, `parent_office_external_id` | `primary_contact_user_id` -> `primary_in_house_contact_user_id`; `location` object -> string |
| prospect_pools | `prospect_stages` | |
| scorecards | `attributes`, `candidate_id`, `interview`, `interview_step`, `overall_recommendation`, `questions`, `ratings` | `interviewer` -> `interviewer_id`, `submitted_by` -> `submitter_id` |
| user_permissions | `user_role_id` | |
| user_roles | `type` | |
| users | `departments`, `offices` | `disabled` -> `deactivated`, `primary_email_address` -> `primary_email` |

If you upgrade an existing connection in place, refresh the schema in every destination and reset streams whose records or fields are used downstream. Timestamp and date fields now carry `format: date-time` / `format: date`, so destinations type them as TIMESTAMP/DATE rather than string.

Most of the fields above are not gone from Harvest. Harvest v3 moved them off the parent record onto their own collection endpoints, and this release does not sync those endpoints yet. Adding the rest is tracked for a follow-up release and requires new OAuth scopes, so it will need a second authorization. Until then, Harvest v3 still serves this data at:

| Dropped v1 field | Harvest v3 endpoint |
|---|---|
| `applications.attachments`, `candidates.attachments` | `GET /v3/attachments` |
| `applications.current_stage` | `GET /v3/application_stages` (join on `applications.stage_id`) |
| `applications.prospect_detail`, `prospective_department`, `prospective_office` | `GET /v3/prospect_details` |
| `applications.rejection_details` | `GET /v3/rejection_details` |
| `approvals.approver_groups` | `GET /v3/approver_groups`, `GET /v3/approvers` |
| `candidates.educations` | `GET /v3/candidate_educations` |
| `candidates.employments` | `GET /v3/candidate_employments` |
| `custom_fields.departments`, `custom_fields.offices` | `GET /v3/custom_field_departments`, `GET /v3/custom_field_offices` |
| `interviews.interviewers` | `GET /v3/interviewers` |
| `job_posts.location` | `GET /v3/job_post_locations` (a job post can carry several locations in v3) |
| `job_stages.interviews` | `GET /v3/job_interviews`, `GET /v3/interview_kits` |
| `jobs.hiring_team` | `GET /v3/job_hiring_managers`, `GET /v3/job_owners` |
| `prospect_pools.prospect_stages` | `GET /v3/prospect_pool_stages` |
| `scorecards.attributes` | `GET /v3/scorecard_candidate_attributes` |
| `scorecards.questions` | `GET /v3/scorecard_question_answers` |

`custom_fields.custom_field_options` is not removed in v3, only relocated: Harvest v3 serves it from `GET /v3/custom_field_options`. Enable the new `custom_field_options` stream and join it back to `custom_fields` on `custom_field_id` to rebuild the nested v1 array.

`custom_field_options` reads that endpoint unfiltered, so it is a superset of `degrees`, `disciplines`, and `schools`, which read the same endpoint filtered by `custom_field_key` (`degree`, `discipline`, `school_name`) and share the same `id` primary key. If you enable `custom_field_options`, disable those three unless you specifically want the split tables - otherwise the same option rows land in four destination tables and every sync pages the same endpoint four times.

### Pagination and incremental state

Harvest v3 returns opaque cursor URLs in the `Link` response header. The connector sends `per_page=500`, incremental filters, parent filters, and static filters only on the first request; cursor follow-up requests use only the cursor URL. The legacy `applied_at` watermark is discarded during the 1.0.0 upgrade because it is v3's `created_at`, so `applications` backfills once on the new `updated_at` cursor. The remaining de-fanned child streams preserve the minimum recoverable `updated_at` cursor and resume without a backfill.

The deleted child streams were redundant in v3: `demographics_answers`, `interviews`, and `job_stages` now provide the complete collections formerly exposed through their child-stream counterparts.

### Rate limits

The connector uses Greenhouse's v3 rate-limit headers and a moving 30-second window. Existing connections may take longer or process fewer concurrent requests while the connector uses its own conservative default request budget.

Greenhouse refresh tokens expire after 24 hours of non-use and rotate on every refresh, so set every Greenhouse connection to sync more often than once a day. A connection left paused, disabled, or failing for more than 24 hours requires re-running the consent flow from the source settings.

## Connector upgrade guide

<MigrationGuide />
