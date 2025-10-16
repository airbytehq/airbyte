# Apple Ads Migration Guide

## Upgrading to 1.0.0

This release introduces changes to incremental sync of `adgroups_daily_reports` and `keywords_daily_reports` streams, changing stream's state from per partition state to usage of a global state cursor. 
This will decrease the time of read for the streams. 

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