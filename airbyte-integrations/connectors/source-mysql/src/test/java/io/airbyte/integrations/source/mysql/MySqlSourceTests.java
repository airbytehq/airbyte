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
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.cdk.integrations.source.jdbc.AbstractJdbcSource.PrimaryKeyAttributesFromDb;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase.BaseImage;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase.ContainerModifier;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

public class MySqlSourceTests {

  public MySqlSource source() {
    return new MySqlSource();
  }

  @Test
  public void testSettingTimezones() throws Exception {
    try (final var testdb = MySQLTestDatabase.in(BaseImage.MYSQL_8, ContainerModifier.MOSCOW_TIMEZONE)) {
      final var config = testdb.testConfigBuilder()
          .with(JdbcUtils.JDBC_URL_PARAMS_KEY, "serverTimezone=Europe/Moscow")
          .withoutSsl()
          .build();
      final AirbyteConnectionStatus check = source().check(config);
      assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, check.getStatus(), check.getMessage());
    }
  }

  @Test
  void testJdbcUrlWithEscapedDatabaseName() {
    final JsonNode jdbcConfig = source().toDatabaseConfig(buildConfigEscapingNeeded());
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
  public void testNullCursorValueShouldThrowException() {
    try (final var testdb = MySQLTestDatabase.in(BaseImage.MYSQL_8)
        .with("CREATE TABLE null_cursor_table(id INTEGER NULL);")
        .with("INSERT INTO null_cursor_table(id) VALUES (1), (2), (NULL);")
        .with("CREATE VIEW null_cursor_view(id) AS SELECT null_cursor_table.id FROM null_cursor_table;")) {
      final var config = testdb.testConfigBuilder().withoutSsl().build();

      final var tableStream = new ConfiguredAirbyteStream()
          .withCursorField(Lists.newArrayList("id"))
          .withDestinationSyncMode(DestinationSyncMode.APPEND)
          .withSyncMode(SyncMode.INCREMENTAL)
          .withStream(CatalogHelpers.createAirbyteStream(
              "null_cursor_table",
              testdb.getDatabaseName(),
              Field.of("id", JsonSchemaType.STRING))
              .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
              .withSourceDefinedPrimaryKey(List.of(List.of("id"))));
      final var tableCatalog = new ConfiguredAirbyteCatalog().withStreams(List.of(tableStream));
      final var tableThrowable = catchThrowable(() -> MoreIterators.toSet(source().read(config, tableCatalog, null)));
      assertThat(tableThrowable).isInstanceOf(ConfigErrorException.class).hasMessageContaining(NULL_CURSOR_EXCEPTION_MESSAGE_CONTAINS);

      final var viewStream = new ConfiguredAirbyteStream()
          .withCursorField(Lists.newArrayList("id"))
          .withDestinationSyncMode(DestinationSyncMode.APPEND)
          .withSyncMode(SyncMode.INCREMENTAL)
          .withStream(CatalogHelpers.createAirbyteStream(
              "null_cursor_view",
              testdb.getDatabaseName(),
              Field.of("id", JsonSchemaType.STRING))
              .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
              .withSourceDefinedPrimaryKey(List.of(List.of("id"))));
      final var viewCatalog = new ConfiguredAirbyteCatalog().withStreams(List.of(viewStream));
      final var viewThrowable = catchThrowable(() -> MoreIterators.toSet(source().read(config, viewCatalog, null)));
      assertThat(viewThrowable).isInstanceOf(ConfigErrorException.class).hasMessageContaining(NULL_CURSOR_EXCEPTION_MESSAGE_CONTAINS);
    }
  }

  static private final String NULL_CURSOR_EXCEPTION_MESSAGE_CONTAINS = "The following tables have invalid columns " +
      "selected as cursor, please select a column with a well-defined ordering with no null values as a cursor.";

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
    try (final var testdb = MySQLTestDatabase.in(BaseImage.MYSQL_8)) {
      final var config = testdb.testConfigBuilder()
          .with(JdbcUtils.JDBC_URL_PARAMS_KEY, "sessionVariables=MAX_EXECUTION_TIME=28800000")
          .withoutSsl()
          .build();
      final AirbyteConnectionStatus check = source().check(config);
      assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, check.getStatus());
    }
  }

  @Test
  public void testPrimaryKeyOrder() {
    final List<PrimaryKeyAttributesFromDb> primaryKeys = new ArrayList<>();
    primaryKeys.add(new PrimaryKeyAttributesFromDb("stream-a", "col1", 3));
    primaryKeys.add(new PrimaryKeyAttributesFromDb("stream-b", "xcol1", 3));
    primaryKeys.add(new PrimaryKeyAttributesFromDb("stream-a", "col2", 2));
    primaryKeys.add(new PrimaryKeyAttributesFromDb("stream-b", "xcol2", 2));
    primaryKeys.add(new PrimaryKeyAttributesFromDb("stream-a", "col3", 1));
    primaryKeys.add(new PrimaryKeyAttributesFromDb("stream-b", "xcol3", 1));

    final Map<String, List<String>> result = AbstractJdbcSource.aggregatePrimateKeys(primaryKeys);
    assertEquals(2, result.size());
    assertTrue(result.containsKey("stream-a"));
    assertEquals(3, result.get("stream-a").size());
    assertEquals(Arrays.asList("col3", "col2", "col1"), result.get("stream-a"));

    assertTrue(result.containsKey("stream-b"));
    assertEquals(3, result.get("stream-b").size());
    assertEquals(Arrays.asList("xcol3", "xcol2", "xcol1"), result.get("stream-b"));
  }

}
