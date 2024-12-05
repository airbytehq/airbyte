/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static io.airbyte.integrations.source.snowflake.SnowflakeDataSourceUtils.AIRBYTE_OSS;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableSet;
import com.google.common.collect.Lists;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.source.snowflake.SnowflakeSource;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.SyncMode;
import java.math.BigDecimal;
import java.nio.file.Path;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

class SnowflakeJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest<SnowflakeSource, SnowflakeTestDatabase> {

  private static JsonNode snConfig;

  @BeforeAll
  static void init() {
    snConfig = Jsons
        .deserialize(IOs.readFile(Path.of("secrets/config.json")));
    // due to case sensitiveness in SnowflakeDB
    SCHEMA_NAME = Strings.addRandomSuffix("jdbc_integration_test1", "_", 5).toUpperCase();
    SCHEMA_NAME2 = Strings.addRandomSuffix("jdbc_integration_test1", "_", 5).toUpperCase();
    TEST_SCHEMAS = ImmutableSet.of(SCHEMA_NAME, SCHEMA_NAME2);
    TABLE_NAME = "ID_AND_NAME";
    TABLE_NAME_WITH_SPACES = "ID AND NAME";
    TABLE_NAME_WITHOUT_PK = "ID_AND_NAME_WITHOUT_PK";
    TABLE_NAME_COMPOSITE_PK = "FULL_NAME_COMPOSITE_PK";
    TABLE_NAME_AND_TIMESTAMP = "NAME_AND_TIMESTAMP";
    COL_ID = "ID";
    COL_NAME = "NAME";
    COL_UPDATED_AT = "UPDATED_AT";
    COL_FIRST_NAME = "FIRST_NAME";
    COL_LAST_NAME = "LAST_NAME";
    COL_LAST_NAME_WITH_SPACE = "LAST NAME";
    COL_TIMESTAMP = "TIMESTAMP";
    ID_VALUE_1 = new BigDecimal(1);
    ID_VALUE_2 = new BigDecimal(2);
    ID_VALUE_3 = new BigDecimal(3);
    ID_VALUE_4 = new BigDecimal(4);
    ID_VALUE_5 = new BigDecimal(5);
    CREATE_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "CREATE TABLE %s (%s boolean)";
    INSERT_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "INSERT INTO %s VALUES(true)";
  }

  @Override
  public boolean supportsSchemas() {
    return true;
  }

  @Override
  protected JsonNode config() {
    return Jsons.clone(snConfig);
  }

  @Override
  protected SnowflakeTestDatabase createTestDatabase() {
    final SnowflakeTestDatabase snowflakeTestDatabase = new SnowflakeTestDatabase(source().toDatabaseConfig(Jsons.clone(snConfig)));
    for (final String schemaName : TEST_SCHEMAS) {
      snowflakeTestDatabase.onClose(DROP_SCHEMA_QUERY, schemaName);
    }
    return snowflakeTestDatabase.initialized();
  }

  @Override
  protected SnowflakeSource source() {
    return new SnowflakeSource(AIRBYTE_OSS);
  }

  @Test
  @Override
  protected void testCheckFailure() throws Exception {
    final JsonNode config = config();
    ((ObjectNode) config).with("credentials").put(JdbcUtils.PASSWORD_KEY, "fake");
    try (SnowflakeSource source = source()) {
      final AirbyteConnectionStatus status = source.check(config);
      assertEquals(Status.FAILED, status.getStatus());
      assertTrue(status.getMessage().contains("State code: 08001; Error code: 390100;"));
    }
  }

  @Test
  public void testCheckIncorrectUsernameFailure() throws Exception {
    final JsonNode config = config();
    ((ObjectNode) config).with("credentials").put(JdbcUtils.USERNAME_KEY, "fake");
    try (SnowflakeSource source = source()) {
      final AirbyteConnectionStatus status = source.check(config);
      assertEquals(Status.FAILED, status.getStatus());
      assertTrue(status.getMessage().contains("State code: 08001; Error code: 390100;"));
    }
  }

  @Test
  public void testCheckEmptyUsernameFailure() throws Exception {
    final JsonNode config = config();
    ((ObjectNode) config).with("credentials").put(JdbcUtils.USERNAME_KEY, "");
    try (SnowflakeSource source = source()) {
      final AirbyteConnectionStatus status = source.check(config);
      assertEquals(Status.FAILED, status.getStatus());
      assertTrue(status.getMessage().contains("State code: 28000; Error code: 200011;"));
    }
  }

  @Test
  public void testCheckIncorrectHostFailure() throws Exception {
    final JsonNode config = config();
    ((ObjectNode) config).put(JdbcUtils.HOST_KEY, "localhost2");
    try (SnowflakeSource source = source()) {
      final AirbyteConnectionStatus status = source.check(config);
      assertEquals(Status.FAILED, status.getStatus());
      assertTrue(status.getMessage().contains("Could not connect with provided configuration"));
    }
  }

  @Override
  protected AirbyteCatalog getCatalog(final String defaultNamespace) {
    return new AirbyteCatalog().withStreams(List.of(
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME,
            defaultNamespace,
            Field.of(COL_ID, JsonSchemaType.INTEGER),
            Field.of(COL_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING_DATE))
            .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID))),
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME_WITHOUT_PK,
            defaultNamespace,
            Field.of(COL_ID, JsonSchemaType.INTEGER),
            Field.of(COL_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING_DATE))
            .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(Collections.emptyList()),
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME_COMPOSITE_PK,
            defaultNamespace,
            Field.of(COL_FIRST_NAME, JsonSchemaType.STRING),
            Field.of(COL_LAST_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING_DATE))
            .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(
                List.of(List.of(COL_FIRST_NAME), List.of(COL_LAST_NAME)))));
  }

  @Override
  protected void incrementalDateCheck() throws Exception {
    super.incrementalCursorCheck(COL_UPDATED_AT,
        "2005-10-18",
        "2006-10-19",
        Lists.newArrayList(getTestMessages().get(1),
            getTestMessages().get(2)));
  }

  /* Test that schema config key is making discover pull tables of this schema only */
  @Test
  void testDiscoverSchemaConfig() throws Exception {
    // add table to a separate schema.
    testdb.with(String.format("CREATE TABLE %s(id VARCHAR(200) NOT NULL, name VARCHAR(200) NOT NULL)",
        RelationalDbQueryUtils.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME)))
        .with(String.format("CREATE TABLE %s(id VARCHAR(200) NOT NULL, name VARCHAR(200) NOT NULL)",
            RelationalDbQueryUtils.getFullyQualifiedTableName(SCHEMA_NAME, Strings.addRandomSuffix(TABLE_NAME, "_", 4))));

    final JsonNode config = config();
    JsonNode confWithSchema = ((ObjectNode) config).put("schema", SCHEMA_NAME);
    try (SnowflakeSource source = source()) {
      AirbyteCatalog actual = source.discover(confWithSchema);

      assertFalse(actual.getStreams().isEmpty());

      var streams = actual.getStreams().stream().filter(s -> !s.getNamespace().equals(SCHEMA_NAME)).collect(Collectors.toList());

      assertTrue(streams.isEmpty());

      confWithSchema = ((ObjectNode) config).put("schema", SCHEMA_NAME2);
      actual = source.discover(confWithSchema);
      assertFalse(actual.getStreams().isEmpty());

      streams = actual.getStreams().stream().filter(s -> !s.getNamespace().equals(SCHEMA_NAME2)).collect(Collectors.toList());
      assertTrue(streams.isEmpty());
    }
  }

}
