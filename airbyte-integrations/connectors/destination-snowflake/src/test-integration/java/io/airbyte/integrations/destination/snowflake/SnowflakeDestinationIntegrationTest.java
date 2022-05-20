/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import java.io.Closeable;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.sql.SQLException;
import javax.sql.DataSource;
import org.junit.jupiter.api.Test;

class SnowflakeDestinationIntegrationTest {

  private final SnowflakeSQLNameTransformer namingResolver = new SnowflakeSQLNameTransformer();

  @Test
  void testCheckFailsWithInvalidPermissions() throws Exception {
    // TODO(sherifnada) this test case is assumes config.json does not have permission to access the
    // schema
    // this connector should be updated with multiple credentials, each with a clear purpose (valid,
    // invalid: insufficient permissions, invalid: wrong password, etc..)
    final JsonNode credentialsJsonString = Jsons.deserialize(Files.readString(Paths.get("secrets/config.json")));
    final AirbyteConnectionStatus check = new SnowflakeDestination().check(credentialsJsonString);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, check.getStatus());
  }

  @Test
  public void testInvalidSchemaName() throws Exception {
    final JsonNode config = getConfig();
    final String schema = config.get("schema").asText();
    final DataSource dataSource = SnowflakeDatabase.createDataSource(config);
    try {
      final JdbcDatabase database = SnowflakeDatabase.getDatabase(dataSource);
      assertDoesNotThrow(() -> syncWithNamingResolver(database, schema));
      assertThrows(SQLException.class, () -> syncWithoutNamingResolver(database, schema));
    } finally {
      DataSourceFactory.close(dataSource);
    }
  }

  public void syncWithNamingResolver(final JdbcDatabase database, final String schema) throws SQLException {
    final String normalizedSchemaName = namingResolver.getIdentifier(schema);
    try {
      database.execute(String.format("CREATE SCHEMA %s", normalizedSchemaName));
    } finally {
      database.execute(String.format("DROP SCHEMA IF EXISTS %s", normalizedSchemaName));
    }
  }

  private void syncWithoutNamingResolver(final JdbcDatabase database, final String schema) throws SQLException {
    try {
      database.execute(String.format("CREATE SCHEMA %s", schema));
    } finally {
      database.execute(String.format("DROP SCHEMA IF EXISTS %s", schema));
    }
  }

  private JsonNode getConfig() throws IOException {
    final JsonNode config = Jsons.deserialize(Files.readString(Paths.get("secrets/insert_config.json")));
    final String schemaName = "schemaName with whitespace " + Strings.addRandomSuffix("integration_test", "_", 5);
    ((ObjectNode) config).put("schema", schemaName);
    return config;
  }

}
