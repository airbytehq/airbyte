/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iomete;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class IometeDestinationConfigTest {

  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

  @Test
  public void testConfigCreationFromJson() {
    final ObjectNode dataSourceConfig = OBJECT_MAPPER.createObjectNode()
        .put("data_source_type", "S3")
        .put("s3_bucket_name", "bucket_name")
        .put("s3_bucket_path", "bucket_path")
        .put("s3_bucket_region", "bucket_region")
        .put("s3_access_key_id", "access_key_id")
        .put("s3_secret_access_key", "secret_access_key");

    final ObjectNode iometeConfig = OBJECT_MAPPER.createObjectNode()
        .put("warehouse_hostname", "hostname")
        .put("warehouse_name", "warehouse_name")
        .put("iomete_account_number", "1231425135")
        .put("iomete_username", "username")
        .put("iomete_password", "pass")
        .set("data_source", dataSourceConfig);

    final IometeDestinationConfig config1 = IometeDestinationConfig.get(iometeConfig);
    assertEquals(IometeDestinationConfig.DEFAULT_WAREHOUSE_PORT, config1.getWarehousePort());
    assertEquals(IometeDestinationConfig.DEFAULT_DATABASE_SCHEMA, config1.getDatabaseSchema());

    iometeConfig.put("warehouse_port", "1234").put("database_schema", "test_schema");
    final IometeDestinationConfig config2 = IometeDestinationConfig.get(iometeConfig);
    assertEquals("1234", config2.getWarehousePort());
    assertEquals("test_schema", config2.getDatabaseSchema());
  }

}
