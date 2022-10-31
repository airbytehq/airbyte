package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.JsonNode;

public interface MetastoreOperations extends AutoCloseable {

    //TODO (itaseskii) extend metadata with data format (json, avro, parquet)
    void upsertTable(String databaseName, String tableName, String location, JsonNode jsonSchema);

    void deleteTable(String databaseName, String tableName);


}
