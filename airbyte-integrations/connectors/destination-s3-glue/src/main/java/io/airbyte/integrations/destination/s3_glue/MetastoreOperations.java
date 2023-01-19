/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_glue;

import com.fasterxml.jackson.databind.JsonNode;

// TODO (itaseskii) allow config based implementation of different metastores i.e Hive, Nessie, etc.
public interface MetastoreOperations extends AutoCloseable {

  // TODO (itaseskii) extend metadata with data format (json, avro, parquet)
  void upsertTable(String databaseName, String tableName, String location, JsonNode jsonSchema, String serializationLibrary);

  void deleteTable(String databaseName, String tableName);

  @Override
  void close();

}
