# Mailchimp Migration Guide

## Upgrading to 2.0.0

Version 2.0.0 introduces changes in primary key for streams `Segment Members` and `List Members`.

## Migration Steps

### Refresh affected schemas and reset data

1. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update.
2. Select the **Replication** tab. 1. Select **Refresh source schema**. 2. Select **OK**.
   :::note
   Any detected schema changes will be listed for your review.
   :::
3. Select **Save changes** at the bottom of the page. 1. Ensure the **Reset affected streams** option is checked.
   :::note
   Depending on destination type you may not be prompted to reset your data.
   :::
4. Select **Save connection**.
   :::note
   This will reset the data in your destination and initiate a fresh sync.
   :::

For more information on resetting your data in Airbyte, see [this page](/operator-guides/clear).

## Upgrading to 1.0.0

Version 1.0.0 of the Source Mailchimp connector introduces a number of breaking changes to the schemas of all incremental streams. A full schema refresh and data reset are required when upgrading to this version.

### Upgrade steps

1. Select **Connections** in the main navbar.
2. From the list of your existing connections, select the connection(s) affected by the update.
3. Select the **Replication** tab, then select **Refresh source schema**.

:::note
Any detected schema changes will be listed for your review. Select **OK** when you are ready to proceed.
:::

4. At the bottom of the page, select **Save changes**. Ensure the **Reset all streams** option is checked.

:::note
Depending on the destination type, you may not be prompted to reset your data
:::

5. Select **Save connection**. This will reset the data in your destination (if applicable) and initiate a fresh sync.

## Changes

- The `._links` field, which contained non-user-relevant Mailchimp metadata, has been removed from all streams.
- All instances of datetime fields have had their type changed from `string` to airbyte-type `timestamp-with-timezone`. This change should ensure greater precision and consistency in how datetime information is represented and processed by destinations.
- The Mailchimp API returns many fields without data as empty strings. To accomodate the above changes, empty strings are now converted to null values:

```md
{"id": "record_id", "last_opened": ""} -> {"id": "record_id", "last_opened": null}
```

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
  - `variate_settings.send_times` (Array of datetime fields)

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
