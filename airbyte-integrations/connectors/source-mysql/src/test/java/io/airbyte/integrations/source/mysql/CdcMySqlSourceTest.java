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

package io.airbyte.integrations.source.mysql;

import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_DELETED_AT;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_UPDATED_AT;
import static io.airbyte.integrations.source.mysql.MySqlSource.CDC_LOG_FILE;
import static io.airbyte.integrations.source.mysql.MySqlSource.CDC_LOG_POS;
import static io.airbyte.integrations.source.mysql.MySqlSource.DRIVER_CLASS;
import static io.airbyte.integrations.source.mysql.MySqlSource.MYSQL_CDC_OFFSET;
import static io.airbyte.integrations.source.mysql.MySqlSource.MYSQL_DB_HISTORY;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.debezium.CdcSourceTest;
import io.airbyte.integrations.debezium.CdcTargetPosition;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import io.airbyte.protocol.models.SyncMode;
import java.sql.SQLException;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MySQLContainer;

public class CdcMySqlSourceTest extends CdcSourceTest {

  private static final String DB_NAME = MODELS_SCHEMA;
  private MySQLContainer<?> container;
  private Database database;
  private MySqlSource source;
  private JsonNode config;

  @BeforeEach
  public void setup() throws SQLException {
    init();
    revokeAllPermissions();
    grantCorrectPermissions();
    super.setup();
  }

  private void init() {
    container = new MySQLContainer<>("mysql:8.0");
    container.start();
    source = new MySqlSource();
    database = Databases.createDatabase(
        "root",
        "test",
        String.format("jdbc:mysql://%s:%s",
            container.getHost(),
            container.getFirstMappedPort()),
        DRIVER_CLASS,
        SQLDialect.MYSQL);

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("database", DB_NAME)
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .put("replication_method", "CDC")
        .build());
  }

  private void revokeAllPermissions() {
    executeQuery("REVOKE ALL PRIVILEGES, GRANT OPTION FROM " + container.getUsername() + "@'%';");
  }

  private void grantCorrectPermissions() {
    executeQuery("GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO " + container.getUsername() + "@'%';");
  }

  @AfterEach
  public void tearDown() {
    try {
      database.close();
      container.close();
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  @Test
  public void fullRefreshAndCDCShouldReturnSameRecords() throws Exception {
    JsonNode record1 = Jsons.jsonNode(ImmutableMap.of(
        "id", 1,
        "bool_col", true,
        "tiny_int_one_col", true));
    ((ObjectNode) record1).put("tiny_int_two_col", (short) 80);
    JsonNode record2 = Jsons.jsonNode(ImmutableMap.of(
        "id", 2,
        "bool_col", false,
        "tiny_int_one_col", false));
    ((ObjectNode) record2).put("tiny_int_two_col", (short) 90);
    ImmutableList<JsonNode> records = ImmutableList.of(record1, record2);
    Set<JsonNode> originalData = new HashSet<>(records);
    setupForComparisonBetweenFullRefreshAndCDCSnapshot(records);

    AirbyteCatalog discover = source.discover(config);
    List<AirbyteStream> streams = discover.getStreams();

    assertEquals(streams.size(), 1);
    JsonNode jsonSchema = streams.get(0).getJsonSchema().get("properties");
    assertEquals(jsonSchema.get("id").get("type").asText(), "number");
    assertEquals(jsonSchema.get("bool_col").get("type").asText(), "boolean");
    assertEquals(jsonSchema.get("tiny_int_one_col").get("type").asText(), "boolean");
    assertEquals(jsonSchema.get("tiny_int_two_col").get("type").asText(), "number");

    AirbyteCatalog catalog = new AirbyteCatalog().withStreams(streams);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers
        .toDefaultConfiguredCatalog(catalog);
    configuredCatalog.getStreams().forEach(c -> c.setSyncMode(SyncMode.FULL_REFRESH));

    Set<JsonNode> dataFromFullRefresh = extractRecordMessages(
        AutoCloseableIterators.toListAndClose(source.read(config, configuredCatalog, null)))
            .stream()
            .map(AirbyteRecordMessage::getData).collect(Collectors.toSet());

    configuredCatalog.getStreams().forEach(c -> c.setSyncMode(SyncMode.INCREMENTAL));
    Set<JsonNode> dataFromDebeziumSnapshot =
        extractRecordMessages(AutoCloseableIterators.toListAndClose(source.read(config, configuredCatalog, null)))
            .stream()
            .map(airbyteRecordMessage -> {
              JsonNode data = airbyteRecordMessage.getData();
              removeCDCColumns((ObjectNode) data);
              /**
               * Debezium reads TINYINT (expect for TINYINT(1)) as IntNode while FullRefresh reads it as Short Ref
               * : {@link io.airbyte.db.jdbc.JdbcUtils#setJsonField(java.sql.ResultSet, int, ObjectNode)} -> case
               * TINYINT, SMALLINT -> o.put(columnName, r.getShort(i));
               */
              ((ObjectNode) data)
                  .put("tiny_int_two_col", (short) data.get("tiny_int_two_col").asInt());
              return data;
            })
            .collect(Collectors.toSet());

    assertEquals(dataFromFullRefresh, originalData);
    assertEquals(dataFromFullRefresh, dataFromDebeziumSnapshot);
  }

  private void setupForComparisonBetweenFullRefreshAndCDCSnapshot(ImmutableList<JsonNode> data) {
    executeQuery("CREATE DATABASE " + "test_schema" + ";");
    executeQuery(String.format(
        "CREATE TABLE %s.%s(%s INTEGER, %s Boolean, %s TINYINT(1), %s TINYINT(2), PRIMARY KEY (%s));",
        "test_schema", "table_with_tiny_int", "id", "bool_col", "tiny_int_one_col",
        "tiny_int_two_col", "id"));

    executeQuery(String
        .format("INSERT INTO %s.%s (%s, %s, %s, %s) VALUES (%s, %s, %s, %s);", "test_schema",
            "table_with_tiny_int",
            "id", "bool_col", "tiny_int_one_col", "tiny_int_two_col",
            data.get(0).get("id").asInt(), data.get(0).get("bool_col").asBoolean(),
            data.get(0).get("tiny_int_one_col").asBoolean() ? 99 : -99, data.get(0).get("tiny_int_two_col").asInt()));

    executeQuery(String
        .format("INSERT INTO %s.%s (%s, %s, %s, %s) VALUES (%s, %s, %s, %s);", "test_schema",
            "table_with_tiny_int",
            "id", "bool_col", "tiny_int_one_col", "tiny_int_two_col",
            data.get(1).get("id").asInt(), data.get(1).get("bool_col").asBoolean(),
            data.get(1).get("tiny_int_one_col").asBoolean() ? 99 : -99, data.get(1).get("tiny_int_two_col").asInt()));
    ((ObjectNode) config).put("database", "test_schema");
  }

  @Test
  public void dateTimeDataTypeTest() throws Exception {
    JsonNode record1 = Jsons.jsonNode(ImmutableMap.of(
        "id", 1,
        "datetime_col", "\'2013-09-05T10:10:02\'"));
    JsonNode record2 = Jsons.jsonNode(ImmutableMap.of(
        "id", 2,
        "datetime_col", "\'2013-09-06T10:10:02\'"));
    ImmutableList<JsonNode> records = ImmutableList.of(record1, record2);
    setupForDateTimeDataTypeTest(records);
    Set<JsonNode> originalData = records.stream().peek(c -> {
      String dateTimeValue = c.get("datetime_col").asText();
      ((ObjectNode) c).put("datetime_col", dateTimeValue.substring(1, dateTimeValue.length() - 1));
    }).collect(Collectors.toSet());

    AirbyteCatalog discover = source.discover(config);
    List<AirbyteStream> streams = discover.getStreams();

    assertEquals(streams.size(), 1);
    JsonNode jsonSchema = streams.get(0).getJsonSchema().get("properties");
    assertEquals(jsonSchema.get("id").get("type").asText(), "number");
    assertEquals(jsonSchema.get("datetime_col").get("type").asText(), "string");

    AirbyteCatalog catalog = new AirbyteCatalog().withStreams(streams);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);

    configuredCatalog.getStreams().forEach(c -> c.setSyncMode(SyncMode.INCREMENTAL));
    Set<JsonNode> dataFromDebeziumSnapshot =
        extractRecordMessages(AutoCloseableIterators.toListAndClose(source.read(config, configuredCatalog, null)))
            .stream()
            .map(airbyteRecordMessage -> {
              JsonNode data = airbyteRecordMessage.getData();
              removeCDCColumns((ObjectNode) data);
              return data;
            })
            .collect(Collectors.toSet());

    assertEquals(originalData, dataFromDebeziumSnapshot);

    // TODO: Fix full refresh (non-cdc) mode. The value of the datetime_col is adjusted by the TIMEZONE
    // the code is running in,
    // in my case it got adjusted to IST i.e. "2013-09-05T15:40:02Z" and "2013-09-06T15:40:02Z".
    // configuredCatalog.getStreams().forEach(c -> c.setSyncMode(SyncMode.FULL_REFRESH));
    // Set<JsonNode> dataFromFullRefresh = extractRecordMessages(
    // AutoCloseableIterators.toListAndClose(source.read(config, configuredCatalog, null)))
    // .stream()
    // .map(AirbyteRecordMessage::getData).collect(Collectors.toSet());
    // assertEquals(dataFromFullRefresh, originalData);
  }

  private void setupForDateTimeDataTypeTest(ImmutableList<JsonNode> data) {
    executeQuery("CREATE DATABASE " + "test_schema" + ";");
    executeQuery(String.format(
        "CREATE TABLE %s.%s(%s INTEGER, %s DATETIME, PRIMARY KEY (%s));",
        "test_schema", "table_with_date_time", "id", "datetime_col", "id"));

    executeQuery(String
        .format("INSERT INTO %s.%s (%s, %s) VALUES (%s, %s);", "test_schema",
            "table_with_date_time",
            "id", "datetime_col",
            data.get(0).get("id").asInt(), data.get(0).get("datetime_col").asText()));

    executeQuery(String
        .format("INSERT INTO %s.%s (%s, %s) VALUES (%s, %s);", "test_schema",
            "table_with_date_time",
            "id", "datetime_col",
            data.get(1).get("id").asInt(), data.get(1).get("datetime_col").asText()));
    ((ObjectNode) config).put("database", "test_schema");
  }

  @Override
  protected CdcTargetPosition cdcLatestTargetPosition() {
    JdbcDatabase jdbcDatabase = Databases.createJdbcDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:mysql://%s:%s",
            config.get("host").asText(),
            config.get("port").asInt()),
        DRIVER_CLASS);

    return MySqlCdcTargetPosition.targetPosition(jdbcDatabase);
  }

  @Override
  protected CdcTargetPosition extractPosition(JsonNode record) {
    return new MySqlCdcTargetPosition(record.get(CDC_LOG_FILE).asText(), record.get(CDC_LOG_POS).asInt());
  }

  @Override
  protected void assertNullCdcMetaData(JsonNode data) {
    assertNull(data.get(CDC_LOG_FILE));
    assertNull(data.get(CDC_LOG_POS));
    assertNull(data.get(CDC_UPDATED_AT));
    assertNull(data.get(CDC_DELETED_AT));
  }

  @Override
  protected void assertCdcMetaData(JsonNode data, boolean deletedAtNull) {
    assertNotNull(data.get(CDC_LOG_FILE));
    assertNotNull(data.get(CDC_LOG_POS));
    assertNotNull(data.get(CDC_UPDATED_AT));
    if (deletedAtNull) {
      assertTrue(data.get(CDC_DELETED_AT).isNull());
    } else {
      assertFalse(data.get(CDC_DELETED_AT).isNull());
    }
  }

  @Override
  protected void removeCDCColumns(ObjectNode data) {
    data.remove(CDC_LOG_FILE);
    data.remove(CDC_LOG_POS);
    data.remove(CDC_UPDATED_AT);
    data.remove(CDC_DELETED_AT);
  }

  @Override
  protected void addCdcMetadataColumns(AirbyteStream stream) {
    ObjectNode jsonSchema = (ObjectNode) stream.getJsonSchema();
    ObjectNode properties = (ObjectNode) jsonSchema.get("properties");

    final JsonNode numberType = Jsons.jsonNode(ImmutableMap.of("type", "number"));

    final JsonNode stringType = Jsons.jsonNode(ImmutableMap.of("type", "string"));
    properties.set(CDC_LOG_FILE, stringType);
    properties.set(CDC_LOG_POS, numberType);
    properties.set(CDC_UPDATED_AT, stringType);
    properties.set(CDC_DELETED_AT, stringType);
  }

  @Override
  protected Source getSource() {
    return source;
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected Database getDatabase() {
    return database;
  }

  @Override
  public void assertExpectedStateMessages(List<AirbyteStateMessage> stateMessages) {
    for (AirbyteStateMessage stateMessage : stateMessages) {
      assertNotNull(stateMessage.getData().get("cdc_state").get("state").get(MYSQL_CDC_OFFSET));
      assertNotNull(stateMessage.getData().get("cdc_state").get("state").get(MYSQL_DB_HISTORY));
    }
  }

  @Override
  protected AirbyteCatalog expectedCatalogForDiscover() {
    final AirbyteCatalog expectedCatalog = Jsons.clone(CATALOG);

    createTable(MODELS_SCHEMA, MODELS_STREAM_NAME + "_2",
        columnClause(ImmutableMap.of(COL_ID, "INTEGER", COL_MAKE_ID, "INTEGER", COL_MODEL, "VARCHAR(200)"), Optional.empty()));

    List<AirbyteStream> streams = expectedCatalog.getStreams();
    // stream with PK
    streams.get(0).setSourceDefinedCursor(true);
    addCdcMetadataColumns(streams.get(0));

    AirbyteStream streamWithoutPK = CatalogHelpers.createAirbyteStream(
        MODELS_STREAM_NAME + "_2",
        MODELS_SCHEMA,
        Field.of(COL_ID, JsonSchemaPrimitive.NUMBER),
        Field.of(COL_MAKE_ID, JsonSchemaPrimitive.NUMBER),
        Field.of(COL_MODEL, JsonSchemaPrimitive.STRING));
    streamWithoutPK.setSourceDefinedPrimaryKey(Collections.emptyList());
    streamWithoutPK.setSupportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    addCdcMetadataColumns(streamWithoutPK);

    streams.add(streamWithoutPK);
    expectedCatalog.withStreams(streams);
    return expectedCatalog;
  }

}
