# Azure Table Storage

## Overview

The Azure table storage supports Full Refresh and Incremental syncs. You can choose which tables you want to replicate.

### Output schema

This Source have generic schema for all streams.
Azure Table storage is a service that stores non-relational structured data (also known as structured NoSQL data). There is no efficient way to read schema for the given table. We use `data` property to have all the properties for any given row.

- data - This property contains all values
- additionalProperties - This property denotes that all the values are in `data` property.

```
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "data": {
            "type": "object"
        },
        "additionalProperties": {
            "type": "boolean"
        }
    }
}
```

### Data type mapping

Azure Table Storage uses different [property](https://docs.microsoft.com/en-us/rest/api/storageservices/understanding-the-table-service-data-model#property-types) types and Airbyte uses internally \(`string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number`\). We don't apply any explicit data type mappings.

### Features

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | Yes        |
| Incremental - Dedupe Sync | No         |
| SSL connection            | Yes        |
| Namespaces                | No         |

### Performance considerations

The Azure table storage connector should not run into API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- Azure Storage Account
- Azure Storage Account Key
- Azure Storage Endpoint Suffix

### Setup guide

Visit the [Azure Portal](https://portal.azure.com). Go to your storage account, you can find :

- Azure Storage Account - under the overview tab
- Azure Storage Account Key - under the Access keys tab
- Azure Storage Endpoint Suffix - under the Endpoint tab

We recommend creating a restricted key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access. However, shared access key authentication is not supported by this connector yet.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                           |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------ |
| 0.1.22 | 2024-09-07 | [45248](https://github.com/airbytehq/airbyte/pull/45248) | Update dependencies |
| 0.1.21 | 2024-08-31 | [45039](https://github.com/airbytehq/airbyte/pull/45039) | Update dependencies |
| 0.1.20 | 2024-08-24 | [44623](https://github.com/airbytehq/airbyte/pull/44623) | Update dependencies |
| 0.1.19 | 2024-08-17 | [44344](https://github.com/airbytehq/airbyte/pull/44344) | Update dependencies |
| 0.1.18 | 2024-08-10 | [43677](https://github.com/airbytehq/airbyte/pull/43677) | Update dependencies |
| 0.1.17 | 2024-08-03 | [43292](https://github.com/airbytehq/airbyte/pull/43292) | Update dependencies |
| 0.1.16 | 2024-07-27 | [42734](https://github.com/airbytehq/airbyte/pull/42734) | Update dependencies |
| 0.1.15 | 2024-07-20 | [42274](https://github.com/airbytehq/airbyte/pull/42274) | Update dependencies |
| 0.1.14 | 2024-07-13 | [41929](https://github.com/airbytehq/airbyte/pull/41929) | Update dependencies |
| 0.1.13 | 2024-07-10 | [41492](https://github.com/airbytehq/airbyte/pull/41492) | Update dependencies |
| 0.1.12 | 2024-07-09 | [41105](https://github.com/airbytehq/airbyte/pull/41105) | Update dependencies |
| 0.1.11 | 2024-07-06 | [40937](https://github.com/airbytehq/airbyte/pull/40937) | Update dependencies |
| 0.1.10 | 2024-06-25 | [40277](https://github.com/airbytehq/airbyte/pull/40277) | Update dependencies |
| 0.1.9 | 2024-06-22 | [40072](https://github.com/airbytehq/airbyte/pull/40072) | Update dependencies |
| 0.1.8 | 2024-06-04 | [38968](https://github.com/airbytehq/airbyte/pull/38968) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.7 | 2024-06-03 | [38915](https://github.com/airbytehq/airbyte/pull/38915) | Replace AirbyteLogger with logging.Logger |
| 0.1.6 | 2024-06-03 | [38915](https://github.com/airbytehq/airbyte/pull/38915) | Replace AirbyteLogger with logging.Logger |
| 0.1.5 | 2024-05-20 | [38443](https://github.com/airbytehq/airbyte/pull/38443) | [autopull] base image + poetry + up_to_date |
| 0.1.4 | 2024-01-26 | [34576](https://github.com/airbytehq/airbyte/pull/34576) | Migrate to per-stream/global state |
| 0.1.3 | 2022-08-12 | [15591](https://github.com/airbytehq/airbyte/pull/15591) | Clean instantiation of AirbyteStream |
| 0.1.2 | 2021-12-23 | [14212](https://github.com/airbytehq/airbyte/pull/14212) | Adding incremental load capability |
| 0.1.1 | 2021-12-23 | [8434](https://github.com/airbytehq/airbyte/pull/8434) | Update fields in source-connectors specifications |

</details>
