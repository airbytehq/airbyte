package io.airbyte.integrations.destination.databricks;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Test;

class DatabricksDestinationConfigTest {

  @Test
  public void testConfigCreationFromJson() {
    ObjectNode object = new ObjectMapper().createObjectNode()
        .put("databricks_server_hostname", "server_hostname")
        .put("databricks_http_path", "http_path")
        .put("databricks_personal_access_token", "pak")
        .put("s3_bucket_name", "bucket_name")
        .put("s3_bucket_path", "bucket_path")
        .put("s3_bucket_region", "bucket_region")
        .put("s3_access_key_id", "access_key_id")
        .put("s3_secret_access_key", "secret_access_key");
    DatabricksDestinationConfig config1 = DatabricksDestinationConfig.get(object);
    assertEquals(DatabricksDestinationConfig.DEFAULT_DATABRICKS_PORT, config1.getDatabricksPort());
    assertEquals(DatabricksDestinationConfig.DEFAULT_DATABASE_SCHEMA, config1.getDatabaseSchema());

    object.put("databricks_port", "1000").put("database_schema", "testing_schema");
    DatabricksDestinationConfig config2 = DatabricksDestinationConfig.get(object);
    assertEquals("1000", config2.getDatabricksPort());
    assertEquals("testing_schema", config2.getDatabaseSchema());
  }

}
