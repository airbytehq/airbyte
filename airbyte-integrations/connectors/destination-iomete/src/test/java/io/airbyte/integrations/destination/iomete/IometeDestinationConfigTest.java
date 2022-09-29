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
    final ObjectNode stagingConfig = OBJECT_MAPPER.createObjectNode()
        .put("staging_type", "S3")
        .put("s3_bucket_name", "bucket_name")
        .put("s3_bucket_path", "bucket_path")
        .put("s3_bucket_region", "bucket_region")
        .put("s3_access_key_id", "access_key_id")
        .put("s3_secret_access_key", "secret_access_key");

    final ObjectNode iometeConfig = OBJECT_MAPPER.createObjectNode()
        .put("connection_url", "connection_url")
        .put("iomete_username", "username")
        .put("iomete_password", "pass")
        .set("staging", stagingConfig);

    final IometeDestinationConfig config1 = IometeDestinationConfig.get(iometeConfig);
    assertEquals(IometeDestinationConfig.DEFAULT_LAKEHOUSE_PORT, config1.getLakehousePort());
    assertEquals(IometeDestinationConfig.DEFAULT_DATABASE_SCHEMA, config1.getDatabaseSchema());

    iometeConfig.put("database_schema", "test_schema");
    final IometeDestinationConfig config2 = IometeDestinationConfig.get(iometeConfig);
    assertEquals("test_schema", config2.getDatabaseSchema());
  }

}
