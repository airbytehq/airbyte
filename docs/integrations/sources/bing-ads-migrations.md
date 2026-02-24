# Bing Ads Migration Guide

## Upgrading to 3.0.0

Version 3.0.0 changes the `ReportTimeZone` used in all report API requests from the hardcoded value `GreenwichMeanTimeDublinEdinburghLisbonLondon` (GMT) to each advertiser account's actual timezone. This aligns daily report data with what users see in the Microsoft Advertising dashboard, but it shifts historical date boundaries for accounts not in GMT.

### Who is affected

All users syncing report streams (performance reports, audience reports, geographic reports, goals and funnels reports, product dimension reports, and budget summary reports). The impact is greatest for accounts in timezones significantly ahead of or behind GMT.

### What changed

- **ReportTimeZone**: Previously hardcoded to GMT for all accounts. Now dynamically set to the account's configured timezone (e.g., `OsakaSapporoTokyo` for a Japan-based account).
- **end_datetime**: Extended by one day (`day_delta(1)`) to ensure accounts in timezones ahead of UTC receive today's data.

### Required actions

1. Refresh the source schema in your Airbyte connection settings.
2. Clear data and reset all report streams to re-sync with the correct timezone alignment.

### Notes

- Aggregate totals over multi-day periods will remain the same; only the daily breakdown alignment changes.
- Accounts already configured with the GMT timezone will see no change in behavior.

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
