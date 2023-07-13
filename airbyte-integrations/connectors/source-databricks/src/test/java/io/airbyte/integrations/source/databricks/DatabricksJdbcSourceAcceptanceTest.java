/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.databricks;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.SyncMode;
import java.nio.file.Path;
import java.sql.JDBCType;
import java.util.Collections;
import java.util.List;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class DatabricksJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabricksJdbcSourceAcceptanceTest.class);
  // TODO declare a test container for DB. EX: org.testcontainers.containers.OracleContainer

  @BeforeAll
  static void init() {
    // For JdbcSourceAcceptanceTest.testDiscoverWithNonCursorFields() : Databricks does not have BIT data type hence, using BOOLEAN
    CREATE_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "CREATE TABLE %s (%s BOOLEAN NOT NULL);";
  }

  private JsonNode buildUsernamePasswordConfig(final JsonNode config) {
    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, config.get(JdbcUtils.JDBC_URL_KEY).asText());
    return Jsons.jsonNode(configBuilder.build());
  }
  private static JsonNode getStaticConfig() {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
  }
  @BeforeEach
  public void setup() throws Exception {
    config = buildUsernamePasswordConfig(getStaticConfig());
    super.setup();
  }

  @AfterEach
  public void tearDown() {
    // TODO clean used resources
  }

  @AfterEach
  public void clean() throws Exception {
    super.tearDown();
    DataSourceFactory.close(dataSource);
  }

  @Override
  public AbstractJdbcSource<JDBCType> getSource() {
    return new DatabricksSource();
  }

  @Override
  public boolean supportsSchemas() {
    // TODO check if your db supports it and update method accordingly
    return true;
  }

  @Override
  public JsonNode getConfig() {
    return config;
  }

  @Override
  public String getDriverClass() {
    return DatabricksSource.DRIVER_CLASS;
  }

  @Override
  public AbstractJdbcSource<JDBCType> getJdbcSource() {
    return new DatabricksSource();
  }

  @AfterAll
  static void cleanUp() {
    // TODO close the container. Ex: "container.close();"
  }

  @Test
  void testCheckFailure() throws Exception {
    ((ObjectNode) config).put(JdbcUtils.JDBC_URL_KEY, "fake");
    final AirbyteConnectionStatus status = source.check(config);
    assertEquals(Status.FAILED, status.getStatus());
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
}
