# Redpanda

The Airbyte Redpanda destination connector allows you to sync data to [Redpada](https://redpanda.com/). Each stream is written to the corresponding Redpanda topic.

## Sync overview

### Output schema

Each stream will be output into a Redpanda topic.

The Redpanda topic will be created with the following format `{namespace}_{stream}`

Currently, this connector only writes data with JSON format. More formats \(e.g. Apache Avro\) will be supported in the future.

Each record will contain in its key the uuid assigned by Airbyte, and in the value these 3 fields:

- `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed.
- `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source.
- `_airbyte_data`: a json blob representing with the event data.

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |

### Features

This section should contain a table with the following format:

| Feature                        | Supported?\(Yes/No\) | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | No                   |       |
| Incremental - Append Sync      | Yes                  |       |
| Incremental - Append + Deduped | No                   |       |
| Namespaces                     | Yes                  |       |

### Performance considerations

Granted you have enough Redpanda nodes/partitions the cluster should be able to handle any type of load you throw at it from the connector.

## Getting started

### Requirements

- The connector should be able to create topics using the [AdminClient](https://docs.confluent.io/platform/current/installation/configuration/admin-configs.html)
- Configuration options
  - **Bootstrap servers**
  - **Buffer Memory**
  - **Compression Type**
  - **Batch Size**
  - **Retries**
  - **Number of topic partitions**
  - **Topic replication factor**
  - **Socket Connection Setup Timeout**
  - **Socket Connection Setup Max Timeout**

More info about this can be found in the [Redpanda producer configs documentation site](https://docs.confluent.io/platform/current/installation/configuration/producer-configs.html).

_NOTE_: Configurations for SSL are not available yet.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject        |
| :------ | :--------- | :------------------------------------------------------- | :------------- |
| 0.1.0   | 2022-08-05 | [18884](https://github.com/airbytehq/airbyte/pull/18884) | Initial commit |

</details>