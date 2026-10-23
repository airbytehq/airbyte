# Apple Ads Migration Guide

## Upgrading to 2.0.0

This breaking release types date and timestamp fields across all streams and adds primary keys to
the four daily report streams. `date` is now a date; `creationTime`, `modificationTime`,
`startTime`, and `endTime` are timestamps with timezone. The daily report stream primary keys are
`(campaignId, date, countryorregion)`, `(adGroupId, date, countryorregion)`,
`(keywordId, date, countryorregion)`, and `(adId, date, countryorregion)`, respectively.
Incremental - Append + Deduped is now available for report streams.

### Affected streams

- `campaigns`
- `adgroups`
- `keywords`
- `ads`
- `campaigns_report_daily`
- `adgroups_report_daily`
- `keywords_report_daily`
- `ads_report_daily`

## Migration Steps

Refresh the schema for the affected streams, then clear their data before syncing:

1. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update and refresh the schema.
2. Select the **Status** tab.
   1. In the **Enabled streams** list, click the three dots on the right side of each affected stream and select **Refresh** → **Clear data**.

After the clear succeeds, trigger a sync by clicking **Sync Now**. For daily report streams, you can
now select **Incremental - Append + Deduped**. For more information on clearing your data in
Airbyte, see [this page](/platform/operator-guides/clear).

## Upgrading to 1.0.0

This release introduces changes to incremental sync of `adgroups_report_daily` and `keywords_report_daily` streams, changing the stream state from per-partition state to a global state cursor. This change decreases the sync time for these streams.

### Affected streams

- `adgroups_report_daily`
- `keywords_report_daily`

## Migration Steps

To clear your data for the `adgroups_report_daily` and `keywords_report_daily` streams, follow the steps below:

1. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update.
2. Select the **Status** tab.
   1. In the **Enabled streams** list, click the three dots on the right side of the affected stream and select **Clear Data**.

After the clear succeeds, trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](/platform/operator-guides/clear).
