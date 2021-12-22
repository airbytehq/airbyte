/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Properties;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class SnowflakeDestinationIntegrationTest {
  private final SnowflakeSQLNameTransformer namingResolver = new SnowflakeSQLNameTransformer();

  @Test
  public void testInvalidSchemaName() throws IOException {
    final JsonNode config = Jsons.deserialize(new String(Files.readAllBytes(Paths.get("secrets/insert_config.json"))));
    final String schemaName = "schemaName with whitespace "+ Strings.addRandomSuffix("integration_test", "_", 5);
    ((ObjectNode) config).put("schema", schemaName);
    assertThrows(SQLException.class, () -> syncWithoutNamingResolver(config));

  }

  private void syncWithoutNamingResolver(JsonNode config) throws SQLException {
    String schemaName = config.get("schema").asText();
    final String createSchemaQuery = String.format("CREATE SCHEMA %s", schemaName);

    try (Connection connection = getConnection(config, false)) {
      Statement statement = connection.createStatement();
      statement.execute(createSchemaQuery);
    }
  }

  public Connection getConnection(JsonNode config, boolean useNameTransformer) throws SQLException {

    final String connectUrl = String.format("jdbc:snowflake://%s", config.get("host").asText());

    final Properties properties = new Properties();

    properties.put("user", config.get("username").asText());
    properties.put("password", config.get("password").asText());
    properties.put("warehouse", config.get("warehouse").asText());
    properties.put("database", config.get("database").asText());
    properties.put("role", config.get("role").asText());
    properties.put("schema", useNameTransformer
            ? namingResolver.getIdentifier(config.get("schema").asText())
            : config.get("schema").asText());

    properties.put("JDBC_QUERY_RESULT_FORMAT", "JSON");

    return DriverManager.getConnection(connectUrl, properties);
  }

}
