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
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Streams;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import io.airbyte.protocol.models.SyncMode;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.util.Collections;
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
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

class PostgresSourceCdcTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresSourceCdcTest.class);

  private static final String SLOT_NAME = "debezium_slot";
  private static final String MAKES_STREAM_NAME = "public.makes";
  private static final String MODELS_STREAM_NAME = "public.models";
  private static final String COL_ID = "id";
  private static final String COL_MAKE = "make";
  private static final String COL_MAKE_ID = "make_id";
  private static final String COL_MODEL = "model";

  private static final AirbyteCatalog CATALOG = new AirbyteCatalog().withStreams(List.of(
      CatalogHelpers.createAirbyteStream(
          MAKES_STREAM_NAME,
          Field.of(COL_ID, JsonSchemaPrimitive.NUMBER),
          Field.of(COL_MAKE, JsonSchemaPrimitive.STRING))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
          .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID))),
      CatalogHelpers.createAirbyteStream(
          MODELS_STREAM_NAME,
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
    MoreResources.writeResource(initScriptName, "CREATE DATABASE " + dbName + ";");
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forClasspathResource(initScriptName), PSQL_DB);

    final JsonNode config = getConfig(PSQL_DB, dbName);
    database = getDatabaseFromConfig(config);
    database.query(ctx -> {
      // ctx.execute("SELECT pg_create_logical_replication_slot('" + SLOT_NAME + "', 'pgoutput');");

      ctx.fetch(String.format("CREATE TABLE %s(%s INTEGER, %s VARCHAR(200), PRIMARY KEY (%s));", MAKES_STREAM_NAME, COL_ID, COL_MAKE, COL_ID));
      ctx.fetch(String.format("CREATE TABLE %s(%s INTEGER, %s INTEGER, %s VARCHAR(200), PRIMARY KEY (%s));",
          MODELS_STREAM_NAME, COL_ID, COL_MAKE_ID, COL_MODEL, COL_ID));

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
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", psqlDb.getHost())
        .put("port", psqlDb.getFirstMappedPort())
        .put("database", dbName)
        .put("username", psqlDb.getUsername())
        .put("password", psqlDb.getPassword())
        .put("replication_slot", SLOT_NAME)
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
  void testExistingData() throws Exception {
    final AutoCloseableIterator<AirbyteMessage> read = source.read(getConfig(PSQL_DB, dbName), CONFIGURED_CATALOG, null);
    final List<AirbyteMessage> actualRecords = AutoCloseableIterators.toList(read);

    final Set<AirbyteRecordMessage> recordMessages = extractRecordMessages(actualRecords);
    final List<AirbyteStateMessage> stateMessages = extractStateMessages(actualRecords);

    assertExpectedRecords(Stream.concat(MAKE_RECORDS.stream(), MODEL_RECORDS.stream()).collect(Collectors.toSet()), recordMessages);
    assertExpectedStateMessages(stateMessages);
  }

  @Test
  void testDelete() throws Exception {
    final AutoCloseableIterator<AirbyteMessage> read1 = source.read(getConfig(PSQL_DB, dbName), CONFIGURED_CATALOG, null);
    final List<AirbyteMessage> actualRecords1 = AutoCloseableIterators.toList(read1);
    final List<AirbyteStateMessage> stateMessages1 = extractStateMessages(actualRecords1);

    assertExpectedStateMessages(stateMessages1);

    database.query(ctx -> {
      ctx.execute(String.format("DELETE FROM %s WHERE %s = %s", MODELS_STREAM_NAME, COL_ID, 11));
      return null;
    });

    final JsonNode state = stateMessages1.get(0).getData();
    final AutoCloseableIterator<AirbyteMessage> read2 = source.read(getConfig(PSQL_DB, dbName), CONFIGURED_CATALOG, state);
    final List<AirbyteMessage> actualRecords2 = AutoCloseableIterators.toList(read2);
    final List<AirbyteStateMessage> stateMessages2 = extractStateMessages(actualRecords2);

    assertExpectedStateMessages(stateMessages2);
    assertEquals(1, actualRecords2.size());
    assertEquals(11, actualRecords2.get(0).getRecord().getData().get(COL_ID).asInt());
    assertNotNull(actualRecords2.get(0).getRecord().getData().get(PostgresSource.CDC_LSN));
    assertNotNull(actualRecords2.get(0).getRecord().getData().get(PostgresSource.CDC_UPDATED_AT));
    assertNotNull(actualRecords2.get(0).getRecord().getData().get(PostgresSource.CDC_DELETED_AT));
  }

  @Test
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
    final List<AirbyteMessage> actualRecords1 = AutoCloseableIterators.toList(read1);
    assertExpectedStateMessages(extractStateMessages(actualRecords1));

    while (recordsCreated.get() != recordsToCreate) {
      LOGGER.info("waiting for records to be created.");
      sleep(500);
    }
    executorService.shutdown();

    final JsonNode state = extractStateMessages(actualRecords1).get(0).getData();
    final AutoCloseableIterator<AirbyteMessage> read2 = source.read(getConfig(PSQL_DB, dbName), CONFIGURED_CATALOG, state);
    final List<AirbyteMessage> actualRecords2 = AutoCloseableIterators.toList(read2);

    assertExpectedStateMessages(extractStateMessages(actualRecords2));

    final Set<AirbyteRecordMessage> recordMessages1 = extractRecordMessages(actualRecords1);
    final Set<AirbyteRecordMessage> recordMessages2 = extractRecordMessages(actualRecords2);

    final int recordsCreatedBeforeTestCount = MAKE_RECORDS.size() + MODEL_RECORDS.size();
    assertTrue(recordsCreatedBeforeTestCount < recordMessages1.size(), "Expected first sync to include records created while the test was running.");
    assertTrue(0 < recordMessages2.size(), "Expected records to be replicated in the second sync.");
    assertEquals(recordsToCreate + recordsCreatedBeforeTestCount, recordMessages1.size() + recordMessages2.size());
  }

  @Test
  void testCdcAndFullRefreshInSameSync() throws Exception {
    final ConfiguredAirbyteCatalog configuredCatalog = Jsons.clone(CONFIGURED_CATALOG);
    // set make stream to full refresh.
    configuredCatalog.getStreams().get(0).setSyncMode(SyncMode.FULL_REFRESH);

    final AutoCloseableIterator<AirbyteMessage> read1 = source.read(getConfig(PSQL_DB, dbName), configuredCatalog, null);
    final List<AirbyteMessage> actualRecords1 = AutoCloseableIterators.toList(read1);

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
    final List<AirbyteMessage> actualRecords2 = AutoCloseableIterators.toList(read2);

    final Set<AirbyteRecordMessage> recordMessages2 = extractRecordMessages(actualRecords2);
    final List<AirbyteStateMessage> stateMessages2 = extractStateMessages(actualRecords2);

    assertExpectedStateMessages(stateMessages2);
    // only make stream should full refresh.
    assertExpectedRecords(
        Streams.concat(MAKE_RECORDS.stream(), Stream.of(fiatRecord, puntoRecord)).collect(Collectors.toSet()),
        recordMessages2,
        Collections.singleton(MODELS_STREAM_NAME));
  }

  private void writeMakeRecord(DSLContext ctx, JsonNode recordJson) {
    ctx.execute(String.format("INSERT INTO %s (%s, %s) VALUES (%s, '%s');", MAKES_STREAM_NAME, COL_ID, COL_MAKE,
        recordJson.get(COL_ID).asInt(), recordJson.get(COL_MAKE).asText()));
  }

  private void writeModelRecord(DSLContext ctx, JsonNode recordJson) {
    ctx.execute(String.format("INSERT INTO %s (%s, %s, %s) VALUES (%s, %s, '%s');", MODELS_STREAM_NAME, COL_ID, COL_MAKE_ID, COL_MODEL,
        recordJson.get(COL_ID).asInt(), recordJson.get(COL_MAKE_ID).asInt(), recordJson.get(COL_MODEL).asText()));
  }

  private Set<AirbyteRecordMessage> extractRecordMessages(List<AirbyteMessage> messages) {
    final Set<AirbyteRecordMessage> collect = messages
        .stream()
        .filter(r -> r.getType() == Type.RECORD).map(AirbyteMessage::getRecord)
        .collect(Collectors.toSet());

    assertEquals(messages.size(), collect.size(), "Expected no duplicates in airbyte record message output for a single sync.");

    return collect;
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
    assertExpectedRecords(expectedRecords, actualRecords, actualRecords.stream().map(AirbyteRecordMessage::getStream).collect(Collectors.toSet()));
  }

  private static void assertExpectedRecords(Set<JsonNode> expectedRecords, Set<AirbyteRecordMessage> actualRecords, Set<String> cdcStreams) {
    final Set<JsonNode> actualData = actualRecords
        .stream()
        .map(recordMessage -> {
          final JsonNode data = recordMessage.getData();

          if (cdcStreams.contains(recordMessage.getStream())) {
            assertNotNull(data.get(PostgresSource.CDC_LSN));
            assertNotNull(data.get(PostgresSource.CDC_UPDATED_AT));
          } else {
            if (data.get((PostgresSource.CDC_LSN)) != null) {
              System.out.println("data = " + data);
            }
            assertNull(data.get(PostgresSource.CDC_LSN));
            assertNull(data.get(PostgresSource.CDC_UPDATED_AT));
            assertNull(data.get(PostgresSource.CDC_DELETED_AT));
          }

          ((ObjectNode) data).remove(PostgresSource.CDC_LSN);
          ((ObjectNode) data).remove(PostgresSource.CDC_UPDATED_AT);
          ((ObjectNode) data).remove(PostgresSource.CDC_DELETED_AT);

          return data;
        })
        .collect(Collectors.toSet());

    assertEquals(expectedRecords, actualData);
  }

}
