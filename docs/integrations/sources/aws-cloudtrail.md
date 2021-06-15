# Twilio

## Overview

The AWS CloudTrail source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This Source Connector is based on a [Boto3 CloudTrail](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudtrail.html).

### Output schema

This Source is capable of syncing the following core Streams:

* [Events](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudtrail.html#CloudTrail.Client.lookup_events)

Only Management events supported right now.

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `number` | `integer` |  |
| `array` | `array` |  |
| `object` | `object` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Namespaces | No |  |

### Performance considerations

The rate of lookup requests for `events` stream is limited to two per second, per account, per region. If this limit is exceeded, a throttling error occurs.

## Getting started

### Requirements

* AWS Access key ID
* AWS Secret access key
* AWS region name

### Setup guide

Please, follow this [steps](https://docs.aws.amazon.com/powershell/latest/userguide/pstools-appendix-sign-up.html) to get your AWS access key and secret.
