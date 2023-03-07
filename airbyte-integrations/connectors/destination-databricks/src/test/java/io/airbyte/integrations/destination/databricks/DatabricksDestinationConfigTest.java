/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Test;

class DatabricksDestinationConfigTest {

  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

  @Test
  public void testConfigCreationFromJsonS3() {
    final ObjectNode dataSourceConfig = OBJECT_MAPPER.createObjectNode()
        .put("data_source_type", "S3")
        .put("s3_bucket_name", "bucket_name")
        .put("s3_bucket_path", "bucket_path")
        .put("s3_bucket_region", "bucket_region")
        .put("s3_access_key_id", "access_key_id")
        .put("s3_secret_access_key", "secret_access_key");

    final ObjectNode databricksConfig = OBJECT_MAPPER.createObjectNode()
        .put("databricks_server_hostname", "server_hostname")
        .put("databricks_http_path", "http_path")
        .put("databricks_personal_access_token", "pak")
        .set("data_source", dataSourceConfig);

    assertThrows(IllegalArgumentException.class, () -> DatabricksDestinationConfig.get(databricksConfig));

    databricksConfig.put("accept_terms", false);
    assertThrows(IllegalArgumentException.class, () -> DatabricksDestinationConfig.get(databricksConfig));

    databricksConfig.put("accept_terms", true);
    final DatabricksDestinationConfig config1 = DatabricksDestinationConfig.get(databricksConfig);
    assertEquals(DatabricksDestinationConfig.DEFAULT_DATABRICKS_PORT, config1.getDatabricksPort());
    assertEquals(DatabricksDestinationConfig.DEFAULT_DATABASE_SCHEMA, config1.getDatabaseSchema());

    databricksConfig.put("databricks_port", "1000").put("database_schema", "testing_schema");
    final DatabricksDestinationConfig config2 = DatabricksDestinationConfig.get(databricksConfig);
    assertEquals("1000", config2.getDatabricksPort());
    assertEquals("testing_schema", config2.getDatabaseSchema());

    assertEquals(DatabricksS3StorageConfig.class, config2.getStorageConfig().getClass());
  }

  @Test
  public void testConfigCreationFromJsonAzure() {
    final ObjectNode dataSourceConfig = OBJECT_MAPPER.createObjectNode()
        .put("data_source_type", "Azure_Blob_Storage")
        .put("azure_blob_storage_account_name", "bucket_name")
        .put("azure_blob_storage_container_name", "bucket_path")
        .put("azure_blob_storage_sas_token", "sas_token");

    final ObjectNode databricksConfig = OBJECT_MAPPER.createObjectNode()
        .put("databricks_server_hostname", "server_hostname")
        .put("databricks_http_path", "http_path")
        .put("databricks_personal_access_token", "pak")
        .set("data_source", dataSourceConfig);

    assertThrows(IllegalArgumentException.class, () -> DatabricksDestinationConfig.get(databricksConfig));

    databricksConfig.put("accept_terms", false);
    assertThrows(IllegalArgumentException.class, () -> DatabricksDestinationConfig.get(databricksConfig));

    databricksConfig.put("accept_terms", true);
    final DatabricksDestinationConfig config1 = DatabricksDestinationConfig.get(databricksConfig);
    assertEquals(DatabricksDestinationConfig.DEFAULT_DATABRICKS_PORT, config1.getDatabricksPort());
    assertEquals(DatabricksDestinationConfig.DEFAULT_DATABASE_SCHEMA, config1.getDatabaseSchema());

    databricksConfig.put("databricks_port", "1000").put("database_schema", "testing_schema");
    final DatabricksDestinationConfig config2 = DatabricksDestinationConfig.get(databricksConfig);
    assertEquals("1000", config2.getDatabricksPort());
    assertEquals("testing_schema", config2.getDatabaseSchema());

    assertEquals(DatabricksAzureBlobStorageConfig.class, config2.getStorageConfig().getClass());
  }

}
