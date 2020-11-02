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
import io.airbyte.integrations.base.TestDestination;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;
import java.util.function.Function;
import java.util.function.Supplier;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.Test;

public class SnowflakeIntegrationTest extends TestDestination {

  private static final String COLUMN_NAME = "data";

  // use a unique stream name from the source so we can write to the same schema/database in Snowflake
  private static final String OLD_STREAM_NAME = "exchange_rate";
  private static final String NEW_STREAM_NAME = "exchange_rate_" + RandomStringUtils.randomAlphanumeric(5);

  @Override
  protected Function<String, String> renameFunction() {
    return x -> x.replace(OLD_STREAM_NAME, NEW_STREAM_NAME);
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-snowflake:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return getStaticConfig();
  }

  private static JsonNode getStaticConfig() {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    ObjectNode node = (ObjectNode) getConfig();
    node.put("password", "wrong password");
    return node;
  }

  @Test
  public void testIt() {
    assertTrue(true);
  }

  // todo: DRY
  private static Supplier<Connection> getConnectionFactory(JsonNode config) {
    final String connectUrl = String.format("jdbc:snowflake://%s", config.get("host").asText());

    Properties properties = new Properties();
    properties.put("user", config.get("username").asText());
    properties.put("password", config.get("password").asText());
    properties.put("warehouse", config.get("warehouse").asText());
    properties.put("database", config.get("database").asText());
    properties.put("role", config.get("role").asText());
    properties.put("schema", config.get("schema").asText());

    // todo: queryTimeout
    // todo: networkTimeout

    return () -> {
      try {
        return DriverManager.getConnection(connectUrl, properties);
      } catch (SQLException e) {
        throw new RuntimeException(e);
      }
    };
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv env, String streamName) throws Exception {
    return SnowflakeDatabase.executeSync(
        getConnectionFactory(getConfig()),
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

  @Override
  protected void setup(TestDestinationEnv testEnv) throws Exception {
    // no-op
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws Exception {
    SnowflakeDatabase.executeSync(
        getConnectionFactory(getStaticConfig()),
        String.format("DROP TABLE IF EXISTS \"%s\";", NEW_STREAM_NAME));
  }

}
