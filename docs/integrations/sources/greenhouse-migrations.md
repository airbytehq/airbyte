import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Greenhouse Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 migrates the connector from Greenhouse Harvest v1 to Harvest v3 because Greenhouse is sunsetting Harvest v1 and v2 together on 2026-08-31. This is a breaking release; choose one of the upgrade paths below before upgrading.

### Upgrade paths

**No stream in 1.0.0 is a one-to-one replacement for its Harvest v1 equivalent.** The migration changes authentication, the endpoint each stream reads, pagination, incremental cursors and state, and the record shape of every stream, so the rows and columns that 1.0.0 produces do not line up with the rows and columns already in your destination.

There are two ways to upgrade. Creating a new connection is strongly recommended because it retains your Harvest v1 data; upgrading the existing connection in place is supported and keeps the connection itself, but it requires clearing the affected streams, which replaces the contents of those destination tables and therefore does not retain that history.

#### Option 1 (recommended): create a new connection

Create a **brand-new connection** with `source-greenhouse` 1.0.0 writing to a new destination namespace or table prefix, and keep your existing Harvest v1 tables as history. This keeps the v1 data you already replicated intact and untouched, lets you reconcile the two datasets and migrate downstream models on your own schedule, and avoids every mixed-table problem described in Option 2.

1. Create a new Greenhouse source on 1.0.0 and complete the authentication setup (see [Authentication](#authentication)).
2. Create a new connection to your destination, writing to a different namespace or stream prefix than the existing Greenhouse connection.
3. Enable the streams you need, optionally setting **Start date** to bound the initial backfill (omitting it replicates all history, matching the previous behavior).
4. Sync, then update downstream models against the v3 columns — see [Stream and schema changes](#stream-and-schema-changes) for the removed and renamed fields.
5. Disable the old connection once the new one has caught up, and keep its destination tables for as long as you need the v1 history.

#### Option 2: upgrade the existing connection in place

This path keeps your existing connection, its streams, and its destination tables in place: you update the source configuration to the new OAuth credential, refresh each stream's schema, and clear the affected streams. The trade-off is the data itself — clearing refreshes those destination tables from scratch, so the Harvest v1 rows they hold are replaced by v3 rows and the v1 history is not retained. Back up or copy the tables first if you need that history, or use Option 1 instead.

1. Edit the existing Greenhouse source and complete the authentication setup (see [Authentication](#authentication)).
2. Refresh the schema for every enabled stream and accept the changes.
3. Remove `applications_demographics_answers`, `applications_interviews`, and `jobs_stages` from the connection; 1.0.0 no longer provides them (see [Stream and schema changes](#stream-and-schema-changes)).
4. Clear (reset) the affected streams so the v1 rows are removed before the v3 backfill, then sync.
5. Update downstream models against the v3 columns.

What to expect if you take this path:

- If you skip the clear, the two record shapes coexist: v1-only columns stay in the table, permanently null on v3 rows, and dropped nested objects such as `candidates.applications` and `jobs.openings` remain populated on old rows only. In destinations that merge records, the shapes collide on the same primary keys, so v3 rows overwrite v1 rows column by column; in append modes the table accumulates both.
- Timestamp columns are typed `string` in the v1 tables and `date-time` in v3. Destinations do not retype an existing column on a schema refresh, so those columns stay strings unless the table is re-created.
- `applications` switches from the `applied_at` cursor to `updated_at` and its legacy state is discarded, so it backfills once regardless of which path you choose.
- `activity_feed` changes record grain (one row per candidate to one row per entry) and replaces every column, so drop and re-create that table rather than refreshing it.

### Authentication

Harvest v3 uses OAuth 2.0 Authorization Code authentication instead of Harvest API keys. The connector authenticates through Airbyte's registered Greenhouse partner application: click **Authenticate**, approve the Greenhouse consent flow as a Site Admin, and Airbyte stores and rotates the resulting refresh token. You don't need to obtain, request, or register Greenhouse OAuth credentials of your own; Greenhouse issues Harvest v3 partner credentials only to integration partners and doesn't allow customers to connect through their own applications. Because the consent flow depends on Airbyte's partner credentials, it's available in Airbyte Cloud only. After upgrading to 1.0.0, every existing connection must be authenticated again. If consent does not include the scopes required by an enabled stream, Greenhouse returns `403` and 1.0.0 fails the sync with a configuration error instead of silently yielding an empty stream.

Version 1.0.0 introduces a new optional `start_date` configuration value for incremental streams. When it is omitted, the connector preserves the previous full-history behavior.

### Stream and schema changes

The 33 streams carried over from 0.8.1 now use their Harvest v3 collection endpoints, and this release adds one new `custom_field_options` stream, for 34 streams in total. The v3 response schemas remove several nested v1 objects and add v3 identifiers, timestamps, and relationship fields. Examples include:

- `applications` uses `updated_at` for incremental state instead of `applied_at` and exposes flat job, stage, recruiter, coordinator, and source identifiers.
- `candidates` no longer embeds applications and uses `private`, `preferred_name`, `last_activity_at`, and linked user identifiers.
- `jobs_openings`, `offers`, and `users` use v3 relationship identifiers instead of the v1 nested objects.
- `offices.location` is a string in v3 rather than the v1 object.
- `activity_feed` changes record grain without losing content. In v1 it returned one row per candidate whose only columns were the `activities`, `emails`, and `notes` arrays, and the stream had no primary key. It now reads `GET /v3/notes` and emits one flat row per activity-feed entry, with `id` as the primary key. `GET /v3/notes` returns every entry type - candidate notes, logged emails, system activity, interview feedback, LinkedIn messages, and `TOUCHPOINT` entries - discriminated by the `type` field, and the flat row carries `subject`, `body`, `body_with_tags`, `email_to`, `email_cc`, `email_from`, and `email_attachment_file_names`. The nested v1 arrays are therefore flattened rather than dropped: filter on `type` to rebuild each of them. Because every column is replaced and the row count grows to the number of entries per candidate, drop and re-create the destination table for this stream rather than refreshing the schema in place.

#### Dropped and renamed top-level fields

Version 1.0.0 removes the redundant `applications_demographics_answers`, `applications_interviews`, and `jobs_stages` streams. Their top-level replacements are `demographics_answers`, `interviews`, and `job_stages`, respectively.

| Stream | Dropped from this stream in v3 | Renamed in v3 |
|---|---|---|
| activity_feed | `activities`, `emails`, `notes` (flattened into one row per entry, not dropped - see above) | |
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

Timestamp and date fields now carry `format: date-time` / `format: date`, so destinations type them as TIMESTAMP/DATE rather than string. This is another reason to give 1.0.0 its own tables: the v1 tables type those columns as string, and destinations do not change a column's type on a schema refresh.

Most of the fields above are not gone from Harvest. Harvest v3 moved them off the parent record onto their own collection endpoints. Version 1.2.0 syncs most of those endpoints as their own streams; enabling them on a source authorized before 1.2.0 requires re-running the consent flow, because each one needs its own scope (see [Streams added in 1.2.0](./greenhouse.md#streams-added-in-120)). The four endpoints marked "not synced" below are not read by any stream.

| Dropped v1 field | Stream in 1.2.0 and later |
|---|---|
| `applications.attachments`, `candidates.attachments` | `attachments` |
| `applications.current_stage` | `application_stages` (join on `applications.stage_id`) |
| `applications.prospect_detail`, `prospective_department`, `prospective_office` | `prospect_details` |
| `applications.rejection_details` | `rejection_details` |
| `approvals.approver_groups` | `approver_groups`, `approvers` |
| `candidates.educations` | `candidate_educations` |
| `candidates.employments` | `candidate_employments` |
| `custom_fields.departments`, `custom_fields.offices` | Not synced (`GET /v3/custom_field_departments`, `GET /v3/custom_field_offices`) |
| `interviews.interviewers` | `interviewers` |
| `job_posts.location` | Not synced (`GET /v3/job_post_locations`; a job post can carry several locations in v3) |
| `job_stages.interviews` | `job_interviews`, `interview_kits` |
| `jobs.hiring_team` | `job_hiring_managers`, `job_owners` |
| `prospect_pools.prospect_stages` | `prospect_pool_stages` |
| `scorecards.attributes` | `scorecard_candidate_attributes` |
| `scorecards.questions` | Not synced (`GET /v3/scorecard_question_answers`); `scorecard_questions` has the question text but not the answers |

`custom_fields.custom_field_options` is not removed in v3, only relocated: Harvest v3 serves it from `GET /v3/custom_field_options`. Enable the new `custom_field_options` stream and join it back to `custom_fields` on `custom_field_id` to rebuild the nested v1 array.

`custom_field_options` reads that endpoint unfiltered, so it is a superset of `degrees`, `disciplines`, and `schools`, which read the same endpoint filtered by `custom_field_key` (`degree`, `discipline`, `school_name`) and share the same `id` primary key. If you enable `custom_field_options`, disable those three unless you specifically want the split tables - otherwise the same option rows land in four destination tables and every sync pages the same endpoint four times.

### Pagination and incremental state

Harvest v3 returns opaque cursor URLs in the `Link` response header. The connector sends `per_page=500`, incremental filters, parent filters, and static filters only on the first request; cursor follow-up requests use only the cursor URL. The legacy `applied_at` watermark is discarded during the 1.0.0 upgrade because it is v3's `created_at`, so `applications` backfills once on the new `updated_at` cursor. The remaining de-fanned child streams preserve the minimum recoverable `updated_at` cursor and resume without a backfill.

`eeoc` keeps `submitted_at` as its cursor, matching 0.8.1. `/v3/eeoc` also accepts an `updated_at` filter, but switching the cursor needs a migration of the saved state of existing connections, so the connector hasn't made that change yet. Corrections made to an EEOC response after submission do not change `submitted_at`, so incremental syncs never re-read them and, with `application_id` as the primary key in destinations that merge records, the corrected values are silently missed. Re-run the stream in full refresh if you need corrections to land.

The deleted child streams were redundant in v3: `demographics_answers`, `interviews`, and `job_stages` now provide the complete collections formerly exposed through their child-stream counterparts.

### Rate limits

The connector uses Greenhouse's v3 rate-limit headers and a fixed 30-second window. Existing connections may take longer or process fewer concurrent requests while the connector uses its own conservative default request budget.

Greenhouse refresh tokens expire after approximately 24 hours of non-use and rotate on every refresh. Set each connection to sync more often than once a day. A connection left paused, turned off, or failing for more than 24 hours requires re-running the consent flow from the source settings.

## Connector upgrade guide

<MigrationGuide />
