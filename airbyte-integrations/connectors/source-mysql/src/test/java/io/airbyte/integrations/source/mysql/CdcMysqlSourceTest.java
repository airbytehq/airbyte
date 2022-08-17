/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.debezium.CdcSourceTest;
import io.airbyte.integrations.debezium.CdcTargetPosition;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.SyncMode;
import java.sql.SQLException;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import javax.sql.DataSource;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MySQLContainer;

public class CdcMysqlSourceTest extends CdcSourceTest {

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
    database = new Database(DSLContextFactory.create(
        "root",
        "test",
        DRIVER_CLASS,
        String.format("jdbc:mysql://%s:%s",
            container.getHost(),
            container.getFirstMappedPort()),
        SQLDialect.MYSQL));

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

  private void purgeAllBinaryLogs() {
    executeQuery("RESET MASTER;");
  }

  @AfterEach
  public void tearDown() {
    try {
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

    for (JsonNode record : data) {
      executeQuery(String
          .format("INSERT INTO %s.%s (%s, %s, %s, %s) VALUES (%s, %s, %s, %s);", "test_schema",
              "table_with_tiny_int",
              "id", "bool_col", "tiny_int_one_col", "tiny_int_two_col",
              record.get("id").asInt(), record.get("bool_col").asBoolean(),
              record.get("tiny_int_one_col").asBoolean() ? 99 : -99, record.get("tiny_int_two_col").asInt()));
    }

    ((ObjectNode) config).put("database", "test_schema");
  }

  @Override
  protected CdcTargetPosition cdcLatestTargetPosition() {
    DataSource dataSource = DataSourceFactory.create(
        "root",
        "test",
        DRIVER_CLASS,
        String.format("jdbc:mysql://%s:%s",
            container.getHost(),
            container.getFirstMappedPort()),
        Collections.emptyMap());
    JdbcDatabase jdbcDatabase = new DefaultJdbcDatabase(dataSource);

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
        Field.of(COL_ID, JsonSchemaType.INTEGER),
        Field.of(COL_MAKE_ID, JsonSchemaType.INTEGER),
        Field.of(COL_MODEL, JsonSchemaType.STRING));
    streamWithoutPK.setSourceDefinedPrimaryKey(Collections.emptyList());
    streamWithoutPK.setSupportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    addCdcMetadataColumns(streamWithoutPK);

    streams.add(streamWithoutPK);
    expectedCatalog.withStreams(streams);
    return expectedCatalog;
  }

  // TODO : Enable this test once we fix handling of DATETIME values
  @Test
  @Disabled
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

  @Test
  protected void syncShouldHandlePurgedLogsGracefully() throws Exception {

    final int recordsToCreate = 20;
    // first batch of records. 20 created here and 6 created in setup method.
    for (int recordsCreated = 0; recordsCreated < recordsToCreate; recordsCreated++) {
      final JsonNode record =
          Jsons.jsonNode(ImmutableMap
              .of(COL_ID, 100 + recordsCreated, COL_MAKE_ID, 1, COL_MODEL,
                  "F-" + recordsCreated));
      writeModelRecord(record);
    }

    final AutoCloseableIterator<AirbyteMessage> firstBatchIterator = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, null);
    final List<AirbyteMessage> dataFromFirstBatch = AutoCloseableIterators
        .toListAndClose(firstBatchIterator);
    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessages(dataFromFirstBatch);
    assertEquals(1, stateAfterFirstBatch.size());
    assertNotNull(stateAfterFirstBatch.get(0).getData());
    assertExpectedStateMessages(stateAfterFirstBatch);
    final Set<AirbyteRecordMessage> recordsFromFirstBatch = extractRecordMessages(
        dataFromFirstBatch);

    final int recordsCreatedBeforeTestCount = MODEL_RECORDS.size();
    assertEquals((recordsCreatedBeforeTestCount + recordsToCreate), recordsFromFirstBatch.size());
    // sometimes there can be more than one of these at the end of the snapshot and just before the
    // first incremental.
    final Set<AirbyteRecordMessage> recordsFromFirstBatchWithoutDuplicates = removeDuplicates(
        recordsFromFirstBatch);

    assertTrue(recordsCreatedBeforeTestCount < recordsFromFirstBatchWithoutDuplicates.size(),
        "Expected first sync to include records created while the test was running.");

    // second batch of records again 20 being created
    for (int recordsCreated = 0; recordsCreated < recordsToCreate; recordsCreated++) {
      final JsonNode record =
          Jsons.jsonNode(ImmutableMap
              .of(COL_ID, 200 + recordsCreated, COL_MAKE_ID, 1, COL_MODEL,
                  "F-" + recordsCreated));
      writeModelRecord(record);
    }

    purgeAllBinaryLogs();

    final JsonNode state = Jsons.jsonNode(stateAfterFirstBatch);
    final AutoCloseableIterator<AirbyteMessage> secondBatchIterator = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, state);
    final List<AirbyteMessage> dataFromSecondBatch = AutoCloseableIterators
        .toListAndClose(secondBatchIterator);

    final List<AirbyteStateMessage> stateAfterSecondBatch = extractStateMessages(dataFromSecondBatch);
    assertEquals(1, stateAfterSecondBatch.size());
    assertNotNull(stateAfterSecondBatch.get(0).getData());
    assertExpectedStateMessages(stateAfterSecondBatch);

    final Set<AirbyteRecordMessage> recordsFromSecondBatch = extractRecordMessages(
        dataFromSecondBatch);
    assertEquals((recordsToCreate * 2) + recordsCreatedBeforeTestCount, recordsFromSecondBatch.size(),
        "Expected 46 records to be replicated in the second sync.");
  }

}
