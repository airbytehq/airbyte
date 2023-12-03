# Mailchimp Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 of the Source Mailchimp connector introduces a number of breaking changes to the schemas of all incremental streams.

- The `._links` field, which contained non-user relevant Mailchimp metadata, has been removed from all streams.
- Multiple instances of timestamp fields have had their type changed from `string` to airbyte-type `timestamp-with-timezone`. This change should improve the accuracy of types in destinations.

A full schema refresh and data reset are required when upgrading to this version.

### Updated datetime fields

- Automations:
  - `create_time`
  - `send_time`

- Campaigns:
  - `create_time`
  - `send_time`
  - `rss_opts.last_sent`
  - `ab_split_opts.send_time_a`
  - `ab_split_opts.send_time_b`
  - `variate_settings.send_times` (Array of datetimes)

- Email Activity:
  - `timestamp`

- List Members:
  - `timestamp_signup`
  - `timestamp_opt`
  - `last_changed`
  - `created_at`

- Lists:
  - `date_created`
  - `stats.campaign_last_sent`
  - `stats.last_sub_date`
  - `stats.last_unsub_date`

- Reports:
  - `send_time`
  - `rss_last_send`
  - `opens.last_open`
  - `clicks.last_click`
  - `ab_split.a.last_open`
  - `ab_split.b.last_open`
  - `timewarp.last_open`
  - `timeseries.timestamp`

- Segment Members:
  - `timestamp_signup`
  - `timestamp_opt`
  - `last_changed`
  - `last_note.created_at`

- Segments:
  - `created_at`
  - `updated_at`

- Unsubscribes:
  - `timestamp`
