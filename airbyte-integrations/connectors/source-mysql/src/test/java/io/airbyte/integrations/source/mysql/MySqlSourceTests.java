/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
import static org.assertj.core.api.AssertionsForClassTypes.catchThrowable;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.MySQLContainer;
import org.testcontainers.containers.output.Slf4jLogConsumer;

public class MySqlSourceTests {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlSourceTests.class);

  private static final String TEST_USER = "test";
  private static final String TEST_PASSWORD = "test";

  @Test
  public void testSettingTimezones() throws Exception {
    // start DB
    try (final MySQLContainer<?> container = new MySQLContainer<>("mysql:8.0")
        .withUsername(TEST_USER)
        .withPassword(TEST_PASSWORD)
        .withEnv("MYSQL_ROOT_HOST", "%")
        .withEnv("MYSQL_ROOT_PASSWORD", TEST_PASSWORD)
        .withEnv("TZ", "Europe/Moscow")
        .withLogConsumer(new Slf4jLogConsumer(LOGGER))) {

      container.start();

      final Properties properties = new Properties();
      properties.putAll(ImmutableMap.of("user", "root", JdbcUtils.PASSWORD_KEY, TEST_PASSWORD, "serverTimezone", "Europe/Moscow"));
      DriverManager.getConnection(container.getJdbcUrl(), properties);
      final String dbName = Strings.addRandomSuffix("db", "_", 10);
      final JsonNode config = getConfig(container, dbName, "serverTimezone=Europe/Moscow");

      try (final Connection connection = DriverManager.getConnection(container.getJdbcUrl(), properties)) {
        connection.createStatement().execute("GRANT ALL PRIVILEGES ON *.* TO '" + TEST_USER + "'@'%';\n");
        connection.createStatement().execute("CREATE DATABASE " + config.get(JdbcUtils.DATABASE_KEY).asText());
      }
      final AirbyteConnectionStatus check = new MySqlSource().check(config);
      assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, check.getStatus());
    }
  }

  private static JsonNode getConfig(final MySQLContainer dbContainer, final String dbName, final String jdbcParams) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, dbContainer.getHost())
        .put(JdbcUtils.PORT_KEY, dbContainer.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, dbName)
        .put(JdbcUtils.USERNAME_KEY, TEST_USER)
        .put(JdbcUtils.PASSWORD_KEY, TEST_PASSWORD)
        .put(JdbcUtils.JDBC_URL_PARAMS_KEY, jdbcParams)
        .build());
  }

  @Test
  void testJdbcUrlWithEscapedDatabaseName() {
    final JsonNode jdbcConfig = new MySqlSource().toDatabaseConfig(buildConfigEscapingNeeded());
    assertNotNull(jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
    assertTrue(jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText().startsWith(EXPECTED_JDBC_ESCAPED_URL));
  }

  private static final String EXPECTED_JDBC_ESCAPED_URL = "jdbc:mysql://localhost:1111/db%2Ffoo?";

  private JsonNode buildConfigEscapingNeeded() {
    return Jsons.jsonNode(ImmutableMap.of(
        JdbcUtils.HOST_KEY, "localhost",
        JdbcUtils.PORT_KEY, 1111,
        JdbcUtils.USERNAME_KEY, "user",
        JdbcUtils.DATABASE_KEY, "db/foo"));
  }

  @Test
  @Disabled("See https://github.com/airbytehq/airbyte/pull/23908#issuecomment-1463753684, enable once communication is out")
  public void testTableWithNullCursorValueShouldThrowException() throws SQLException {
    try (final MySQLContainer<?> db = new MySQLContainer<>("mysql:8.0")
        .withUsername(TEST_USER)
        .withPassword(TEST_PASSWORD)
        .withEnv("MYSQL_ROOT_HOST", "%")
        .withEnv("MYSQL_ROOT_PASSWORD", TEST_PASSWORD)) {
      db.start();
      final JsonNode config = getConfig(db, "test", "");
      try (Connection connection = DriverManager.getConnection(db.getJdbcUrl(), "root", config.get(JdbcUtils.PASSWORD_KEY).asText())) {
        final ConfiguredAirbyteStream table = createTableWithNullValueCursor(connection);
        final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(Collections.singletonList(table));

        final Throwable throwable = catchThrowable(() -> MoreIterators.toSet(new MySqlSource().read(config, catalog, null)));
        assertThat(throwable).isInstanceOf(ConfigErrorException.class)
            .hasMessageContaining(
                "The following tables have invalid columns selected as cursor, please select a column with a well-defined ordering with no null values as a cursor. {tableName='test.null_cursor_table', cursorColumnName='id', cursorSqlType=INT, cause=Cursor column contains NULL value}");

      } finally {
        db.stop();
      }
    }
  }

  private ConfiguredAirbyteStream createTableWithNullValueCursor(final Connection connection) throws SQLException {
    connection.createStatement().execute("GRANT ALL PRIVILEGES ON *.* TO '" + TEST_USER + "'@'%';\n");
    connection.createStatement().execute("CREATE TABLE IF NOT EXISTS test.null_cursor_table(id INTEGER NULL)");
    connection.createStatement().execute("INSERT INTO test.null_cursor_table(id) VALUES (1), (2), (NULL)");

    return new ConfiguredAirbyteStream().withSyncMode(SyncMode.INCREMENTAL)
        .withCursorField(Lists.newArrayList("id"))
        .withDestinationSyncMode(DestinationSyncMode.APPEND)
        .withSyncMode(SyncMode.INCREMENTAL)
        .withStream(CatalogHelpers.createAirbyteStream(
            "null_cursor_table",
            "test",
            Field.of("id", JsonSchemaType.STRING))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of("id"))));

  }

  @Test
  @Disabled("See https://github.com/airbytehq/airbyte/pull/23908#issuecomment-1463753684, enable once communication is out")
  public void viewWithNullValueCursorShouldThrowException() throws SQLException {
    try (final MySQLContainer<?> db = new MySQLContainer<>("mysql:8.0")
        .withUsername(TEST_USER)
        .withPassword(TEST_PASSWORD)
        .withEnv("MYSQL_ROOT_HOST", "%")
        .withEnv("MYSQL_ROOT_PASSWORD", TEST_PASSWORD)) {
      db.start();
      final JsonNode config = getConfig(db, "test", "");
      try (Connection connection = DriverManager.getConnection(db.getJdbcUrl(), "root", config.get(JdbcUtils.PASSWORD_KEY).asText())) {
        final ConfiguredAirbyteStream table = createViewWithNullValueCursor(connection);
        final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(Collections.singletonList(table));

        final Throwable throwable = catchThrowable(() -> MoreIterators.toSet(new MySqlSource().read(config, catalog, null)));
        assertThat(throwable).isInstanceOf(ConfigErrorException.class)
            .hasMessageContaining(
                "The following tables have invalid columns selected as cursor, please select a column with a well-defined ordering with no null values as a cursor. {tableName='test.test_view_null_cursor', cursorColumnName='id', cursorSqlType=INT, cause=Cursor column contains NULL value}");

      } finally {
        db.stop();
      }
    }
  }

  private ConfiguredAirbyteStream createViewWithNullValueCursor(final Connection connection) throws SQLException {

    connection.createStatement().execute("GRANT ALL PRIVILEGES ON *.* TO '" + TEST_USER + "'@'%';\n");
    connection.createStatement().execute("CREATE TABLE IF NOT EXISTS test.test_table_null_cursor(id INTEGER NULL)");
    connection.createStatement().execute("""
                                         CREATE VIEW test_view_null_cursor(id) as
                                         SELECT test_table_null_cursor.id
                                         FROM test_table_null_cursor
                                         """);
    connection.createStatement().execute("INSERT INTO test.test_table_null_cursor(id) VALUES (1), (2), (NULL)");

    return new ConfiguredAirbyteStream().withSyncMode(SyncMode.INCREMENTAL)
        .withCursorField(Lists.newArrayList("id"))
        .withDestinationSyncMode(DestinationSyncMode.APPEND)
        .withSyncMode(SyncMode.INCREMENTAL)
        .withStream(CatalogHelpers.createAirbyteStream(
            "test_view_null_cursor",
            "test",
            Field.of("id", JsonSchemaType.STRING))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of("id"))));

  }

  @Test
  void testParseJdbcParameters() {
    Map<String, String> parameters =
        MySqlSource.parseJdbcParameters("theAnswerToLiveAndEverything=42&sessionVariables=max_execution_time=10000&foo=bar", "&");
    assertEquals("max_execution_time=10000", parameters.get("sessionVariables"));
    assertEquals("42", parameters.get("theAnswerToLiveAndEverything"));
    assertEquals("bar", parameters.get("foo"));
  }

  @Test
  public void testJDBCSessionVariable() throws Exception {
    // start DB
    try (final MySQLContainer<?> container = new MySQLContainer<>("mysql:8.0")
        .withUsername(TEST_USER)
        .withPassword(TEST_PASSWORD)
        .withEnv("MYSQL_ROOT_HOST", "%")
        .withEnv("MYSQL_ROOT_PASSWORD", TEST_PASSWORD)
        .withLogConsumer(new Slf4jLogConsumer(LOGGER))) {

      container.start();
      final Properties properties = new Properties();
      properties.putAll(ImmutableMap.of("user", "root", JdbcUtils.PASSWORD_KEY, TEST_PASSWORD));
      DriverManager.getConnection(container.getJdbcUrl(), properties);
      final String dbName = Strings.addRandomSuffix("db", "_", 10);
      final JsonNode config = getConfig(container, dbName, "sessionVariables=MAX_EXECUTION_TIME=28800000");

      try (final Connection connection = DriverManager.getConnection(container.getJdbcUrl(), properties)) {
        connection.createStatement().execute("GRANT ALL PRIVILEGES ON *.* TO '" + TEST_USER + "'@'%';\n");
        connection.createStatement().execute("CREATE DATABASE " + config.get(JdbcUtils.DATABASE_KEY).asText());
      }
      final AirbyteConnectionStatus check = new MySqlSource().check(config);
      assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, check.getStatus());
    }
  }

}
