# Azure Table Storage

## Overview

The Azure table storage supports Full Refresh and Incremental syncs. You can choose which tables you want to replicate.

### Output schema

This Source have generic schema for all streams.
Azure Table storage is a service that stores non-relational structured data (also known as structured NoSQL data). There is no efficient way to read schema for the given table. We use `data` property to have all the properties for any given row. 

- data - This property contain all values
- additionalProperties - This property denotes that all the values are in `data` property.

`
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
`

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

* Azure Storage Account
* Azure Storage Account Key
* Azure Storage Endpoint Suffix

### Setup guide

Visit the [Azure Portal](https://portal.azure.com). Go to your storage account, you can find :
 - Azure Storage Account - under the overview tab
 - Azure Storage Account Key - under the Access keys tab
 - Azure Storage Endpoint Suffix - under the Enpoint tab

We recommend creating a restricted key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access. However, shared access key authentication is not supported by this connector yet.


## Changelog

| Version | Date       | Pull Request                                             | Subject                                           |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------ |
| 0.1.3   | 2022-08-12 | [15591](https://github.com/airbytehq/airbyte/pull/15591) | Clean instantiation of AirbyteStream              |
| 0.1.2   | 2021-12-23 | [14212](https://github.com/airbytehq/airbyte/pull/14212) | Adding incremental load capability                |
| 0.1.1   | 2021-12-23 | [8434](https://github.com/airbytehq/airbyte/pull/8434)   | Update fields in source-connectors specifications |

