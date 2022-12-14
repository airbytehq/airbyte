/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import com.google.common.collect.Streams;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.Database;
import io.airbyte.integrations.base.Source;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.AirbyteStreamState;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.StreamDescriptor;
import io.airbyte.protocol.models.SyncMode;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class CdcSourceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(CdcSourceTest.class);

  protected static final String MODELS_SCHEMA = "models_schema";
  protected static final String MODELS_STREAM_NAME = "models";
  private static final Set<String> STREAM_NAMES = Sets
      .newHashSet(MODELS_STREAM_NAME);
  protected static final String COL_ID = "id";
  protected static final String COL_MAKE_ID = "make_id";
  protected static final String COL_MODEL = "model";
  protected static final int INITIAL_WAITING_SECONDS = 5;

  protected final List<JsonNode> MODEL_RECORDS_RANDOM = ImmutableList.of(
      Jsons
          .jsonNode(ImmutableMap
              .of(COL_ID + "_random", 11000, COL_MAKE_ID + "_random", 1, COL_MODEL + "_random",
                  "Fiesta-random")),
      Jsons.jsonNode(ImmutableMap
          .of(COL_ID + "_random", 12000, COL_MAKE_ID + "_random", 1, COL_MODEL + "_random",
              "Focus-random")),
      Jsons
          .jsonNode(ImmutableMap
              .of(COL_ID + "_random", 13000, COL_MAKE_ID + "_random", 1, COL_MODEL + "_random",
                  "Ranger-random")),
      Jsons.jsonNode(ImmutableMap
          .of(COL_ID + "_random", 14000, COL_MAKE_ID + "_random", 2, COL_MODEL + "_random",
              "GLA-random")),
      Jsons.jsonNode(ImmutableMap
          .of(COL_ID + "_random", 15000, COL_MAKE_ID + "_random", 2, COL_MODEL + "_random",
              "A 220-random")),
      Jsons
          .jsonNode(ImmutableMap
              .of(COL_ID + "_random", 16000, COL_MAKE_ID + "_random", 2, COL_MODEL + "_random",
                  "E 350-random")));

  protected static final AirbyteCatalog CATALOG = new AirbyteCatalog().withStreams(List.of(
      CatalogHelpers.createAirbyteStream(
          MODELS_STREAM_NAME,
          MODELS_SCHEMA,
          Field.of(COL_ID, JsonSchemaType.INTEGER),
          Field.of(COL_MAKE_ID, JsonSchemaType.INTEGER),
          Field.of(COL_MODEL, JsonSchemaType.STRING))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
          .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID)))));
  protected static final ConfiguredAirbyteCatalog CONFIGURED_CATALOG = CatalogHelpers
      .toDefaultConfiguredCatalog(CATALOG);

  // set all streams to incremental.
  static {
    CONFIGURED_CATALOG.getStreams().forEach(s -> s.setSyncMode(SyncMode.INCREMENTAL));
  }

  protected static final List<JsonNode> MODEL_RECORDS = ImmutableList.of(
      Jsons.jsonNode(ImmutableMap.of(COL_ID, 11, COL_MAKE_ID, 1, COL_MODEL, "Fiesta")),
      Jsons.jsonNode(ImmutableMap.of(COL_ID, 12, COL_MAKE_ID, 1, COL_MODEL, "Focus")),
      Jsons.jsonNode(ImmutableMap.of(COL_ID, 13, COL_MAKE_ID, 1, COL_MODEL, "Ranger")),
      Jsons.jsonNode(ImmutableMap.of(COL_ID, 14, COL_MAKE_ID, 2, COL_MODEL, "GLA")),
      Jsons.jsonNode(ImmutableMap.of(COL_ID, 15, COL_MAKE_ID, 2, COL_MODEL, "A 220")),
      Jsons.jsonNode(ImmutableMap.of(COL_ID, 16, COL_MAKE_ID, 2, COL_MODEL, "E 350")));

  protected void setup() throws SQLException {
    createAndPopulateTables();
  }

  private void createAndPopulateTables() {
    createAndPopulateActualTable();
    createAndPopulateRandomTable();
  }

  protected void executeQuery(final String query) {
    try {
      getDatabase().query(
          ctx -> ctx
              .execute(query));
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  public String columnClause(final Map<String, String> columnsWithDataType, final Optional<String> primaryKey) {
    final StringBuilder columnClause = new StringBuilder();
    int i = 0;
    for (final Map.Entry<String, String> column : columnsWithDataType.entrySet()) {
      columnClause.append(column.getKey());
      columnClause.append(" ");
      columnClause.append(column.getValue());
      if (i < (columnsWithDataType.size() - 1)) {
        columnClause.append(",");
        columnClause.append(" ");
      }
      i++;
    }
    primaryKey.ifPresent(s -> columnClause.append(", PRIMARY KEY (").append(s).append(")"));

    return columnClause.toString();
  }

  public void createTable(final String schemaName, final String tableName, final String columnClause) {
    executeQuery(createTableQuery(schemaName, tableName, columnClause));
  }

  public String createTableQuery(final String schemaName, final String tableName, final String columnClause) {
    return String.format("CREATE TABLE %s.%s(%s);", schemaName, tableName, columnClause);
  }

  public void createSchema(final String schemaName) {
    executeQuery(createSchemaQuery(schemaName));
  }

  public String createSchemaQuery(final String schemaName) {
    return "CREATE DATABASE " + schemaName + ";";
  }

  private void createAndPopulateActualTable() {
    createSchema(MODELS_SCHEMA);
    createTable(MODELS_SCHEMA, MODELS_STREAM_NAME,
        columnClause(ImmutableMap.of(COL_ID, "INTEGER", COL_MAKE_ID, "INTEGER", COL_MODEL, "VARCHAR(200)"), Optional.of(COL_ID)));
    for (final JsonNode recordJson : MODEL_RECORDS) {
      writeModelRecord(recordJson);
    }
  }

  /**
   * This database and table is not part of Airbyte sync. It is being created just to make sure the
   * databases not being synced by Airbyte are not causing issues with our debezium logic
   */
  private void createAndPopulateRandomTable() {
    if (!randomTableSchema().equals(MODELS_SCHEMA)) {
      createSchema(randomTableSchema());
    }
    createTable(randomTableSchema(), MODELS_STREAM_NAME + "_random",
        columnClause(ImmutableMap.of(COL_ID + "_random", "INTEGER", COL_MAKE_ID + "_random", "INTEGER", COL_MODEL + "_random", "VARCHAR(200)"),
            Optional.of(COL_ID + "_random")));
    for (final JsonNode recordJson : MODEL_RECORDS_RANDOM) {
      writeRecords(recordJson, randomTableSchema(), MODELS_STREAM_NAME + "_random",
          COL_ID + "_random", COL_MAKE_ID + "_random", COL_MODEL + "_random");
    }
  }

  protected void writeModelRecord(final JsonNode recordJson) {
    writeRecords(recordJson, MODELS_SCHEMA, MODELS_STREAM_NAME, COL_ID, COL_MAKE_ID, COL_MODEL);
  }

  protected void writeRecords(
                              final JsonNode recordJson,
                              final String dbName,
                              final String streamName,
                              final String idCol,
                              final String makeIdCol,
                              final String modelCol) {
    executeQuery(
        String.format("INSERT INTO %s.%s (%s, %s, %s) VALUES (%s, %s, '%s');", dbName, streamName,
            idCol, makeIdCol, modelCol,
            recordJson.get(idCol).asInt(), recordJson.get(makeIdCol).asInt(),
            recordJson.get(modelCol).asText()));
  }

  protected static Set<AirbyteRecordMessage> removeDuplicates(final Set<AirbyteRecordMessage> messages) {
    final Set<JsonNode> existingDataRecordsWithoutUpdated = new HashSet<>();
    final Set<AirbyteRecordMessage> output = new HashSet<>();

    for (final AirbyteRecordMessage message : messages) {
      final ObjectNode node = message.getData().deepCopy();
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

  protected Set<AirbyteRecordMessage> extractRecordMessages(final List<AirbyteMessage> messages) {
    final Map<String, Set<AirbyteRecordMessage>> recordsPerStream = extractRecordMessagesStreamWise(messages);
    final Set<AirbyteRecordMessage> consolidatedRecords = new HashSet<>();
    recordsPerStream.values().forEach(consolidatedRecords::addAll);
    return consolidatedRecords;
  }

  protected Map<String, Set<AirbyteRecordMessage>> extractRecordMessagesStreamWise(final List<AirbyteMessage> messages) {
    final Map<String, List<AirbyteRecordMessage>> recordsPerStream = new HashMap<>();
    for (final AirbyteMessage message : messages) {
      if (message.getType() == Type.RECORD) {
        AirbyteRecordMessage recordMessage = message.getRecord();
        recordsPerStream.computeIfAbsent(recordMessage.getStream(), (c) -> new ArrayList<>()).add(recordMessage);
      }
    }

    final Map<String, Set<AirbyteRecordMessage>> recordsPerStreamWithNoDuplicates = new HashMap<>();
    for (final Map.Entry<String, List<AirbyteRecordMessage>> element : recordsPerStream.entrySet()) {
      final String streamName = element.getKey();
      final List<AirbyteRecordMessage> records = element.getValue();
      final Set<AirbyteRecordMessage> recordMessageSet = new HashSet<>(records);
      assertEquals(records.size(), recordMessageSet.size(),
          "Expected no duplicates in airbyte record message output for a single sync.");
      recordsPerStreamWithNoDuplicates.put(streamName, recordMessageSet);
    }

    return recordsPerStreamWithNoDuplicates;
  }

  protected List<AirbyteStateMessage> extractStateMessages(final List<AirbyteMessage> messages) {
    return messages.stream().filter(r -> r.getType() == Type.STATE).map(AirbyteMessage::getState)
        .collect(Collectors.toList());
  }

  protected void assertExpectedRecords(final Set<JsonNode> expectedRecords, final Set<AirbyteRecordMessage> actualRecords) {
    // assume all streams are cdc.
    assertExpectedRecords(expectedRecords, actualRecords, actualRecords.stream().map(AirbyteRecordMessage::getStream).collect(Collectors.toSet()));
  }

  private void assertExpectedRecords(final Set<JsonNode> expectedRecords,
                                     final Set<AirbyteRecordMessage> actualRecords,
                                     final Set<String> cdcStreams) {
    assertExpectedRecords(expectedRecords, actualRecords, cdcStreams, STREAM_NAMES, MODELS_SCHEMA);
  }

  protected void assertExpectedRecords(final Set<JsonNode> expectedRecords,
                                       final Set<AirbyteRecordMessage> actualRecords,
                                       final Set<String> cdcStreams,
                                       final Set<String> streamNames,
                                       final String namespace) {
    final Set<JsonNode> actualData = actualRecords
        .stream()
        .map(recordMessage -> {
          assertTrue(streamNames.contains(recordMessage.getStream()));
          assertNotNull(recordMessage.getEmittedAt());

          assertEquals(namespace, recordMessage.getNamespace());

          final JsonNode data = recordMessage.getData();

          if (cdcStreams.contains(recordMessage.getStream())) {
            assertCdcMetaData(data, true);
          } else {
            assertNullCdcMetaData(data);
          }

          removeCDCColumns((ObjectNode) data);

          return data;
        })
        .collect(Collectors.toSet());

    assertEquals(expectedRecords, actualData);
  }

  @Test
  @DisplayName("On the first sync, produce returns records that exist in the database.")
  void testExistingData() throws Exception {
    final CdcTargetPosition targetPosition = cdcLatestTargetPosition();
    final AutoCloseableIterator<AirbyteMessage> read = getSource().read(getConfig(), CONFIGURED_CATALOG, null);
    final List<AirbyteMessage> actualRecords = AutoCloseableIterators.toListAndClose(read);

    final Set<AirbyteRecordMessage> recordMessages = extractRecordMessages(actualRecords);
    final List<AirbyteStateMessage> stateMessages = extractStateMessages(actualRecords);

    assertNotNull(targetPosition);
    recordMessages.forEach(record -> {
      assertEquals(extractPosition(record.getData()), targetPosition);
    });

    assertExpectedRecords(new HashSet<>(MODEL_RECORDS), recordMessages);
    assertEquals(1, stateMessages.size());
    assertNotNull(stateMessages.get(0).getData());
    assertExpectedStateMessages(stateMessages);
  }

  @Test
  @DisplayName("When a record is deleted, produces a deletion record.")
  void testDelete() throws Exception {
    final AutoCloseableIterator<AirbyteMessage> read1 = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, null);
    final List<AirbyteMessage> actualRecords1 = AutoCloseableIterators.toListAndClose(read1);
    final List<AirbyteStateMessage> stateMessages1 = extractStateMessages(actualRecords1);
    assertEquals(1, stateMessages1.size());
    assertNotNull(stateMessages1.get(0).getData());
    assertExpectedStateMessages(stateMessages1);

    executeQuery(String
        .format("DELETE FROM %s.%s WHERE %s = %s", MODELS_SCHEMA, MODELS_STREAM_NAME, COL_ID,
            11));

    final JsonNode state = Jsons.jsonNode(stateMessages1);
    final AutoCloseableIterator<AirbyteMessage> read2 = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, state);
    final List<AirbyteMessage> actualRecords2 = AutoCloseableIterators.toListAndClose(read2);
    final List<AirbyteRecordMessage> recordMessages2 = new ArrayList<>(
        extractRecordMessages(actualRecords2));
    final List<AirbyteStateMessage> stateMessages2 = extractStateMessages(actualRecords2);
    assertEquals(1, stateMessages2.size());
    assertNotNull(stateMessages2.get(0).getData());
    assertExpectedStateMessages(stateMessages2);
    assertEquals(1, recordMessages2.size());
    assertEquals(11, recordMessages2.get(0).getData().get(COL_ID).asInt());
    assertCdcMetaData(recordMessages2.get(0).getData(), false);
  }

  @Test
  @DisplayName("When a record is updated, produces an update record.")
  void testUpdate() throws Exception {
    final String updatedModel = "Explorer";
    final AutoCloseableIterator<AirbyteMessage> read1 = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, null);
    final List<AirbyteMessage> actualRecords1 = AutoCloseableIterators.toListAndClose(read1);
    final List<AirbyteStateMessage> stateMessages1 = extractStateMessages(actualRecords1);
    assertEquals(1, stateMessages1.size());
    assertNotNull(stateMessages1.get(0).getData());
    assertExpectedStateMessages(stateMessages1);

    executeQuery(String
        .format("UPDATE %s.%s SET %s = '%s' WHERE %s = %s", MODELS_SCHEMA, MODELS_STREAM_NAME,
            COL_MODEL, updatedModel, COL_ID, 11));

    final JsonNode state = Jsons.jsonNode(stateMessages1);
    final AutoCloseableIterator<AirbyteMessage> read2 = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, state);
    final List<AirbyteMessage> actualRecords2 = AutoCloseableIterators.toListAndClose(read2);
    final List<AirbyteRecordMessage> recordMessages2 = new ArrayList<>(
        extractRecordMessages(actualRecords2));
    final List<AirbyteStateMessage> stateMessages2 = extractStateMessages(actualRecords2);
    assertEquals(1, stateMessages2.size());
    assertNotNull(stateMessages2.get(0).getData());
    assertExpectedStateMessages(stateMessages2);
    assertEquals(1, recordMessages2.size());
    assertEquals(11, recordMessages2.get(0).getData().get(COL_ID).asInt());
    assertEquals(updatedModel, recordMessages2.get(0).getData().get(COL_MODEL).asText());
    assertCdcMetaData(recordMessages2.get(0).getData(), true);
  }

  @SuppressWarnings({"BusyWait", "CodeBlock2Expr"})
  @Test
  @DisplayName("Verify that when data is inserted into the database while a sync is happening and after the first sync, it all gets replicated.")
  protected void testRecordsProducedDuringAndAfterSync() throws Exception {

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
    assertEquals((MODEL_RECORDS.size() + recordsToCreate), recordsFromFirstBatch.size());

    // second batch of records again 20 being created
    for (int recordsCreated = 0; recordsCreated < recordsToCreate; recordsCreated++) {
      final JsonNode record =
          Jsons.jsonNode(ImmutableMap
              .of(COL_ID, 200 + recordsCreated, COL_MAKE_ID, 1, COL_MODEL,
                  "F-" + recordsCreated));
      writeModelRecord(record);
    }

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
    assertEquals(recordsToCreate, recordsFromSecondBatch.size(),
        "Expected 20 records to be replicated in the second sync.");

    // sometimes there can be more than one of these at the end of the snapshot and just before the
    // first incremental.
    final Set<AirbyteRecordMessage> recordsFromFirstBatchWithoutDuplicates = removeDuplicates(
        recordsFromFirstBatch);
    final Set<AirbyteRecordMessage> recordsFromSecondBatchWithoutDuplicates = removeDuplicates(
        recordsFromSecondBatch);

    final int recordsCreatedBeforeTestCount = MODEL_RECORDS.size();
    assertTrue(recordsCreatedBeforeTestCount < recordsFromFirstBatchWithoutDuplicates.size(),
        "Expected first sync to include records created while the test was running.");
    assertEquals((recordsToCreate * 2) + recordsCreatedBeforeTestCount,
        recordsFromFirstBatchWithoutDuplicates.size() + recordsFromSecondBatchWithoutDuplicates
            .size());
  }

  @Test
  @DisplayName("When both incremental CDC and full refresh are configured for different streams in a sync, the data is replicated as expected.")
  void testCdcAndFullRefreshInSameSync() throws Exception {
    final ConfiguredAirbyteCatalog configuredCatalog = Jsons.clone(CONFIGURED_CATALOG);

    final List<JsonNode> MODEL_RECORDS_2 = ImmutableList.of(
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 110, COL_MAKE_ID, 1, COL_MODEL, "Fiesta-2")),
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 120, COL_MAKE_ID, 1, COL_MODEL, "Focus-2")),
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 130, COL_MAKE_ID, 1, COL_MODEL, "Ranger-2")),
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 140, COL_MAKE_ID, 2, COL_MODEL, "GLA-2")),
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 150, COL_MAKE_ID, 2, COL_MODEL, "A 220-2")),
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 160, COL_MAKE_ID, 2, COL_MODEL, "E 350-2")));

    createTable(MODELS_SCHEMA, MODELS_STREAM_NAME + "_2",
        columnClause(ImmutableMap.of(COL_ID, "INTEGER", COL_MAKE_ID, "INTEGER", COL_MODEL, "VARCHAR(200)"), Optional.of(COL_ID)));

    for (final JsonNode recordJson : MODEL_RECORDS_2) {
      writeRecords(recordJson, MODELS_SCHEMA, MODELS_STREAM_NAME + "_2", COL_ID,
          COL_MAKE_ID, COL_MODEL);
    }

    final ConfiguredAirbyteStream airbyteStream = new ConfiguredAirbyteStream()
        .withStream(CatalogHelpers.createAirbyteStream(
            MODELS_STREAM_NAME + "_2",
            MODELS_SCHEMA,
            Field.of(COL_ID, JsonSchemaType.INTEGER),
            Field.of(COL_MAKE_ID, JsonSchemaType.INTEGER),
            Field.of(COL_MODEL, JsonSchemaType.STRING))
            .withSupportedSyncModes(
                Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID))));
    airbyteStream.setSyncMode(SyncMode.FULL_REFRESH);

    final List<ConfiguredAirbyteStream> streams = configuredCatalog.getStreams();
    streams.add(airbyteStream);
    configuredCatalog.withStreams(streams);

    final AutoCloseableIterator<AirbyteMessage> read1 = getSource()
        .read(getConfig(), configuredCatalog, null);
    final List<AirbyteMessage> actualRecords1 = AutoCloseableIterators.toListAndClose(read1);

    final Set<AirbyteRecordMessage> recordMessages1 = extractRecordMessages(actualRecords1);
    final List<AirbyteStateMessage> stateMessages1 = extractStateMessages(actualRecords1);
    final HashSet<String> names = new HashSet<>(STREAM_NAMES);
    names.add(MODELS_STREAM_NAME + "_2");
    assertEquals(1, stateMessages1.size());
    assertNotNull(stateMessages1.get(0).getData());
    assertExpectedStateMessages(stateMessages1);
    assertExpectedRecords(Streams.concat(MODEL_RECORDS_2.stream(), MODEL_RECORDS.stream())
        .collect(Collectors.toSet()),
        recordMessages1,
        Collections.singleton(MODELS_STREAM_NAME),
        names,
        MODELS_SCHEMA);

    final JsonNode puntoRecord = Jsons
        .jsonNode(ImmutableMap.of(COL_ID, 100, COL_MAKE_ID, 3, COL_MODEL, "Punto"));
    writeModelRecord(puntoRecord);

    final JsonNode state = Jsons.jsonNode(extractStateMessages(actualRecords1));
    final AutoCloseableIterator<AirbyteMessage> read2 = getSource()
        .read(getConfig(), configuredCatalog, state);
    final List<AirbyteMessage> actualRecords2 = AutoCloseableIterators.toListAndClose(read2);

    final Set<AirbyteRecordMessage> recordMessages2 = extractRecordMessages(actualRecords2);
    final List<AirbyteStateMessage> stateMessages2 = extractStateMessages(actualRecords2);
    assertEquals(1, stateMessages2.size());
    assertNotNull(stateMessages2.get(0).getData());
    assertExpectedStateMessages(stateMessages2);
    assertExpectedRecords(
        Streams.concat(MODEL_RECORDS_2.stream(), Stream.of(puntoRecord))
            .collect(Collectors.toSet()),
        recordMessages2,
        Collections.singleton(MODELS_STREAM_NAME),
        names,
        MODELS_SCHEMA);
  }

  @Test
  @DisplayName("When no records exist, no records are returned.")
  void testNoData() throws Exception {

    executeQuery(String.format("DELETE FROM %s.%s", MODELS_SCHEMA, MODELS_STREAM_NAME));

    final AutoCloseableIterator<AirbyteMessage> read = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, null);
    final List<AirbyteMessage> actualRecords = AutoCloseableIterators.toListAndClose(read);

    final Set<AirbyteRecordMessage> recordMessages = extractRecordMessages(actualRecords);
    final List<AirbyteStateMessage> stateMessages = extractStateMessages(actualRecords);

    assertExpectedRecords(Collections.emptySet(), recordMessages);
    assertEquals(1, stateMessages.size());
    assertNotNull(stateMessages.get(0).getData());
    assertExpectedStateMessages(stateMessages);
  }

  @Test
  @DisplayName("When no changes have been made to the database since the previous sync, no records are returned.")
  void testNoDataOnSecondSync() throws Exception {
    final AutoCloseableIterator<AirbyteMessage> read1 = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, null);
    final List<AirbyteMessage> actualRecords1 = AutoCloseableIterators.toListAndClose(read1);
    final JsonNode state = Jsons.jsonNode(extractStateMessages(actualRecords1));

    final AutoCloseableIterator<AirbyteMessage> read2 = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, state);
    final List<AirbyteMessage> actualRecords2 = AutoCloseableIterators.toListAndClose(read2);

    final Set<AirbyteRecordMessage> recordMessages2 = extractRecordMessages(actualRecords2);
    final List<AirbyteStateMessage> stateMessages2 = extractStateMessages(actualRecords2);

    assertExpectedRecords(Collections.emptySet(), recordMessages2);
    assertEquals(1, stateMessages2.size());
    assertNotNull(stateMessages2.get(0).getData());
    assertExpectedStateMessages(stateMessages2);
  }

  @Test
  void testCheck() throws Exception {
    final AirbyteConnectionStatus status = getSource().check(getConfig());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.SUCCEEDED);
  }

  @Test
  void testDiscover() throws Exception {
    final AirbyteCatalog expectedCatalog = expectedCatalogForDiscover();
    final AirbyteCatalog actualCatalog = getSource().discover(getConfig());

    assertEquals(
        expectedCatalog.getStreams().stream().sorted(Comparator.comparing(AirbyteStream::getName))
            .collect(Collectors.toList()),
        actualCatalog.getStreams().stream().sorted(Comparator.comparing(AirbyteStream::getName))
            .collect(Collectors.toList()));
  }

  @Test
  public void newTableSnapshotTest() throws Exception {
    final AutoCloseableIterator<AirbyteMessage> firstBatchIterator = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, null);
    final List<AirbyteMessage> dataFromFirstBatch = AutoCloseableIterators
        .toListAndClose(firstBatchIterator);
    final Set<AirbyteRecordMessage> recordsFromFirstBatch = extractRecordMessages(
        dataFromFirstBatch);
    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessages(dataFromFirstBatch);
    assertEquals(1, stateAfterFirstBatch.size());

    final AirbyteStateMessage stateMessageEmittedAfterFirstSyncCompletion = stateAfterFirstBatch.get(0);
    assertEquals(AirbyteStateMessage.AirbyteStateType.GLOBAL, stateMessageEmittedAfterFirstSyncCompletion.getType());
    assertNotNull(stateMessageEmittedAfterFirstSyncCompletion.getGlobal().getSharedState());
    final Set<StreamDescriptor> streamsInStateAfterFirstSyncCompletion = stateMessageEmittedAfterFirstSyncCompletion.getGlobal().getStreamStates()
        .stream()
        .map(AirbyteStreamState::getStreamDescriptor)
        .collect(Collectors.toSet());
    assertEquals(1, streamsInStateAfterFirstSyncCompletion.size());
    assertTrue(streamsInStateAfterFirstSyncCompletion.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(MODELS_SCHEMA)));
    assertNotNull(stateMessageEmittedAfterFirstSyncCompletion.getData());

    assertEquals((MODEL_RECORDS.size()), recordsFromFirstBatch.size());
    assertExpectedRecords(new HashSet<>(MODEL_RECORDS), recordsFromFirstBatch);

    final JsonNode state = stateAfterFirstBatch.get(0).getData();

    final ConfiguredAirbyteCatalog newTables = CatalogHelpers
        .toDefaultConfiguredCatalog(new AirbyteCatalog().withStreams(List.of(
            CatalogHelpers.createAirbyteStream(
                MODELS_STREAM_NAME + "_random",
                randomTableSchema(),
                Field.of(COL_ID + "_random", JsonSchemaType.NUMBER),
                Field.of(COL_MAKE_ID + "_random", JsonSchemaType.NUMBER),
                Field.of(COL_MODEL + "_random", JsonSchemaType.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID + "_random"))))));

    newTables.getStreams().forEach(s -> s.setSyncMode(SyncMode.INCREMENTAL));
    final List<ConfiguredAirbyteStream> combinedStreams = new ArrayList<>();
    combinedStreams.addAll(CONFIGURED_CATALOG.getStreams());
    combinedStreams.addAll(newTables.getStreams());

    final ConfiguredAirbyteCatalog updatedCatalog = new ConfiguredAirbyteCatalog().withStreams(combinedStreams);

    /*
     * Write 20 records to the existing table
     */
    final Set<JsonNode> recordsWritten = new HashSet<>();
    for (int recordsCreated = 0; recordsCreated < 20; recordsCreated++) {
      final JsonNode record =
          Jsons.jsonNode(ImmutableMap
              .of(COL_ID, 100 + recordsCreated, COL_MAKE_ID, 1, COL_MODEL,
                  "F-" + recordsCreated));
      recordsWritten.add(record);
      writeModelRecord(record);
    }

    final AutoCloseableIterator<AirbyteMessage> secondBatchIterator = getSource()
        .read(getConfig(), updatedCatalog, state);
    final List<AirbyteMessage> dataFromSecondBatch = AutoCloseableIterators
        .toListAndClose(secondBatchIterator);

    final List<AirbyteStateMessage> stateAfterSecondBatch = extractStateMessages(dataFromSecondBatch);
    assertEquals(2, stateAfterSecondBatch.size());

    final AirbyteStateMessage stateMessageEmittedAfterSnapshotCompletionInSecondSync = stateAfterSecondBatch.get(0);
    assertEquals(AirbyteStateMessage.AirbyteStateType.GLOBAL, stateMessageEmittedAfterSnapshotCompletionInSecondSync.getType());
    assertEquals(stateMessageEmittedAfterFirstSyncCompletion.getGlobal().getSharedState(),
        stateMessageEmittedAfterSnapshotCompletionInSecondSync.getGlobal().getSharedState());
    final Set<StreamDescriptor> streamsInSnapshotState = stateMessageEmittedAfterSnapshotCompletionInSecondSync.getGlobal().getStreamStates()
        .stream()
        .map(AirbyteStreamState::getStreamDescriptor)
        .collect(Collectors.toSet());
    assertEquals(2, streamsInSnapshotState.size());
    assertTrue(
        streamsInSnapshotState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME + "_random").withNamespace(randomTableSchema())));
    assertTrue(streamsInSnapshotState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(MODELS_SCHEMA)));
    assertNotNull(stateMessageEmittedAfterSnapshotCompletionInSecondSync.getData());

    final AirbyteStateMessage stateMessageEmittedAfterSecondSyncCompletion = stateAfterSecondBatch.get(1);
    assertEquals(AirbyteStateMessage.AirbyteStateType.GLOBAL, stateMessageEmittedAfterSecondSyncCompletion.getType());
    assertNotEquals(stateMessageEmittedAfterFirstSyncCompletion.getGlobal().getSharedState(),
        stateMessageEmittedAfterSecondSyncCompletion.getGlobal().getSharedState());
    final Set<StreamDescriptor> streamsInSyncCompletionState = stateMessageEmittedAfterSecondSyncCompletion.getGlobal().getStreamStates()
        .stream()
        .map(AirbyteStreamState::getStreamDescriptor)
        .collect(Collectors.toSet());
    assertEquals(2, streamsInSnapshotState.size());
    assertTrue(
        streamsInSyncCompletionState.contains(
            new StreamDescriptor().withName(MODELS_STREAM_NAME + "_random").withNamespace(randomTableSchema())));
    assertTrue(streamsInSyncCompletionState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(MODELS_SCHEMA)));
    assertNotNull(stateMessageEmittedAfterSecondSyncCompletion.getData());

    final Map<String, Set<AirbyteRecordMessage>> recordsStreamWise = extractRecordMessagesStreamWise(dataFromSecondBatch);
    assertTrue(recordsStreamWise.containsKey(MODELS_STREAM_NAME));
    assertTrue(recordsStreamWise.containsKey(MODELS_STREAM_NAME + "_random"));

    final Set<AirbyteRecordMessage> recordsForModelsStreamFromSecondBatch = recordsStreamWise.get(MODELS_STREAM_NAME);
    final Set<AirbyteRecordMessage> recordsForModelsRandomStreamFromSecondBatch = recordsStreamWise.get(MODELS_STREAM_NAME + "_random");

    assertEquals((MODEL_RECORDS_RANDOM.size()), recordsForModelsRandomStreamFromSecondBatch.size());
    assertEquals(20, recordsForModelsStreamFromSecondBatch.size());
    assertExpectedRecords(new HashSet<>(MODEL_RECORDS_RANDOM), recordsForModelsRandomStreamFromSecondBatch,
        recordsForModelsRandomStreamFromSecondBatch.stream().map(AirbyteRecordMessage::getStream).collect(
            Collectors.toSet()),
        Sets
            .newHashSet(MODELS_STREAM_NAME + "_random"),
        randomTableSchema());
    assertExpectedRecords(recordsWritten, recordsForModelsStreamFromSecondBatch);

    /*
     * Write 20 records to both the tables
     */
    final Set<JsonNode> recordsWrittenInRandomTable = new HashSet<>();
    recordsWritten.clear();
    for (int recordsCreated = 30; recordsCreated < 50; recordsCreated++) {
      final JsonNode record =
          Jsons.jsonNode(ImmutableMap
              .of(COL_ID, 100 + recordsCreated, COL_MAKE_ID, 1, COL_MODEL,
                  "F-" + recordsCreated));
      writeModelRecord(record);
      recordsWritten.add(record);

      final JsonNode record2 = Jsons
          .jsonNode(ImmutableMap
              .of(COL_ID + "_random", 11000 + recordsCreated, COL_MAKE_ID + "_random", 1 + recordsCreated, COL_MODEL + "_random",
                  "Fiesta-random" + recordsCreated));
      writeRecords(record2, randomTableSchema(), MODELS_STREAM_NAME + "_random",
          COL_ID + "_random", COL_MAKE_ID + "_random", COL_MODEL + "_random");
      recordsWrittenInRandomTable.add(record2);
    }

    final JsonNode state2 = stateAfterSecondBatch.get(1).getData();
    final AutoCloseableIterator<AirbyteMessage> thirdBatchIterator = getSource()
        .read(getConfig(), updatedCatalog, state2);
    final List<AirbyteMessage> dataFromThirdBatch = AutoCloseableIterators
        .toListAndClose(thirdBatchIterator);

    final List<AirbyteStateMessage> stateAfterThirdBatch = extractStateMessages(dataFromThirdBatch);
    assertEquals(1, stateAfterThirdBatch.size());

    final AirbyteStateMessage stateMessageEmittedAfterThirdSyncCompletion = stateAfterThirdBatch.get(0);
    assertEquals(AirbyteStateMessage.AirbyteStateType.GLOBAL, stateMessageEmittedAfterThirdSyncCompletion.getType());
    assertNotEquals(stateMessageEmittedAfterThirdSyncCompletion.getGlobal().getSharedState(),
        stateMessageEmittedAfterSecondSyncCompletion.getGlobal().getSharedState());
    final Set<StreamDescriptor> streamsInSyncCompletionStateAfterThirdSync = stateMessageEmittedAfterThirdSyncCompletion.getGlobal().getStreamStates()
        .stream()
        .map(AirbyteStreamState::getStreamDescriptor)
        .collect(Collectors.toSet());
    assertTrue(
        streamsInSyncCompletionStateAfterThirdSync.contains(
            new StreamDescriptor().withName(MODELS_STREAM_NAME + "_random").withNamespace(randomTableSchema())));
    assertTrue(streamsInSyncCompletionStateAfterThirdSync.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(MODELS_SCHEMA)));
    assertNotNull(stateMessageEmittedAfterThirdSyncCompletion.getData());

    final Map<String, Set<AirbyteRecordMessage>> recordsStreamWiseFromThirdBatch = extractRecordMessagesStreamWise(dataFromThirdBatch);
    assertTrue(recordsStreamWiseFromThirdBatch.containsKey(MODELS_STREAM_NAME));
    assertTrue(recordsStreamWiseFromThirdBatch.containsKey(MODELS_STREAM_NAME + "_random"));

    final Set<AirbyteRecordMessage> recordsForModelsStreamFromThirdBatch = recordsStreamWiseFromThirdBatch.get(MODELS_STREAM_NAME);
    final Set<AirbyteRecordMessage> recordsForModelsRandomStreamFromThirdBatch = recordsStreamWiseFromThirdBatch.get(MODELS_STREAM_NAME + "_random");

    assertEquals(20, recordsForModelsStreamFromThirdBatch.size());
    assertEquals(20, recordsForModelsRandomStreamFromThirdBatch.size());
    assertExpectedRecords(recordsWritten, recordsForModelsStreamFromThirdBatch);
    assertExpectedRecords(recordsWrittenInRandomTable, recordsForModelsRandomStreamFromThirdBatch,
        recordsForModelsRandomStreamFromThirdBatch.stream().map(AirbyteRecordMessage::getStream).collect(
            Collectors.toSet()),
        Sets
            .newHashSet(MODELS_STREAM_NAME + "_random"),
        randomTableSchema());
  }

  protected AirbyteCatalog expectedCatalogForDiscover() {
    final AirbyteCatalog expectedCatalog = Jsons.clone(CATALOG);

    createTable(MODELS_SCHEMA, MODELS_STREAM_NAME + "_2",
        columnClause(ImmutableMap.of(COL_ID, "INTEGER", COL_MAKE_ID, "INTEGER", COL_MODEL, "VARCHAR(200)"), Optional.empty()));

    final List<AirbyteStream> streams = expectedCatalog.getStreams();
    // stream with PK
    streams.get(0).setSourceDefinedCursor(true);
    addCdcMetadataColumns(streams.get(0));

    final AirbyteStream streamWithoutPK = CatalogHelpers.createAirbyteStream(
        MODELS_STREAM_NAME + "_2",
        MODELS_SCHEMA,
        Field.of(COL_ID, JsonSchemaType.INTEGER),
        Field.of(COL_MAKE_ID, JsonSchemaType.INTEGER),
        Field.of(COL_MODEL, JsonSchemaType.STRING));
    streamWithoutPK.setSourceDefinedPrimaryKey(Collections.emptyList());
    streamWithoutPK.setSupportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    addCdcMetadataColumns(streamWithoutPK);

    final AirbyteStream randomStream = CatalogHelpers.createAirbyteStream(
        MODELS_STREAM_NAME + "_random",
        randomTableSchema(),
        Field.of(COL_ID + "_random", JsonSchemaType.INTEGER),
        Field.of(COL_MAKE_ID + "_random", JsonSchemaType.INTEGER),
        Field.of(COL_MODEL + "_random", JsonSchemaType.STRING))
        .withSourceDefinedCursor(true)
        .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
        .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID + "_random")));
    addCdcMetadataColumns(randomStream);

    streams.add(streamWithoutPK);
    streams.add(randomStream);
    expectedCatalog.withStreams(streams);
    return expectedCatalog;
  }

  /**
   * The schema of a random table which is used as a new table in snapshot test
   */
  protected abstract String randomTableSchema();

  protected abstract CdcTargetPosition cdcLatestTargetPosition();

  protected abstract CdcTargetPosition extractPosition(final JsonNode record);

  protected abstract void assertNullCdcMetaData(final JsonNode data);

  protected abstract void assertCdcMetaData(final JsonNode data, final boolean deletedAtNull);

  protected abstract void removeCDCColumns(final ObjectNode data);

  protected abstract void addCdcMetadataColumns(final AirbyteStream stream);

  protected abstract Source getSource();

  protected abstract JsonNode getConfig();

  protected abstract Database getDatabase();

  protected abstract void assertExpectedStateMessages(final List<AirbyteStateMessage> stateMessages);

}
