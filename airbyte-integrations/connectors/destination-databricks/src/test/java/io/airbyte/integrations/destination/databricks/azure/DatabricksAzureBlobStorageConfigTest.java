/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.azure;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.integrations.destination.databricks.DatabricksStorageConfigProvider;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class DatabricksAzureBlobStorageConfigTest {

  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();
  private DatabricksStorageConfigProvider storageConfig;

  @BeforeEach
  public void setup() {
    final ObjectNode dataSourceConfig = OBJECT_MAPPER.createObjectNode()
        .put("data_source_type", "AZURE_BLOB_STORAGE")
        .put("azure_blob_storage_account_name", "bucket_name")
        .put("azure_blob_storage_container_name", "bucket_path")
        .put("azure_blob_storage_sas_token", "sas_token");

    storageConfig = DatabricksStorageConfigProvider.getDatabricksStorageConfig(dataSourceConfig);
  }

  @Test
  public void testRetrieveAzureConfig() {
    assertNotNull(storageConfig.getAzureBlobStorageConfigOrThrow());
  }

  @Test
  public void testCannotRetrieveS3Config() {
    assertThrows(UnsupportedOperationException.class, () -> storageConfig.getS3DestinationConfigOrThrow());
  }

}
