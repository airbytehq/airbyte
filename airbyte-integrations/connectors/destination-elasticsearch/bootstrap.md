# Elasticsearch Destination

Elasticsearch is a Lucene based search engine that's a type of NoSql storage.  
Documents are created in an `index`, similar to a `table`in a relation database.

The documents are structured with fields that may contain nested complex structures.  
[Read more about Elastic](https://elasticsearch.org/)

This connector maps an incoming `stream` to an Elastic `index`.  
When using destination sync mode `append` and `append_dedup`, an `upsert` operation is performed against the Elasticsearch index.  
When using `overwrite`, the records/docs are place in a temp index, then cloned to the target index.
The target index is deleted first, if it exists before the sync.

The [ElasticsearchConnection.java](./src/main/java/io/airbyte/integrations/destination/elasticsearch/ElasticsearchConnection.java)
handles the communication with the Elastic server.
This uses the `elasticsearch-java` rest client from the Elasticsearch team -  
[https://github.com/elastic/elasticsearch-java/](https://github.com/elastic/elasticsearch-java/)

The [ElasticsearchAirbyteMessageConsumerFactory.java](./src/main/java/io/airbyte/integrations/destination/elasticsearch/ElasticsearchAirbyteMessageConsumerFactory.java)
contains the logic for organizing a batch of records and reporting progress.

The `namespace` and stream `name` are used to generate an index name.  
The index is created if it doesn't exist, but no other index configuration is done at this time.

Elastic will determine the type of data by detection.  
You can create an index ahead of time for field type customization.

Basic authentication and API key authentication are supported.

## Development

See the Elasticsearch client tests for examples on how to use the library.

[https://github.com/elastic/elasticsearch-java/blob/main/java-client/src/test/java/co/elastic/clients/elasticsearch/end_to_end/RequestTest.java](https://github.com/elastic/elasticsearch-java/blob/main/java-client/src/test/java/co/elastic/clients/elasticsearch/end_to_end/RequestTest.java)
