# Bing Ads Migration Guide

## Upgrading to 2.0.0

This version update only affects the Accounts, Campaigns and Search Query Performance Report streams. 

Version 2.0.0 updates schemas for Accounts, Campaigns and Search Query Performance Report streams. LinkedAgencies was changed from string to object in Accounts stream. 
BiddingScheme.MaxCpc.Amount was changed from string to number in Campaigns stream. And CostPerConversion was changed from integer to number. 

For the changes to take effect, please refresh the source schema and reset affected streams after you have applied the upgrade.

| Stream field                | Current Airbyte Type | New Airbyte Type |
|-----------------------------|----------------------|------------------|
| LinkedAgencies              | string               | object           |
| BiddingScheme.MaxCpc.Amount | string               | number           |
| CostPerConversion           | integer              | number           |

## Upgrading to 1.0.0

This version update only affects the geographic performance reports streams. 

Version 1.0.0 prevents the data loss by removing the primary keys from the `GeographicPerformanceReportMonthly`, `GeographicPerformanceReportWeekly`, `GeographicPerformanceReportDaily`, `GeographicPerformanceReportHourly` streams. 
Due to multiple records with the same primary key, users could experience data loss in the incremental append+dedup mode because of deduplication.

For the changes to take effect, please reset your data and refresh the stream schemas after you have applied the upgrade.