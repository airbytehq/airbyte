# Bing Ads Migration Guide

## Upgrading to 2.0.0

This update is a follow-up to the previous major update - version 1.0.0. It completes what should have been done in version 1.0.0, but unfortunately was not.
It only affects the geographic performance reports streams.

Version 2.0.0 prevents the data loss by removing the primary keys from the `GeographicPerformanceReportMonthly`, `GeographicPerformanceReportWeekly`, `GeographicPerformanceReportDaily`, `GeographicPerformanceReportHourly` streams. 
Due to multiple records with the same primary key, users could experience data loss in the incremental append+dedup mode because of deduplication.

For the changes to take effect, please reset your data and refresh the stream schemas after you have applied the upgrade.

## Upgrading to 1.0.0

This version update only affects the geographic performance reports streams. 

Version 1.0.0 prevents the data loss by removing the primary keys from the `GeographicPerformanceReportMonthly`, `GeographicPerformanceReportWeekly`, `GeographicPerformanceReportDaily`, `GeographicPerformanceReportHourly` streams. 
Due to multiple records with the same primary key, users could experience data loss in the incremental append+dedup mode because of deduplication.

For the changes to take effect, please reset your data and refresh the stream schemas after you have applied the upgrade.
