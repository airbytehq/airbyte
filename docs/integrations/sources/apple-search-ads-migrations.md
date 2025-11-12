# Apple Ads Migration Guide

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
