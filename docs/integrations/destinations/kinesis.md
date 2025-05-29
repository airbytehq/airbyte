# Kinesis

## Prerequisites

- For Airbyte Open Source users using the [Postgres](https://docs.airbyte.com/integrations/sources/postgres) source connector, [upgrade](https://docs.airbyte.com/operator-guides/upgrading-airbyte/) your Airbyte platform to version `v0.40.0-alpha` or newer and upgrade your Kinesis connector to version `0.1.4` or newer

## Sync overview

### Output schema

The incoming Airbyte data is structured in a Json format and is sent across diferent stream shards determined by the partition key.
This connector maps an incoming data from a namespace and stream to a unique Kinesis stream. The Kinesis record which is sent to the stream is consisted of the following Json fields

- `_airbyte_ab_id`: Random UUID generated to be used as a partition key for sending data to different shards.
- `_airbyte_emitted_at`: a timestamp representing when the event was received from the data source.
- `_airbyte_data`: a json text/object representing the data that was received from the data source.

### Features

| Feature                        | Support | Notes                                                                             |
| :----------------------------- | :-----: | :-------------------------------------------------------------------------------- |
| Full Refresh Sync              |   ❌    |                                                                                   |
| Incremental - Append Sync      |   ✅    | Incoming messages are streamed/appended to a Kinesis stream as they are received. |
| Incremental - Append + Deduped |   ❌    |                                                                                   |
| Namespaces                     |   ✅    | Namespaces will be used to determine the Kinesis stream name.                     |

### Performance considerations

Although Kinesis is designed to handle large amounts of real-time data by scaling streams with shards, you should be aware of the following Kinesis [Quotas and Limits](https://docs.aws.amazon.com/streams/latest/dev/service-sizes-and-limits.html).
The connector buffer size should also be tweaked according to your data size and freguency

## Getting started

### Requirements

- The connector is compatible with the latest Kinesis service version at the time of this writing.
- Configuration
  - **_Endpoint_**: Aws Kinesis endpoint to connect to. Default endpoint if not provided
  - **_Region_**: Aws Kinesis region to connect to. Default region if not provided.
  - **_shardCount_**: The number of shards with which the stream should be created. The amount of shards affects the throughput of your stream.
  - **_accessKey_**: Access key credential for authenticating with the service.
  - **_privateKey_**: Private key credential for authenticating with the service.
  - **_bufferSize_**: Buffer size used to increase throughput by sending data in a single request.

### Setup guide

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                    |
| :------ | :--------- | :------------------------------------------------------- | :------------------------- |
| 0.1.5   | 2022-09-22 | [16952](https://github.com/airbytehq/airbyte/pull/16952) | Add required config fields |

</details>