# Elasticsearch

## Sync overview

### Output schema


Elasticsearch is a Lucene based search engine that's a type of NoSql storage.  
Documents are created in an `index`, similar to a `table`in a relation database.

The output schema matches the input schema of a source. 
Each source `stream` becomes a destination `index`.  
For example, in with a relational database source -  
The DB table name is mapped to the destination index. 
The DB table columns become fields in the destination document.  
Each row becomes a document in the destination index.  

### Data type mapping

[See Elastic documentation for detailed information about the field types](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-types.html)
This section should contain a table mapping each of the connector's data types to Airbyte types. At the moment, Airbyte uses the same types used by [JSONSchema](https://json-schema.org/understanding-json-schema/reference/index.html). `string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number` are the most commonly used data types.

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| text | string | [more info](https://www.elastic.co/guide/en/elasticsearch/reference/current/text.html)
| date | date-time | [more info](https://www.elastic.co/guide/en/elasticsearch/reference/current/date.html)
| object | object | [more info](https://www.elastic.co/guide/en/elasticsearch/reference/current/object.html)
| array | array | [more info](https://www.elastic.co/guide/en/elasticsearch/reference/current/array.html)
| boolean | boolean | [more info](https://www.elastic.co/guide/en/elasticsearch/reference/current/boolean.html)
| numeric | integer | [more info](https://www.elastic.co/guide/en/elasticsearch/reference/current/number.html)
| numeric | number | [more info](https://www.elastic.co/guide/en/elasticsearch/reference/current/number.html)


### Features

This section should contain a table with the following format:

| Feature | Supported?(Yes/No) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | yes |  |
| Incremental Sync | yes |  |
| Replicate Incremental Deletes | no |  |
| SSL connection | yes |  |
| SSH Tunnel Support | ?? |  |

### Performance considerations

Batch/bulk writes are performed. Large records may impact performance.  
The connector should be enhanced to support variable batch sizes.

## Getting started

### Requirements

* Elasticsearch >= 7.x
* Configuration 
  * Endpoint URL [ex. https://elasticsearch.savantly.net:9423]
  * Username [optional] (basic auth)
  * Password [optional] (basic auth)
  * Api key ID [optional]
  * Api key secret [optional]
* If authentication is used, the user should have permission to create an index if it doesn't exist, and/or be able to `create` documents


### Setup guide

Enter the hostname and/or other configuration information ... 
## CHANGELOG

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.3 | 2022-05-30 | [14640](https://github.com/airbytehq/airbyte/pull/14640) | Include lifecycle management |
| 0.1.2 | 2022-04-19 | [11752](https://github.com/airbytehq/airbyte/pull/11752) | Reduce batch size to 32Mb |
| 0.1.1 | 2022-02-10 | [10256](https://github.com/airbytehq/airbyte/pull/1256) | Add ExitOnOutOfMemoryError connectors |
| 0.1.0 | 2021-10-13 | [7005](https://github.com/airbytehq/airbyte/pull/7005) | Initial release. |

