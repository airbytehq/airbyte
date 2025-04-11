# Source Custom API Connector

## Overview
This connector allows you to import data from Google's SOAP Ads APIs into Airbyte. 
The connector creates a report with user provided set of dimensions and columns, attributes, dates. Then the connector donwloads the report as CSV file, divides it in chunks and sends each chunk as an Airbyte message. 
The connector is currently using the [the v202502 version of the APIs](https://developers.google.com/ad-manager/api/rel_notes#v202502) and supports both full and incremental synchronization. 

## Prerequisites
- A Google Ad Manager account with API access enabled
- A Google Ad Manager network with its network code
- A Service Account (SA) to read and write from Google Ad Manager account

## Setup
1. Set up a Google Ad Manager account. Look at the guide here `https://support.google.com/admanager/topic/7505789?hl=en&ref_topic=7505988&sjid=13020474609395393555-EU`. Create a network and turn on API access following the guide.
2. Generate a SA with its key. We use [GCP's service account](https://cloud.google.com/iam/docs/service-account-overview)
3. Add SA with "Administrator" role in Admin / Access & authorization section

## Configuration Parameters

| Parameter | Type | Required | Description |
|-----------|------|-----------|-------------|
| `chunk_size` | string | Yes | The number of rows processed in each batch when reading CSV data. Recommended values: 1,000-10,000 depending on available memory and data complexity.
| `dimensions` | array | Yes | The break-down and filterable types available for running a ReportJob.
| `columns` | array | Yes | All the trafficking statistics and revenue information available for the chosen Dimension objects.
| `dateRangeType` | string | Yes | The set of days to include in the report. We set fixed value "CUSTOM_DATE" one can fill with yyyy-mm-dd date.
| `adUnitView` | string | Yes | The table structure of the report as a flat table or hierarchical table. We set fixed value "FLAT".
| `service_account` | string | Yes | The service account key with access to the Google Ad Manager account.
| `network_code` | string | Yes | The unique code used to identify the Ad Manager network.
| `dimensionAttributes` | array | No | The list of break-down attributes being requested in the report.
| `startDate` | string | Yes | The report start date.
| `endDate` | string | Yes | The report end date.

## Report Fields Reference

The available fields for report generation and their accepted values can be found in the official Google Ad Manager API documentation:
[ReportQuery Fields Reference](https://developers.google.com/ad-manager/api/reference/v202405/ReportService.ReportQuery#field)

When configuring this connector, refer to this documentation to ensure you're using valid field names and values in your report specifications.

### Configuration Example
```json
{
  "columns": [
      "TOTAL_CODE_SERVED_COUNT",
      "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS",
      "TOTAL_LINE_ITEM_LEVEL_ALL_REVENUE"
  ],
  "endDate": "2024-06-14",
  "startDate": "2024-01-01",
  "adUnitView": "FLAT",
  "chunk_size": "10000",
  "dimensions": [
      "ORDER_ID",
      "AD_UNIT_ID",
      "PROGRAMMATIC_CHANNEL_ID",
      "ORDER_NAME",
      "PROGRAMMATIC_CHANNEL_NAME"
  ],
  "network_code": "****",
  "dateRangeType": "CUSTOM_DATE",
  "service_account": "****"
}