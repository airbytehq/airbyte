# Bing Ads Migration Guide

## Upgrading to 2.0.0

This version update affects all hourly reports (end in report_hourly) and the following streams:

- Accounts
- Campaigns
- Search Query Performance Report
- AppInstallAds
- AppInstallAdLabels
- Labels
- Campaign Labels
- Keyword Labels
- Ad Group Labels
- Keywords
- Budget Summary Report

All `date` and `date-time` fields will be converted to standard `RFC3339`. Stream state format will be updated as well.

For the changes to take effect, please refresh the source schema and reset affected streams after you have applied the upgrade.

| Stream field                | Current Airbyte Type | New Airbyte Type  |
| --------------------------- | -------------------- | ----------------- |
| LinkedAgencies              | string               | object            |
| BiddingScheme.MaxCpc.Amount | string               | number            |
| CostPerConversion           | integer              | number            |
| Modified Time               | string               | timestamp with tz |
| Date                        | string               | date              |
| TimePeriod                  | string               | timestamp with tz |

Detailed date-time field change examples:

| Affected streams                                                                                                    | Field_name      | Old type                  | New type (`RFC3339`)            |
| ------------------------------------------------------------------------------------------------------------------- | --------------- | ------------------------- | ------------------------------- |
| `AppInstallAds`, `AppInstallAdLabels`, `Labels`, `Campaign Labels`, `Keyword Labels`, `Ad Group Labels`, `Keywords` | `Modified Time` | `04/27/2023 18:00:14.970` | `2023-04-27T16:00:14.970+00:00` |
| `Budget Summary Report`                                                                                             | `Date`          | `6/10/2021`               | `2021-06-10`                    |
| `* Report Hourly`                                                                                                   | `TimePeriod`    | `2023-11-04\|11`          | `2023-11-04T11:00:00+00:00`     |

## Upgrading to 1.0.0

This version update only affects the geographic performance reports streams.

Version 1.0.0 prevents the data loss by removing the primary keys from the `GeographicPerformanceReportMonthly`, `GeographicPerformanceReportWeekly`, `GeographicPerformanceReportDaily`, `GeographicPerformanceReportHourly` streams.
Due to multiple records with the same primary key, users could experience data loss in the incremental append+dedup mode because of deduplication.

For the changes to take effect, please reset your data and refresh the stream schemas after you have applied the upgrade.
