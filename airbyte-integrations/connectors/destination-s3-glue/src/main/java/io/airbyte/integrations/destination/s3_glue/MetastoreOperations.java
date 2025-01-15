/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_glue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.protocol.models.v0.SyncMode;

// TODO (itaseskii) allow config based implementation of different metastores i.e Hive, Nessie, etc.
public interface MetastoreOperations extends AutoCloseable {

  void upsertTable(String databaseName, String tableName, String location, JsonNode jsonSchema, String serializationLibrary, S3DestinationConfig s3DestinationConfig, SyncMode syncMode);

  void deleteTable(String databaseName, String tableName);

  @Override
  void close();

}
