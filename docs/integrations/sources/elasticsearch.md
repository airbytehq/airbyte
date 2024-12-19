# Elasticsearch

This page contains the setup guide and reference information for the Elasticsearch source connector.

## Prerequisites

### Requirements

- Elasticsearch endpoint URL
- Elasticsearch credentials (optional)

## Supported sync modes

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

This source syncs data from an ElasticSearch domain.

## Supported Streams

This source automatically discovers all indices in the domain and can sync any of them.

## Performance Considerations

ElasticSearch calls may be rate limited by the underlying service.
This is specific to each deployment.

## Data type map

Elasticsearch data types: https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-types.html

Airbyte data types: https://docs.airbyte.com/understanding-airbyte/supported-data-types/

In Elasticsearch, there is no dedicated array data type.
Any field can contain zero or more values by default, however,
all values in the array must be of the same data type. Hence, every field can be an array as well.

| Integration Type          | Airbyte Type                               | Notes |
| :------------------------ | :----------------------------------------- | :---- |
| `binary`                  | `["string", "array"]`                      |       |
| `boolean`                 | `["boolean", "array"]`                     |       |
| `keyword`                 | `["string", "array", "number", "integer"]` |       |
| `constant_keyword`        | `["string", "array", "number", "integer"]` |       |
| `wildcard`                | `["string", "array", "number", "integer"]` |       |
| `long`                    | `["integer", "array"]`                     |       |
| `unsigned_long`           | `["integer", "array"]`                     |       |
| `integer`                 | `["integer", "array"]`                     |       |
| `short`                   | `["integer", "array"]`                     |       |
| `byte`                    | `["integer", "array"]`                     |       |
| `double`                  | `["number", "array"]`                      |       |
| `float`                   | `["number", "array"]`                      |       |
| `half_float`              | `["number", "array"]`                      |       |
| `scaled_float`            | `["number", "array"]`                      |       |
| `date`                    | `["string", "array"]`                      |       |
| `date_nanos`              | `["number", "array"]`                      |       |
| `object`                  | `["object", "array"]`                      |       |
| `flattened`               | `["object", "array"]`                      |       |
| `nested`                  | `["object", "string"]`                     |       |
| `join`                    | `["object", "string"]`                     |       |
| `integer_range`           | `["object", "array"]`                      |       |
| `float_range`             | `["object", "array"]`                      |       |
| `long_range`              | `["object", "array"]`                      |       |
| `double_range`            | `["object", "array"]`                      |       |
| `date_range`              | `["object", "array"]`                      |       |
| `ip_range`                | `["object", "array"]`                      |       |
| `ip`                      | `["string", "array"]`                      |       |
| `version`                 | `["string", "array"]`                      |       |
| `murmur3`                 | `["string", "array", "number", "integer"]` |       |
| `aggregate_metric_double` | `["string", "array", "number", "integer"]` |       |
| `histogram`               | `["string", "array", "number", "integer"]` |       |
| `text`                    | `["string", "array", "number", "integer"]` |       |
| `alias`                   | `["string", "array", "number", "integer"]` |       |
| `search_as_you_type`      | `["string", "array", "number", "integer"]` |       |
| `token_count`             | `["string", "array", "number", "integer"]` |       |
| `dense_vector`            | `["string", "array", "number", "integer"]` |       |
| `geo_point`               | `["string", "array", "number", "integer"]` |       |
| `geo_shape`               | `["string", "array", "number", "integer"]` |       |
| `shape`                   | `["string", "array", "number", "integer"]` |       |
| `point`                   | `["string", "array", "number", "integer"]` |       |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                        |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------- |
| 0.1.3 | 2024-12-18 | [49863](https://github.com/airbytehq/airbyte/pull/49863) | Use a base image: airbyte/java-connector-base:1.0.0 |
| 0.1.2 | 2024-02-13 | [35230](https://github.com/airbytehq/airbyte/pull/35230) | Adopt CDK 0.20.4 |
| `0.1.2` | 2024-01-24 | [34453](https://github.com/airbytehq/airbyte/pull/34453) | bump CDK version               |
| `0.1.1` | 2022-12-02 | [18118](https://github.com/airbytehq/airbyte/pull/18118) | Avoid too_long_frame_exception |
| `0.1.0` | 2022-07-12 | [14118](https://github.com/airbytehq/airbyte/pull/14118) | Initial Release                |

</details>
