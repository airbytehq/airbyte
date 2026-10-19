import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Reddit Ads Migration Guide

## Upgrading to 1.0.0

:::danger Risk of permanent data loss
Clearing a stream truncates its destination data. Snapshot or back up affected tables first. A re-sync is bounded by your configured start date and by the history Reddit still serves: Reddit serves report data for the last 24 months only, so report rows older than that are not restored by a clear.
:::

### What changed

Version 1.0.0 corrects the declared types of existing fields so destinations load them as timestamps, dates and integers instead of text and floating-point numbers. Field values, primary keys and cursors are unchanged, except that report `date` values are now always `YYYY-MM-DD`.

| Stream | Field | Old type | New type |
| --- | --- | --- | --- |
| `ad` | `created_at`, `preview_expiry` | nullable string | nullable string, `format: date-time` |
| `ad` | `modified_at` | string | string, `format: date-time` |
| `campaign` | `created_at` | nullable string | nullable string, `format: date-time` |
| `campaign` | `modified_at` | string | string, `format: date-time` |
| `campaign` | `start_time`, `end_time` | not declared (not synced) | nullable string, `format: date-time` (new columns) |
| `campaign` | `spend_cap` | nullable number | nullable integer |
| `campaign_report` | `date` | string | string, `format: date` |
| `ad_account_report`, `ad_group_report`, `ad_report` | `date` | string, `format: date` | unchanged type; value now always `YYYY-MM-DD` |
| `campaign_report`, `ad_account_report`, `ad_group_report`, `ad_report` | 26 count and micro-currency metrics, listed below | nullable number | nullable integer |

The 26 metrics typed as integers on all four report streams are: `clicks`, `conversion_lead_clicks`, `conversion_lead_total_value`, `conversion_lead_views`, `conversion_page_visit_clicks`, `conversion_page_visit_views`, `conversion_purchase_clicks`, `conversion_purchase_total_items`, `conversion_purchase_total_value`, `conversion_purchase_views`, `conversion_search_clicks`, `conversion_search_views`, `conversion_sign_up_clicks`, `conversion_sign_up_views`, `conversion_signup_total_value`, `conversion_view_content_clicks`, `conversion_view_content_views`, `engaged_click`, `impressions`, `key_conversion_clicks`, `key_conversion_total_count`, `key_conversion_views`, `reach`, `reddit_leads`, `spend` and `video_viewable_impressions`.

Rate, average and cost metrics such as `cpc`, `ctr`, `ecpm`, `frequency` and the `*_ecpa`, `*_rate` and `*_avg_value` fields stay numbers. `conversion_purchase_total_value_all` also stays a number. `spend`, `spend_cap` and the cost metrics are still in Reddit's micro-currency units, and `conversion_*_total_value` is still multiplied by 100; the connector doesn't convert them.

Report `date` is now set to its first ten characters before the record is emitted. Reddit documents `date` as `YYYY-MM-DD`, so for those values nothing changes. If Reddit ever returns a time suffix such as `2026-10-13T00:00:00Z`, the connector now emits `2026-10-13`. Because `date` is part of every report stream's primary key, a row emitted with a suffix before the upgrade and the same row emitted after it would have different keys.

### Who is affected

Connections that sync `ad`, `campaign`, `campaign_report`, `ad_account_report`, `ad_group_report` or `ad_report` need to refresh their source schema. Connections that sync only `ad_account` and `ad_group` need no action.

### Steps

1. Upgrade to version 1.0.0.
2. Refresh the source schema and accept the changes.
3. Check whether your destination can change an existing column's type from string to timestamp or date, and from a floating-point number to an integer.
   - If it can, or if it stores records as JSON, no clear is needed.
   - If it can't (for example, S3 Data Lake and other Iceberg destinations reject these type changes), clear the affected streams, then sync them again. A clear is destructive and truncates the destination data for that stream.
4. `campaign.start_time` and `campaign.end_time` were not synced before. `campaign` syncs incrementally on `modified_at`, so existing campaign rows get these columns only when the campaign changes. To fill them for every campaign, clear `campaign` and sync it again.
5. A clear re-syncs from your configured start date. Report history is limited to the last 24 months, so report rows older than that will not be restored. Snapshot or back up the destination first.

### Downstream changes

Update SQL and dbt models, dashboards and exports that:

- cast or compare `ad.created_at`, `ad.modified_at`, `ad.preview_expiry`, `campaign.created_at`, `campaign.modified_at` or the report `date` as text;
- expect the 26 report metrics or `campaign.spend_cap` to be floating-point numbers. Integer division in some warehouses truncates, so cast to a decimal type before dividing, for example when converting `spend` from micro-currency.

`campaign.start_time` and `campaign.end_time` are new columns.

## Connector upgrade guide

<MigrationGuide />
