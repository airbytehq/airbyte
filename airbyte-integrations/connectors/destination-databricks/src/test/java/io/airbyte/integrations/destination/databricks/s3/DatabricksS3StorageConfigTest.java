/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.s3;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.integrations.destination.databricks.DatabricksStorageConfigProvider;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class DatabricksS3StorageConfigTest {

  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();
  private DatabricksStorageConfigProvider storageConfig;

  @BeforeEach
  public void setup() {
    final ObjectNode dataSourceConfig = OBJECT_MAPPER.createObjectNode()
        .put("data_source_type", "S3_STORAGE")
        .put("s3_bucket_name", "bucket_name")
        .put("s3_bucket_path", "bucket_path")
        .put("s3_bucket_region", "bucket_region")
        .put("s3_access_key_id", "access_key_id")
        .put("s3_secret_access_key", "secret_access_key");

    storageConfig = DatabricksStorageConfigProvider.getDatabricksStorageConfig(dataSourceConfig);
  }

  @Test
  public void testRetrieveS3Config() {
    assertNotNull(storageConfig.getS3DestinationConfigOrThrow());
  }

  @Test
  public void testCannotRetrieveAzureConfig() {
    assertThrows(UnsupportedOperationException.class, () -> storageConfig.getAzureBlobStorageConfigOrThrow());
  }

}
