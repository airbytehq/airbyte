# Pipedrive Migration Guide

## Upgrading to 3.0.0

:::danger Risk of permanent data loss
Clearing a stream deletes its destination table and re-syncs it from Pipedrive. Pipedrive doesn't return records that were deleted (except deals deleted in the last 30 days), so rows for deleted deals, persons, organizations, activities, products, notes and files aren't restored. Back up the affected tables before you clear them if you need that history.
:::

Version 3.0.0 reads `deals`, `persons`, `organizations`, `activities`, `products`, `pipelines`, `stages` and `deal_products` from Pipedrive API v2, adds the `deals_archived` stream, and reads `notes`, `files`, `filters`, `users` and `leads` from their own list endpoints instead of the Recents feed. Incremental streams now backfill every record modified since your Start Date; the one-month history cap of the Recents endpoint is gone.

What changed:

API v2 schemas replace the Recents-era record shapes. The stream-specific changes are listed below; fields not listed remain unchanged.

<details><summary>Field changes in deals</summary>

- Renamed fields: `user_id` → `owner_id`; `label` → `label_ids`; `deleted` → `is_deleted`.
- Added fields: `acv`, `archive_time`, `arr`, `channel`, `channel_id`, `custom_fields`, `is_archived`, `is_deleted`, `label_ids`, `local_close_date`, `local_lost_date`, `local_won_date`, `mrr`, `origin`, `origin_id`, `owner_id`, `source_lead_id`.
- Removed fields: `active`, `activities_count`, `cc_email`, `deleted`, `done_activities_count`, `email_messages_count`, `files_count`, `first_won_time`, `followers_count`, `formatted_value`, `formatted_weighted_value`, `label`, `last_activity_date`, `last_activity_id`, `last_incoming_mail_time`, `last_outgoing_mail_time`, `next_activity_date`, `next_activity_duration`, `next_activity_id`, `next_activity_note`, `next_activity_subject`, `next_activity_time`, `next_activity_type`, `notes_count`, `org_hidden`, `org_name`, `owner_name`, `participants_count`, `person_hidden`, `person_name`, `products_count`, `rotten_time`, `stage_order_nr`, `undone_activities_count`, `user_id`, `weighted_value`, `weighted_value_currency`.
- Retyped fields: `add_time`, `close_time`, `lost_time`, `stage_change_time` and `won_time` are now RFC3339 `date-time` values; `update_time` changes from a timestamp without a time zone to RFC3339 `date-time`; `visible_to` changes from string to integer.

</details>

<details><summary>Field changes in deals_archived</summary>

- New stream: `deals_archived` uses the `deals` schema and returns archived deals from API v2.

</details>

<details><summary>Field changes in persons</summary>

- Renamed fields: `active_flag` → `is_deleted`; `email` → `emails`; `phone` → `phones`; `label` → `label_ids`.
- Added fields: `birthday`, `custom_fields`, `emails`, `im`, `is_deleted`, `job_title`, `label_ids`, `notes`, `phones`, `postal_address`.
- Removed fields: `active_flag`, `activities_count`, `cc_email`, `closed_deals_count`, `company_id`, `delete_time`, `done_activities_count`, `email`, `email_messages_count`, `files_count`, `first_char`, `followers_count`, `label`, `last_activity_date`, `last_activity_id`, `last_incoming_mail_time`, `last_outgoing_mail_time`, `lost_deals_count`, `next_activity_date`, `next_activity_id`, `next_activity_time`, `notes_count`, `open_deals_count`, `org_name`, `owner_name`, `participant_closed_deals_count`, `participant_open_deals_count`, `phone`, `picture_128_url`, `related_closed_deals_count`, `related_lost_deals_count`, `related_open_deals_count`, `related_won_deals_count`, `undone_activities_count`, `won_deals_count`.
- Retyped fields: `add_time` and `update_time` are now RFC3339 `date-time` values; `picture_id` changes from object to integer; `visible_to` changes from string to integer.

</details>

<details><summary>Field changes in organizations</summary>

- Renamed fields: `active_flag` → `is_deleted`; `label` → `label_ids`.
- Added fields: `annual_revenue`, `custom_fields`, `employee_count`, `industry`, `is_deleted`, `label_ids`, `linkedin`, `website`.
- Removed fields: `active_flag`, `activities_count`, `address_admin_area_level_1`, `address_admin_area_level_2`, `address_country`, `address_formatted_address`, `address_locality`, `address_postal_code`, `address_route`, `address_street_number`, `address_sublocality`, `address_subpremise`, `category_id`, `cc_email`, `closed_deals_count`, `company_id`, `country_code`, `delete_time`, `done_activities_count`, `email_messages_count`, `files_count`, `first_char`, `followers_count`, `label`, `last_activity_date`, `last_activity_id`, `lost_deals_count`, `next_activity_date`, `next_activity_id`, `next_activity_time`, `notes_count`, `open_deals_count`, `owner_name`, `people_count`, `picture_id`, `related_closed_deals_count`, `related_lost_deals_count`, `related_open_deals_count`, `related_won_deals_count`, `undone_activities_count`, `won_deals_count`.
- Retyped fields: `add_time` and `update_time` are now RFC3339 `date-time` values; `address` changes from string to object; `id` changes from number to integer; `owner_id` changes from object/number to integer; `visible_to` changes from number/string to integer.

</details>

<details><summary>Field changes in activities</summary>

- Renamed fields: `active_flag` → `is_deleted`; `busy_flag` → `busy`; `user_id` → `owner_id`.
- Added fields: `busy`, `creator_user_id`, `custom_fields`, `is_deleted`, `outcome`, `owner_id`, `priority`, `private`, `project_id`.
- Removed fields: `active_flag`, `assigned_to_user_id`, `busy_flag`, `calendar_sync_include_context`, `company_id`, `created_by_user_id`, `deal_dropbox_bcc`, `deal_title`, `file`, `gcal_event_id`, `google_calendar_etag`, `google_calendar_id`, `last_notification_time`, `last_notification_user_id`, `location_admin_area_level_1`, `location_admin_area_level_2`, `location_country`, `location_formatted_address`, `location_lat`, `location_locality`, `location_long`, `location_postal_code`, `location_route`, `location_street_number`, `location_sublocality`, `location_subpremise`, `notification_language_id`, `org_name`, `owner_name`, `person_dropbox_bcc`, `person_name`, `rec_master_activity_id`, `rec_rule`, `rec_rule_extension`, `reference_id`, `reference_type`, `series`, `source_timezone`, `type_name`, `update_user_id`, `user_id`.
- Retyped fields: `add_time`, `marked_as_done_time` and `update_time` are now RFC3339 `date-time` values; `due_date` changes to `date`; `attendees` and `participants` have new array/object shapes; `location` changes from string to object.

</details>

<details><summary>Field changes in products</summary>

- Renamed fields: `active_flag` → `is_deleted`.
- Added fields: `billing_frequency`, `billing_frequency_cycles`, `custom_fields`, `is_deleted`, `is_linkable`.
- Removed fields: `active_flag`, `files_count`, `first_char`, `owner_name`, `selectable`.
- Retyped fields: `add_time` and `update_time` are now RFC3339 `date-time` values; `prices` has a new array/object shape; `tax` changes from integer to number; `visible_to` changes from string to integer.

</details>

<details><summary>Field changes in pipelines</summary>

- Added fields: `is_deal_probability_enabled`, `is_deleted`.
- Removed fields: `active`, `deal_probability`, `selected`, `url_title`.
- Retyped fields: `add_time` and `update_time` are now RFC3339 `date-time` values.
- Renamed fields: `deal_probability` → `is_deal_probability_enabled`.

</details>

<details><summary>Field changes in stages</summary>

- Renamed fields: `active_flag` → `is_deleted`; `rotten_days` → `days_to_rotten`; `rotten_flag` → `is_deal_rot_enabled`.
- Added fields: `days_to_rotten`, `is_deal_rot_enabled`, `is_deleted`.
- Removed fields: `active_flag`, `pipeline_deal_probability`, `pipeline_name`, `rotten_days`, `rotten_flag`.
- Retyped fields: `add_time` and `update_time` are now RFC3339 `date-time` values.

</details>

<details><summary>Field changes in deal_products</summary>

- Renamed fields: `discount_percentage` → `discount`; `enabled_flag` → `is_enabled`; `duration` and `duration_unit` → `billing_frequency`, `billing_frequency_cycles` and `billing_start_date`.
- Added fields: `billing_frequency`, `billing_frequency_cycles`, `billing_start_date`, `discount`, `discount_type`, `is_deleted`, `is_enabled`, `tax_method`, `update_time`.
- Removed fields: `active_flag`, `discount_percentage`, `duration`, `duration_unit`, `enabled_flag`, `last_edit`, `quantity_formatted`, `sum_formatted`, `sum_no_discount`.
- Retyped fields: `add_time` is now RFC3339 `date-time`; `item_price`, `quantity` and `sum` change from integer to number.

</details>

- RFC3339 timestamps are typed as `date-time` values with a time zone, and custom fields are nested under `custom_fields`; monetary custom fields are `{value, currency}` objects instead of separate `<hash>` and `<hash>_currency` fields. Streams that stay on API v1 keep their `YYYY-MM-DD HH:MM:SS` timestamps, now typed as `date-time` without a time zone.
- `deals` returns not-archived deals and, together with the new `deals_archived` stream, includes deals deleted in the last 30 days with `is_deleted: true`.
- `deal_products` uses the API v2 shape: `discount`, `discount_type`, `is_enabled` and the `billing_*` fields replace `discount_percentage`, `enabled_flag`, `duration` and `duration_unit`.
- Sync modes: `organizations`, `notes` and `leads` are now incremental on `update_time`; `pipelines`, `stages`, `filters` and `users` are full refresh only.
- Primary keys added: `key` on `deal_fields`, `activity_fields`, `organization_fields`, `person_fields` and `product_fields`; `id` on `leads`, `lead_labels`, `activity_types`, `currencies`, `permission_sets`, `roles` and `deal_products`.

If you only sync streams that aren't listed in step 2, you don't need to take any action.

To upgrade:

1. Open the connection, go to **Schema** and click **Refresh source schema**.
   If your Start Date is later than the history you want, move it back before clearing; the re-sync only backfills records modified on or after it.
2. Clear data for `deals`, `persons`, `organizations`, `activities`, `products`, `pipelines`, `stages`, `notes`, `files`, `filters`, `users`, `deal_products`, `deal_fields`, `activity_fields`, `organization_fields`, `person_fields`, `product_fields`, `lead_labels`, `leads`, `activity_types`, `currencies`, `permission_sets` and `roles` (also for Full refresh | Overwrite streams: the retyped timestamp columns need the table rebuilt).
3. Run a sync.

### Update downstream consumers

Update downstream consumers for `user_id` (now `owner_id`), `label` (now `label_ids`), `active_flag` and `deleted` (now `is_deleted`), `persons.email` and `persons.phone` (now `emails` and `phones` arrays), `organizations.address_*`, `*_name`, `*_count`, `next_activity_*`, `last_activity_*`, and `weighted_value`. Top-level custom-field hash columns are now under `custom_fields`; monetary custom fields are `{value, currency}` objects instead of `<hash>` plus `<hash>_currency`. `visible_to` is now an integer, `organizations.address` and `activities.location` are now objects, and `update_time` and `add_time` are now timestamps. In `deal_products`, `discount`, `discount_type`, `is_enabled` and `billing_*` replace `discount_percentage`, `enabled_flag`, `duration` and `duration_unit`.

Rolling back to a 2.x version afterwards requires clearing the state of `deals`, `persons`, `activities`, `products` and `notes`: 2.x cannot read the RFC3339 cursor values that 3.0.0 saves. `deal_flow` stores the `deals` cursor in its own state, so clear it as well.

## Upgrading to 2.0.0

Please update your config and reset your data (to match the new format). This version has changed the config to only require an API key.

This version also removes the `pipeline_ids` field from the `deal_fields` stream.

Starting with version 2.4.7, configurations that still use the pre-2.0.0 `authorization.api_token` shape are migrated automatically to the top-level `api_token` field the next time the connection is tested or synced. Configurations from the OAuth-era versions (0.1.6 to 0.1.14) cannot be migrated automatically. Re-enter your API token in the **API Token** field.

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Connector upgrade guide

<MigrationGuide />
