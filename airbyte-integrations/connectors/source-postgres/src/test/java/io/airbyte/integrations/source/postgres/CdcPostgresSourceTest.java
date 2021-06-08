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

package io.airbyte.integrations.source.postgres;

import static java.lang.Thread.sleep;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import com.google.common.collect.Streams;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import io.airbyte.protocol.models.SyncMode;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.lang3.RandomStringUtils;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

class CdcPostgresSourceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(CdcPostgresSourceTest.class);

  private static final String SLOT_NAME_BASE = "debezium_slot";
  private static final String MAKES_SCHEMA = "public";
  private static final String MAKES_STREAM_NAME = "makes";
  private static final String MODELS_SCHEMA = "staging";
  private static final String MODELS_STREAM_NAME = "models";
  private static final Set<String> STREAM_NAMES = Sets.newHashSet(MAKES_STREAM_NAME, MODELS_STREAM_NAME);
  private static final String COL_ID = "id";
  private static final String COL_MAKE = "make";
  private static final String COL_MAKE_ID = "make_id";
  private static final String COL_MODEL = "model";
  private static final String PUBLICATION = "publication";

  private static final AirbyteCatalog CATALOG = new AirbyteCatalog().withStreams(List.of(
      CatalogHelpers.createAirbyteStream(
          MAKES_STREAM_NAME,
          MAKES_SCHEMA,
          Field.of(COL_ID, JsonSchemaPrimitive.NUMBER),
          Field.of(COL_MAKE, JsonSchemaPrimitive.STRING))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
          .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID))),
      CatalogHelpers.createAirbyteStream(
          MODELS_STREAM_NAME,
          MODELS_SCHEMA,
          Field.of(COL_ID, JsonSchemaPrimitive.NUMBER),
          Field.of(COL_MAKE_ID, JsonSchemaPrimitive.NUMBER),
          Field.of(COL_MODEL, JsonSchemaPrimitive.STRING))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
          .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID)))));
  private static final ConfiguredAirbyteCatalog CONFIGURED_CATALOG = CatalogHelpers.toDefaultConfiguredCatalog(CATALOG);

  // set all streams to incremental.
  static {
    CONFIGURED_CATALOG.getStreams().forEach(s -> s.setSyncMode(SyncMode.INCREMENTAL));
  }

  private static final List<JsonNode> MAKE_RECORDS = ImmutableList.of(
      Jsons.jsonNode(ImmutableMap.of(COL_ID, 1, COL_MAKE, "Ford")),
      Jsons.jsonNode(ImmutableMap.of(COL_ID, 2, COL_MAKE, "Mercedes")));

  private static final List<JsonNode> MODEL_RECORDS = ImmutableList.of(
      Jsons.jsonNode(ImmutableMap.of(COL_ID, 11, COL_MAKE_ID, 1, COL_MODEL, "Fiesta")),
      Jsons.jsonNode(ImmutableMap.of(COL_ID, 12, COL_MAKE_ID, 1, COL_MODEL, "Focus")),
      Jsons.jsonNode(ImmutableMap.of(COL_ID, 13, COL_MAKE_ID, 1, COL_MODEL, "Ranger")),
      Jsons.jsonNode(ImmutableMap.of(COL_ID, 14, COL_MAKE_ID, 2, COL_MODEL, "GLA")),
      Jsons.jsonNode(ImmutableMap.of(COL_ID, 15, COL_MAKE_ID, 2, COL_MODEL, "A 220")),
      Jsons.jsonNode(ImmutableMap.of(COL_ID, 16, COL_MAKE_ID, 2, COL_MODEL, "E 350")));

  private static PostgreSQLContainer<?> PSQL_DB;

  private String dbName;
  private Database database;
  private PostgresSource source;

  @BeforeAll
  static void init() {
    PSQL_DB = new PostgreSQLContainer<>("postgres:13-alpine")
        .withCopyFileToContainer(MountableFile.forClasspathResource("postgresql.conf"), "/etc/postgresql/postgresql.conf")
        .withCommand("postgres -c config_file=/etc/postgresql/postgresql.conf");
    PSQL_DB.start();
  }

  @AfterAll
  static void tearDown() {
    PSQL_DB.close();
  }

  @BeforeEach
  void setup() throws Exception {
    source = new PostgresSource();

    dbName = "db_" + RandomStringUtils.randomAlphabetic(10).toLowerCase();

    final String initScriptName = "init_" + dbName.concat(".sql");
    final String tmpFilePath = IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE " + dbName + ";");
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), PSQL_DB);

    final JsonNode config = getConfig(PSQL_DB, dbName);
    final String fullReplicationSlot = SLOT_NAME_BASE + "_" + dbName;
    database = getDatabaseFromConfig(config);
    database.query(ctx -> {
      ctx.execute("SELECT pg_create_logical_replication_slot('" + fullReplicationSlot + "', 'pgoutput');");
      ctx.execute("CREATE PUBLICATION " + PUBLICATION + " FOR ALL TABLES;");
      ctx.execute("CREATE SCHEMA " + MODELS_SCHEMA + ";");
      ctx.execute(String.format("CREATE TABLE %s.%s(%s INTEGER, %s VARCHAR(200), PRIMARY KEY (%s));", MAKES_SCHEMA, MAKES_STREAM_NAME, COL_ID,
          COL_MAKE, COL_ID));
      ctx.execute(String.format("CREATE TABLE %s.%s(%s INTEGER, %s INTEGER, %s VARCHAR(200), PRIMARY KEY (%s));",
          MODELS_SCHEMA, MODELS_STREAM_NAME, COL_ID, COL_MAKE_ID, COL_MODEL, COL_ID));

      for (JsonNode recordJson : MAKE_RECORDS) {
        writeMakeRecord(ctx, recordJson);
      }

      for (JsonNode recordJson : MODEL_RECORDS) {
        writeModelRecord(ctx, recordJson);
      }

      return null;
    });
  }

  private JsonNode getConfig(PostgreSQLContainer<?> psqlDb, String dbName) {
    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("replication_slot", SLOT_NAME_BASE + "_" + dbName)
        .put("publication", PUBLICATION)
        .build());

    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", psqlDb.getHost())
        .put("port", psqlDb.getFirstMappedPort())
        .put("database", dbName)
        .put("username", psqlDb.getUsername())
        .put("password", psqlDb.getPassword())
        .put("ssl", false)
        .put("replication_method", replicationMethod)
        .build());
  }

  private Database getDatabaseFromConfig(JsonNode config) {
    return Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:postgresql://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()),
        "org.postgresql.Driver",
        SQLDialect.POSTGRES);
  }

  @Test
  @DisplayName("On the first sync, produce returns records that exist in the database.")
  void testExistingData() throws Exception {
    final AutoCloseableIterator<AirbyteMessage> read = source.read(getConfig(PSQL_DB, dbName), CONFIGURED_CATALOG, null);
    final List<AirbyteMessage> actualRecords = AutoCloseableIterators.toListAndClose(read);

    final Set<AirbyteRecordMessage> recordMessages = extractRecordMessages(actualRecords);
    final List<AirbyteStateMessage> stateMessages = extractStateMessages(actualRecords);

    assertExpectedRecords(Stream.concat(MAKE_RECORDS.stream(), MODEL_RECORDS.stream()).collect(Collectors.toSet()), recordMessages);
    assertExpectedStateMessages(stateMessages);
  }

  @Test
  @DisplayName("When a record is deleted, produces a deletion record.")
  void testDelete() throws Exception {
    final AutoCloseableIterator<AirbyteMessage> read1 = source.read(getConfig(PSQL_DB, dbName), CONFIGURED_CATALOG, null);
    final List<AirbyteMessage> actualRecords1 = AutoCloseableIterators.toListAndClose(read1);
    final List<AirbyteStateMessage> stateMessages1 = extractStateMessages(actualRecords1);

    assertExpectedStateMessages(stateMessages1);

    database.query(ctx -> {
      ctx.execute(String.format("DELETE FROM %s.%s WHERE %s = %s", MODELS_SCHEMA, MODELS_STREAM_NAME, COL_ID, 11));
      return null;
    });

    final JsonNode state = stateMessages1.get(0).getData();
    final AutoCloseableIterator<AirbyteMessage> read2 = source.read(getConfig(PSQL_DB, dbName), CONFIGURED_CATALOG, state);
    final List<AirbyteMessage> actualRecords2 = AutoCloseableIterators.toListAndClose(read2);
    final List<AirbyteRecordMessage> recordMessages2 = new ArrayList<>(extractRecordMessages(actualRecords2));
    final List<AirbyteStateMessage> stateMessages2 = extractStateMessages(actualRecords2);

    assertExpectedStateMessages(stateMessages2);
    assertEquals(1, recordMessages2.size());
    assertEquals(11, recordMessages2.get(0).getData().get(COL_ID).asInt());
    assertNotNull(recordMessages2.get(0).getData().get(AbstractJdbcSource.CDC_LSN));
    assertNotNull(recordMessages2.get(0).getData().get(AbstractJdbcSource.CDC_UPDATED_AT));
    assertNotNull(recordMessages2.get(0).getData().get(AbstractJdbcSource.CDC_DELETED_AT));
  }

  @Test
  @DisplayName("When a record is updated, produces an update record.")
  void testUpdate() throws Exception {
    final String updatedModel = "Explorer";
    final AutoCloseableIterator<AirbyteMessage> read1 = source.read(getConfig(PSQL_DB, dbName), CONFIGURED_CATALOG, null);
    final List<AirbyteMessage> actualRecords1 = AutoCloseableIterators.toListAndClose(read1);
    final List<AirbyteStateMessage> stateMessages1 = extractStateMessages(actualRecords1);

    assertExpectedStateMessages(stateMessages1);

    database.query(ctx -> {
      ctx.execute(String.format("UPDATE %s.%s SET %s = '%s' WHERE %s = %s", MODELS_SCHEMA, MODELS_STREAM_NAME, COL_MODEL, updatedModel, COL_ID, 11));
      return null;
    });

    final JsonNode state = stateMessages1.get(0).getData();
    final AutoCloseableIterator<AirbyteMessage> read2 = source.read(getConfig(PSQL_DB, dbName), CONFIGURED_CATALOG, state);
    final List<AirbyteMessage> actualRecords2 = AutoCloseableIterators.toListAndClose(read2);
    final List<AirbyteRecordMessage> recordMessages2 = new ArrayList<>(extractRecordMessages(actualRecords2));
    final List<AirbyteStateMessage> stateMessages2 = extractStateMessages(actualRecords2);

    assertExpectedStateMessages(stateMessages2);
    assertEquals(1, recordMessages2.size());
    assertEquals(11, recordMessages2.get(0).getData().get(COL_ID).asInt());
    assertEquals(updatedModel, recordMessages2.get(0).getData().get(COL_MODEL).asText());
    assertNotNull(recordMessages2.get(0).getData().get(AbstractJdbcSource.CDC_LSN));
    assertNotNull(recordMessages2.get(0).getData().get(AbstractJdbcSource.CDC_UPDATED_AT));
    assertTrue(recordMessages2.get(0).getData().get(AbstractJdbcSource.CDC_DELETED_AT).isNull());
  }

  @SuppressWarnings({"BusyWait", "CodeBlock2Expr"})
  @Test
  @DisplayName("Verify that when data is inserted into the database while a sync is happening and after the first sync, it all gets replicated.")
  void testRecordsProducedDuringAndAfterSync() throws Exception {
    final int recordsToCreate = 20;
    final AtomicInteger recordsCreated = new AtomicInteger();
    final ScheduledExecutorService executorService = Executors.newScheduledThreadPool(1);
    executorService.scheduleAtFixedRate(() -> {
      Exceptions.toRuntime(() -> database.query(ctx -> {
        if (recordsCreated.get() < recordsToCreate) {
          final JsonNode record =
              Jsons.jsonNode(ImmutableMap.of(COL_ID, 100 + recordsCreated.get(), COL_MAKE_ID, 1, COL_MODEL, "F-" + recordsCreated.get()));
          writeModelRecord(ctx, record);

          recordsCreated.incrementAndGet();
        }
        return null;
      }));
    }, 0, 500, TimeUnit.MILLISECONDS);

    final AutoCloseableIterator<AirbyteMessage> read1 = source.read(getConfig(PSQL_DB, dbName), CONFIGURED_CATALOG, null);
    final List<AirbyteMessage> actualRecords1 = AutoCloseableIterators.toListAndClose(read1);
    assertExpectedStateMessages(extractStateMessages(actualRecords1));

    while (recordsCreated.get() != recordsToCreate) {
      LOGGER.info("waiting for records to be created.");
      sleep(500);
    }
    executorService.shutdown();

    final JsonNode state = extractStateMessages(actualRecords1).get(0).getData();
    final AutoCloseableIterator<AirbyteMessage> read2 = source.read(getConfig(PSQL_DB, dbName), CONFIGURED_CATALOG, state);
    final List<AirbyteMessage> actualRecords2 = AutoCloseableIterators.toListAndClose(read2);

    assertExpectedStateMessages(extractStateMessages(actualRecords2));

    // sometimes there can be more than one of these at the end of the snapshot and just before the
    // first incremental.
    final Set<AirbyteRecordMessage> recordMessages1 = removeDuplicates(extractRecordMessages(actualRecords1));
    final Set<AirbyteRecordMessage> recordMessages2 = removeDuplicates(extractRecordMessages(actualRecords2));

    final int recordsCreatedBeforeTestCount = MAKE_RECORDS.size() + MODEL_RECORDS.size();
    assertTrue(recordsCreatedBeforeTestCount < recordMessages1.size(), "Expected first sync to include records created while the test was running.");
    assertTrue(0 < recordMessages2.size(), "Expected records to be replicated in the second sync.");
    LOGGER.info("recordsToCreate = " + recordsToCreate);
    LOGGER.info("recordsCreatedBeforeTestCount = " + recordsCreatedBeforeTestCount);
    LOGGER.info("recordMessages1.size() = " + recordMessages1.size());
    LOGGER.info("recordMessages2.size() = " + recordMessages2.size());
    assertEquals(recordsToCreate + recordsCreatedBeforeTestCount, recordMessages1.size() + recordMessages2.size());
  }

  private static Set<AirbyteRecordMessage> removeDuplicates(Set<AirbyteRecordMessage> messages) {
    final Set<JsonNode> existingDataRecordsWithoutUpdated = new HashSet<>();
    final Set<AirbyteRecordMessage> output = new HashSet<>();

    for (AirbyteRecordMessage message : messages) {
      ObjectNode node = message.getData().deepCopy();
      node.remove("_ab_cdc_updated_at");

      if (existingDataRecordsWithoutUpdated.contains(node)) {
        LOGGER.info("Removing duplicate node: " + node);
      } else {
        output.add(message);
        existingDataRecordsWithoutUpdated.add(node);
      }
    }

    return output;
  }

  @Test
  @DisplayName("When both incremental CDC and full refresh are configured for different streams in a sync, the data is replicated as expected.")
  void testCdcAndFullRefreshInSameSync() throws Exception {
    final ConfiguredAirbyteCatalog configuredCatalog = Jsons.clone(CONFIGURED_CATALOG);
    // set make stream to full refresh.
    configuredCatalog.getStreams().get(0).setSyncMode(SyncMode.FULL_REFRESH);

    final AutoCloseableIterator<AirbyteMessage> read1 = source.read(getConfig(PSQL_DB, dbName), configuredCatalog, null);
    final List<AirbyteMessage> actualRecords1 = AutoCloseableIterators.toListAndClose(read1);

    final Set<AirbyteRecordMessage> recordMessages1 = extractRecordMessages(actualRecords1);
    final List<AirbyteStateMessage> stateMessages1 = extractStateMessages(actualRecords1);

    assertExpectedStateMessages(stateMessages1);
    assertExpectedRecords(
        Stream.concat(MAKE_RECORDS.stream(), MODEL_RECORDS.stream()).collect(Collectors.toSet()),
        recordMessages1,
        Collections.singleton(MODELS_STREAM_NAME));

    final JsonNode fiatRecord = Jsons.jsonNode(ImmutableMap.of(COL_ID, 3, COL_MAKE, "Fiat"));
    final JsonNode puntoRecord = Jsons.jsonNode(ImmutableMap.of(COL_ID, 100, COL_MAKE_ID, 3, COL_MODEL, "Punto"));
    database.query(ctx -> {
      writeMakeRecord(ctx, fiatRecord);
      writeModelRecord(ctx, puntoRecord);
      return null;
    });

    final JsonNode state = extractStateMessages(actualRecords1).get(0).getData();
    final AutoCloseableIterator<AirbyteMessage> read2 = source.read(getConfig(PSQL_DB, dbName), configuredCatalog, state);
    final List<AirbyteMessage> actualRecords2 = AutoCloseableIterators.toListAndClose(read2);

    final Set<AirbyteRecordMessage> recordMessages2 = extractRecordMessages(actualRecords2);
    final List<AirbyteStateMessage> stateMessages2 = extractStateMessages(actualRecords2);

    assertExpectedStateMessages(stateMessages2);
    // only make stream should full refresh.
    assertExpectedRecords(
        Streams.concat(MAKE_RECORDS.stream(), Stream.of(fiatRecord, puntoRecord)).collect(Collectors.toSet()),
        recordMessages2,
        Collections.singleton(MODELS_STREAM_NAME));
  }

  @Test
  @DisplayName("When no records exist, no records are returned.")
  void testNoData() throws Exception {
    database.query(ctx -> {
      ctx.execute(String.format("DELETE FROM %s.%s", MAKES_SCHEMA, MAKES_STREAM_NAME));
      return null;
    });

    database.query(ctx -> {
      ctx.execute(String.format("DELETE FROM %s.%s", MODELS_SCHEMA, MODELS_STREAM_NAME));
      return null;
    });

    final AutoCloseableIterator<AirbyteMessage> read = source.read(getConfig(PSQL_DB, dbName), CONFIGURED_CATALOG, null);
    final List<AirbyteMessage> actualRecords = AutoCloseableIterators.toListAndClose(read);

    final Set<AirbyteRecordMessage> recordMessages = extractRecordMessages(actualRecords);
    final List<AirbyteStateMessage> stateMessages = extractStateMessages(actualRecords);

    assertExpectedRecords(Collections.emptySet(), recordMessages);
    assertExpectedStateMessages(stateMessages);
  }

  @Test
  @DisplayName("When no changes have been made to the database since the previous sync, no records are returned.")
  void testNoDataOnSecondSync() throws Exception {
    final AutoCloseableIterator<AirbyteMessage> read1 = source.read(getConfig(PSQL_DB, dbName), CONFIGURED_CATALOG, null);
    final List<AirbyteMessage> actualRecords1 = AutoCloseableIterators.toListAndClose(read1);
    final JsonNode state = extractStateMessages(actualRecords1).get(0).getData();

    final AutoCloseableIterator<AirbyteMessage> read2 = source.read(getConfig(PSQL_DB, dbName), CONFIGURED_CATALOG, state);
    final List<AirbyteMessage> actualRecords2 = AutoCloseableIterators.toListAndClose(read2);

    final Set<AirbyteRecordMessage> recordMessages2 = extractRecordMessages(actualRecords2);
    final List<AirbyteStateMessage> stateMessages2 = extractStateMessages(actualRecords2);

    assertExpectedRecords(Collections.emptySet(), recordMessages2);
    assertExpectedStateMessages(stateMessages2);
  }

  @Test
  void testCheck() {
    final AirbyteConnectionStatus status = source.check(getConfig(PSQL_DB, dbName));
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.SUCCEEDED);
  }

  @Test
  void testCheckWithoutPublication() throws SQLException {
    database.query(ctx -> ctx.execute("DROP PUBLICATION " + PUBLICATION + ";"));
    final AirbyteConnectionStatus status = source.check(getConfig(PSQL_DB, dbName));
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
  }

  @Test
  void testCheckWithoutReplicationSlot() throws SQLException {
    final String fullReplicationSlot = SLOT_NAME_BASE + "_" + dbName;
    database.query(ctx -> ctx.execute("SELECT pg_drop_replication_slot('" + fullReplicationSlot + "');"));

    final AirbyteConnectionStatus status = source.check(getConfig(PSQL_DB, dbName));
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
  }

  @Test
  void testReadWithoutPublication() throws SQLException {
    database.query(ctx -> ctx.execute("DROP PUBLICATION " + PUBLICATION + ";"));

    assertThrows(Exception.class, () -> {
      source.read(getConfig(PSQL_DB, dbName), CONFIGURED_CATALOG, null);
    });
  }

  @Test
  void testReadWithoutReplicationSlot() throws SQLException {
    final String fullReplicationSlot = SLOT_NAME_BASE + "_" + dbName;
    database.query(ctx -> ctx.execute("SELECT pg_drop_replication_slot('" + fullReplicationSlot + "');"));

    assertThrows(Exception.class, () -> {
      source.read(getConfig(PSQL_DB, dbName), CONFIGURED_CATALOG, null);
    });
  }

  @Test
  void testDiscover() throws Exception {
    final AirbyteCatalog expectedCatalog = Jsons.clone(CATALOG);

    // stream with PK
    expectedCatalog.getStreams().get(0).setSourceDefinedCursor(true);
    addCdcMetadataColumns(expectedCatalog.getStreams().get(0));

    // stream with no PK.
    expectedCatalog.getStreams().get(1).setSourceDefinedPrimaryKey(Collections.emptyList());
    expectedCatalog.getStreams().get(1).setSupportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    addCdcMetadataColumns(expectedCatalog.getStreams().get(1));

    database.query(ctx -> ctx.execute(String.format("ALTER TABLE %s.%s DROP CONSTRAINT models_pkey", MODELS_SCHEMA, MODELS_STREAM_NAME)));

    final AirbyteCatalog actualCatalog = source.discover(getConfig(PSQL_DB, dbName));

    assertEquals(
        expectedCatalog.getStreams().stream().sorted(Comparator.comparing(AirbyteStream::getName)).collect(Collectors.toList()),
        actualCatalog.getStreams().stream().sorted(Comparator.comparing(AirbyteStream::getName)).collect(Collectors.toList()));
  }

  private static AirbyteStream addCdcMetadataColumns(AirbyteStream stream) {
    ObjectNode jsonSchema = (ObjectNode) stream.getJsonSchema();
    ObjectNode properties = (ObjectNode) jsonSchema.get("properties");

    final JsonNode numberType = Jsons.jsonNode(ImmutableMap.of("type", "number"));
    properties.set(AbstractJdbcSource.CDC_LSN, numberType);
    properties.set(AbstractJdbcSource.CDC_UPDATED_AT, numberType);
    properties.set(AbstractJdbcSource.CDC_DELETED_AT, numberType);

    return stream;
  }

  private void writeMakeRecord(DSLContext ctx, JsonNode recordJson) {
    ctx.execute(String.format("INSERT INTO %s.%s (%s, %s) VALUES (%s, '%s');", MAKES_SCHEMA, MAKES_STREAM_NAME, COL_ID, COL_MAKE,
        recordJson.get(COL_ID).asInt(), recordJson.get(COL_MAKE).asText()));
  }

  private void writeModelRecord(DSLContext ctx, JsonNode recordJson) {
    ctx.execute(
        String.format("INSERT INTO %s.%s (%s, %s, %s) VALUES (%s, %s, '%s');", MODELS_SCHEMA, MODELS_STREAM_NAME, COL_ID, COL_MAKE_ID, COL_MODEL,
            recordJson.get(COL_ID).asInt(), recordJson.get(COL_MAKE_ID).asInt(), recordJson.get(COL_MODEL).asText()));
  }

  private Set<AirbyteRecordMessage> extractRecordMessages(List<AirbyteMessage> messages) {
    final List<AirbyteRecordMessage> recordMessageList = messages
        .stream()
        .filter(r -> r.getType() == Type.RECORD).map(AirbyteMessage::getRecord)
        .collect(Collectors.toList());
    final Set<AirbyteRecordMessage> recordMessageSet = new HashSet<>(recordMessageList);

    assertEquals(recordMessageList.size(), recordMessageSet.size(), "Expected no duplicates in airbyte record message output for a single sync.");

    return recordMessageSet;
  }

  private List<AirbyteStateMessage> extractStateMessages(List<AirbyteMessage> messages) {
    return messages.stream().filter(r -> r.getType() == Type.STATE).map(AirbyteMessage::getState).collect(Collectors.toList());
  }

  private static void assertExpectedStateMessages(List<AirbyteStateMessage> stateMessages) {
    assertEquals(1, stateMessages.size());
    assertNotNull(stateMessages.get(0).getData());
  }

  private static void assertExpectedRecords(Set<JsonNode> expectedRecords, Set<AirbyteRecordMessage> actualRecords) {
    // assume all streams are cdc.
    assertExpectedRecords(
        expectedRecords,
        actualRecords,
        actualRecords.stream().map(AirbyteRecordMessage::getStream).collect(Collectors.toSet()));
  }

  private static void assertExpectedRecords(Set<JsonNode> expectedRecords, Set<AirbyteRecordMessage> actualRecords, Set<String> cdcStreams) {
    final Set<JsonNode> actualData = actualRecords
        .stream()
        .map(recordMessage -> {
          assertTrue(STREAM_NAMES.contains(recordMessage.getStream()));
          assertNotNull(recordMessage.getEmittedAt());
          if (recordMessage.getStream().equals(MAKES_STREAM_NAME)) {
            assertEquals(MAKES_SCHEMA, recordMessage.getNamespace());
          } else {
            assertEquals(MODELS_SCHEMA, recordMessage.getNamespace());
          }

          final JsonNode data = recordMessage.getData();

          if (cdcStreams.contains(recordMessage.getStream())) {
            assertNotNull(data.get(AbstractJdbcSource.CDC_LSN));
            assertNotNull(data.get(AbstractJdbcSource.CDC_UPDATED_AT));
          } else {
            assertNull(data.get(AbstractJdbcSource.CDC_LSN));
            assertNull(data.get(AbstractJdbcSource.CDC_UPDATED_AT));
            assertNull(data.get(AbstractJdbcSource.CDC_DELETED_AT));
          }

          ((ObjectNode) data).remove(AbstractJdbcSource.CDC_LSN);
          ((ObjectNode) data).remove(AbstractJdbcSource.CDC_UPDATED_AT);
          ((ObjectNode) data).remove(AbstractJdbcSource.CDC_DELETED_AT);

          return data;
        })
        .collect(Collectors.toSet());

    assertEquals(expectedRecords, actualData);
  }

}
