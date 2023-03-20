# Dynamodb

The Dynamodb source allows you to sync data from Dynamodb. The source supports Full Refresh and Incremental sync strategies.

## Resulting schema

Dynamodb doesn't have table schemas. The discover phase has three steps:

### Step 1. Retrieve items

The connector scans the table with a scan limit of 1k and if the data set size is > 1MB it will initiate another
scan with the same limit until it has >= 1k items.

### Step 2. Combining attributes

After retrieving the items it will combine all the different top level attributes found in the retrieved items. The implementation
assumes that the same attribute present in different items has the same type and possibly nested attributes values.

### Step 3. Determine property types

For each item attribute found the connector determines its type by calling AttributeValue.type(), depending on the received type it will map the
attribute to one of the supported Airbyte types in the schema.

## Features

| Feature | Supported |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Replicate Incremental Deletes | No |
| Namespaces | No |

### Full Refresh sync

Works as usual full refresh sync.

### Incremental sync

Cursor field can't be nested, and it needs to be top level attribute in the item.

Cursor should **never** be blank. and it needs to be either a string or integer type - the incremental sync results might be unpredictable and will totally rely on Dynamodb comparison algorithm.

Only `ISO 8601` and `epoch` cursor types are supported. Cursor type is determined based on the property type present in the previously generated schema:

* `ISO 8601` - if cursor type is string
* `epoch` - if cursor type is integer

## Getting started

This guide describes in details how you can configure the connector to connect with Dynamodb.

### Сonfiguration Parameters

* **_endpoint_**: aws endpoint of the dynamodb instance
* **_region_**: the region code of the dynamodb instance
* **_access_key_id_**: the access key for the IAM user with the required permissions
* **_secret_access_key_**: the secret key for the IAM user with the required permissions
* **_reserved_attribute_names_**: comma separated list of attribute names present in the replication tables which contain reserved words or special characters. https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.ExpressionAttributeNames.html

## Changelog


| Version | Date       | Pull Request                                    | Subject                                                              |
|:--------|:-----------|:------------------------------------------------|:---------------------------------------------------------------------|
| 0.1.2   | 01-19-2023 | https://github.com/airbytehq/airbyte/pull/20172 | Fix reserved words in projection expression & make them configurable |
| 0.1.1   | 02-09-2023 | https://github.com/airbytehq/airbyte/pull/22682 | Fix build                                                            |
| 0.1.0   | 11-14-2022 | https://github.com/airbytehq/airbyte/pull/18750 | Initial version                                                      |

