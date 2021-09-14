/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.databricks;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.Test;

class DatabricksDestinationConfigTest {

  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

  @Test
  public void testConfigCreationFromJson() {
    ObjectNode dataSourceConfig = OBJECT_MAPPER.createObjectNode()
        .put("data_source_type", "S3")
        .put("s3_bucket_name", "bucket_name")
        .put("s3_bucket_path", "bucket_path")
        .put("s3_bucket_region", "bucket_region")
        .put("s3_access_key_id", "access_key_id")
        .put("s3_secret_access_key", "secret_access_key");

    ObjectNode databricksConfig = OBJECT_MAPPER.createObjectNode()
        .put("databricks_server_hostname", "server_hostname")
        .put("databricks_http_path", "http_path")
        .put("databricks_personal_access_token", "pak")
        .set("data_source", dataSourceConfig);

    DatabricksDestinationConfig config1 = DatabricksDestinationConfig.get(databricksConfig);
    assertEquals(DatabricksDestinationConfig.DEFAULT_DATABRICKS_PORT, config1.getDatabricksPort());
    assertEquals(DatabricksDestinationConfig.DEFAULT_DATABASE_SCHEMA, config1.getDatabaseSchema());

    databricksConfig.put("databricks_port", "1000").put("database_schema", "testing_schema");
    DatabricksDestinationConfig config2 = DatabricksDestinationConfig.get(databricksConfig);
    assertEquals("1000", config2.getDatabricksPort());
    assertEquals("testing_schema", config2.getDatabaseSchema());
  }

}
