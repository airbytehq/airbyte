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

package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.standardtest.destination.TestDestination;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.Test;

public class SnowflakeIntegrationTest extends TestDestination {

  private static final String COLUMN_NAME = "data";
  // config from which to create / delete schemas.
  private JsonNode baseConfig;
  // config which refers to the schema that the test is being run in.
  private JsonNode config;

  @Override
  protected String getImageName() {
    return "airbyte/destination-snowflake:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  private static JsonNode getStaticConfig() {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode invalidConfig = Jsons.clone(config);
    ((ObjectNode) invalidConfig).put("password", "wrong password");
    return invalidConfig;
  }

  @Test
  public void testIt() {
    assertTrue(true);
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv env, String streamName) throws Exception {
    return SnowflakeDatabase.executeSync(
        SnowflakeDatabase.getConnectionFactory(getConfig()),
        String.format("SELECT * FROM \"%s\" ORDER BY \"emitted_at\" ASC;", streamName),
        false,
        rs -> {
          try {
            List<JsonNode> nodes = new ArrayList<>();

            while (rs.next()) {
              nodes.add(Jsons.deserialize(rs.getString(COLUMN_NAME)));
            }

            return nodes;
          } catch (Exception e) {
            throw new RuntimeException(e);
          }
        });
  }

  // for each test we create a new schema in the database. run the test in there and then remove it.
  @Override
  protected void setup(TestDestinationEnv testEnv) throws Exception {
    final String schemaName = "integration_test_" + RandomStringUtils.randomAlphanumeric(5);
    final String createSchemaQuery = String.format("CREATE SCHEMA %s", schemaName);

    baseConfig = getStaticConfig();
    SnowflakeDatabase.executeSync(SnowflakeDatabase.getConnectionFactory(baseConfig), createSchemaQuery, false);

    final JsonNode configForSchema = Jsons.clone(baseConfig);
    ((ObjectNode) configForSchema).put("schema", schemaName);
    config = configForSchema;
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws Exception {
    final String createSchemaQuery = String.format("DROP SCHEMA IF EXISTS %s", config.get("schema").asText());
    SnowflakeDatabase.executeSync(SnowflakeDatabase.getConnectionFactory(baseConfig), createSchemaQuery, false);
  }

}
