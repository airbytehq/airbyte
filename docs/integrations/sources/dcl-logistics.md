# DCL Logistics

## Overview
TBD

### Output Schema

* [Orders](https://api.dclcorp.com/Help/Api/GET-api-v1-orders_status_order_numbers_received_from_received_to_shipped_from_shipped_to_modified_from_modified_to_fields_page_page_size_filter_extended_date)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |
| Namespaces | No |

### Performance Considerations

DCL Logistics limits the API calls using the [Leaky Bucket Algorithm](https://en.wikipedia.org/wiki/Leaky_bucket). This 
is documented on DCL Logistics [API documentation](https://api.dclcorp.com/)

## Getting started

### Requirements

* DCL Logistics API username
* DCL Logistics API password

## CHANGELOG

| Version | Date       | Pull Request | Subject |
|:--------|:-----------| :--- | :--- |
| 0.1.0   | 2022-02-04 |      | Introduce DCL Logistics Source |
