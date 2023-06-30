/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.databricks.azure.DatabricksAzureBlobStorageConfigProvider;
import io.airbyte.integrations.destination.databricks.s3.DatabricksS3StorageConfigProvider;
import org.junit.jupiter.api.Test;

class DatabricksDestinationConfigTest {

  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

  @Test
  public void testConfigCreationFromJsonS3() {
    final ObjectNode dataSourceConfig = OBJECT_MAPPER.createObjectNode()
        .put("data_source_type", "S3_STORAGE")
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
    assertEquals(DatabricksDestinationConfig.DEFAULT_DATABRICKS_PORT, config1.port());
    assertEquals(DatabricksDestinationConfig.DEFAULT_DATABASE_SCHEMA, config1.schema());

    databricksConfig.put("databricks_port", "1000").put("schema", "testing_schema").put("enable_schema_evolution", true);
    final DatabricksDestinationConfig config2 = DatabricksDestinationConfig.get(databricksConfig);
    assertEquals("1000", config2.port());
    assertEquals("testing_schema", config2.schema());
    assertEquals(true, config2.enableSchemaEvolution());

    assertEquals(DatabricksS3StorageConfigProvider.class, config2.storageConfig().getClass());
  }

  @Test
  public void testConfigCreationFromJsonAzure() {
    final ObjectNode dataSourceConfig = OBJECT_MAPPER.createObjectNode()
        .put("data_source_type", "AZURE_BLOB_STORAGE")
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
    assertEquals(DatabricksDestinationConfig.DEFAULT_DATABRICKS_PORT, config1.port());
    assertEquals(DatabricksDestinationConfig.DEFAULT_DATABASE_SCHEMA, config1.schema());

    databricksConfig.put("databricks_port", "1000").put("schema", "testing_schema").put("enable_schema_evolution", true);
    final DatabricksDestinationConfig config2 = DatabricksDestinationConfig.get(databricksConfig);
    assertEquals("1000", config2.port());
    assertEquals("testing_schema", config2.schema());
    assertEquals(true, config2.enableSchemaEvolution());
    
    assertEquals(DatabricksAzureBlobStorageConfigProvider.class, config2.storageConfig().getClass());
  }

  @Test
  public void testDefaultCatalog() {
    final DatabricksDestinationConfig databricksDestinationConfig = DatabricksDestinationConfig.get(Jsons.deserialize(
        """
        {
          "accept_terms": true,
          "databricks_server_hostname": "abc-12345678-wxyz.cloud.databricks.com",
          "databricks_http_path": "sql/protocolvx/o/1234567489/0000-1111111-abcd90",
          "databricks_port": "443",
          "databricks_personal_access_token": "dapi0123456789abcdefghij0123456789AB",
          "database_schema": "public",
          "data_source": {
            "data_source_type": "S3_STORAGE",
            "s3_bucket_name": "required",
            "s3_bucket_path": "required",
            "s3_bucket_region": "required",
            "s3_access_key_id": "required",
            "s3_secret_access_key": "required"
          }
        }
        """));

    assertEquals("hive_metastore", databricksDestinationConfig.catalog());
  }

}
