/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.debezium;

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
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.testutils.TestDatabase;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import io.airbyte.protocol.models.v0.SyncMode;
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
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class CdcSourceTest<S extends Source, T extends TestDatabase<?, T, ?>> {

  static private final Logger LOGGER = LoggerFactory.getLogger(CdcSourceTest.class);

  static protected final String MODELS_STREAM_NAME = "models";
  static protected final Set<String> STREAM_NAMES = Set.of(MODELS_STREAM_NAME);
  static protected final String COL_ID = "id";
  static protected final String COL_MAKE_ID = "make_id";
  static protected final String COL_MODEL = "model";

  static protected final List<JsonNode> MODEL_RECORDS = ImmutableList.of(
      Jsons.jsonNode(ImmutableMap.of(COL_ID, 11, COL_MAKE_ID, 1, COL_MODEL, "Fiesta")),
      Jsons.jsonNode(ImmutableMap.of(COL_ID, 12, COL_MAKE_ID, 1, COL_MODEL, "Focus")),
      Jsons.jsonNode(ImmutableMap.of(COL_ID, 13, COL_MAKE_ID, 1, COL_MODEL, "Ranger")),
      Jsons.jsonNode(ImmutableMap.of(COL_ID, 14, COL_MAKE_ID, 2, COL_MODEL, "GLA")),
      Jsons.jsonNode(ImmutableMap.of(COL_ID, 15, COL_MAKE_ID, 2, COL_MODEL, "A 220")),
      Jsons.jsonNode(ImmutableMap.of(COL_ID, 16, COL_MAKE_ID, 2, COL_MODEL, "E 350")));

  static protected final String RANDOM_TABLE_NAME = MODELS_STREAM_NAME + "_random";

  static protected final List<JsonNode> MODEL_RECORDS_RANDOM = MODEL_RECORDS.stream()
      .map(r -> Jsons.jsonNode(ImmutableMap.of(
          COL_ID + "_random", r.get(COL_ID).asInt() * 1000,
          COL_MAKE_ID + "_random", r.get(COL_MAKE_ID),
          COL_MODEL + "_random", r.get(COL_MODEL).asText() + "-random")))
      .toList();

  protected T testdb;

  protected String createTableSqlFmt() {
    return "CREATE TABLE %s.%s(%s);";
  }

  protected String createSchemaSqlFmt() {
    return "CREATE SCHEMA %s;";
  }

  protected String modelsSchema() {
    return "models_schema";
  }

  /**
   * The schema of a random table which is used as a new table in snapshot test
   */
  protected String randomSchema() {
    return "models_schema_random";
  }

  protected AirbyteCatalog getCatalog() {
    return new AirbyteCatalog().withStreams(List.of(
        CatalogHelpers.createAirbyteStream(
            MODELS_STREAM_NAME,
            modelsSchema(),
            Field.of(COL_ID, JsonSchemaType.INTEGER),
            Field.of(COL_MAKE_ID, JsonSchemaType.INTEGER),
            Field.of(COL_MODEL, JsonSchemaType.STRING))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID)))));
  }

  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    final var configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(getCatalog());
    configuredCatalog.getStreams().forEach(s -> s.setSyncMode(SyncMode.INCREMENTAL));
    return configuredCatalog;
  }

  protected abstract T createTestDatabase();

  protected abstract S source();

  protected abstract JsonNode config();

  protected abstract CdcTargetPosition<?> cdcLatestTargetPosition();

  protected abstract CdcTargetPosition<?> extractPosition(final JsonNode record);

  protected abstract void assertNullCdcMetaData(final JsonNode data);

  protected abstract void assertCdcMetaData(final JsonNode data, final boolean deletedAtNull);

  protected abstract void removeCDCColumns(final ObjectNode data);

  protected abstract void addCdcMetadataColumns(final AirbyteStream stream);

  protected abstract void addCdcDefaultCursorField(final AirbyteStream stream);

  protected abstract void assertExpectedStateMessages(final List<AirbyteStateMessage> stateMessages);

  @BeforeEach
  protected void setup() {
    testdb = createTestDatabase();

    // create and populate actual table
    final var actualColumns = ImmutableMap.of(
        COL_ID, "INTEGER",
        COL_MAKE_ID, "INTEGER",
        COL_MODEL, "VARCHAR(200)");
    testdb
        .with(createSchemaSqlFmt(), modelsSchema())
        .with(createTableSqlFmt(), modelsSchema(), MODELS_STREAM_NAME, columnClause(actualColumns, Optional.of(COL_ID)));
    for (final JsonNode recordJson : MODEL_RECORDS) {
      writeModelRecord(recordJson);
    }

    // Create and populate random table.
    // This table is not part of Airbyte sync. It is being created just to make sure the schemas not
    // being synced by Airbyte are not causing issues with our debezium logic.
    final var randomColumns = ImmutableMap.of(
        COL_ID + "_random", "INTEGER",
        COL_MAKE_ID + "_random", "INTEGER",
        COL_MODEL + "_random", "VARCHAR(200)");
    if (!randomSchema().equals(modelsSchema())) {
      testdb.with(createSchemaSqlFmt(), randomSchema());
    }
    testdb.with(createTableSqlFmt(), randomSchema(), RANDOM_TABLE_NAME, columnClause(randomColumns, Optional.of(COL_ID + "_random")));
    for (final JsonNode recordJson : MODEL_RECORDS_RANDOM) {
      writeRecords(recordJson, randomSchema(), RANDOM_TABLE_NAME,
          COL_ID + "_random", COL_MAKE_ID + "_random", COL_MODEL + "_random");
    }
  }

  @AfterEach
  protected void tearDown() {
    try {
      testdb.close();
    } catch (Throwable e) {
      LOGGER.error("exception during teardown", e);
    }
  }

  protected String columnClause(final Map<String, String> columnsWithDataType, final Optional<String> primaryKey) {
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

  protected void writeModelRecord(final JsonNode recordJson) {
    writeRecords(recordJson, modelsSchema(), MODELS_STREAM_NAME, COL_ID, COL_MAKE_ID, COL_MODEL);
  }

  protected void writeRecords(
                              final JsonNode recordJson,
                              final String dbName,
                              final String streamName,
                              final String idCol,
                              final String makeIdCol,
                              final String modelCol) {
    testdb.with("INSERT INTO %s.%s (%s, %s, %s) VALUES (%s, %s, '%s');", dbName, streamName,
        idCol, makeIdCol, modelCol,
        recordJson.get(idCol).asInt(), recordJson.get(makeIdCol).asInt(),
        recordJson.get(modelCol).asText());
  }

  protected void deleteMessageOnIdCol(final String streamName, final String idCol, final int idValue) {
    testdb.with("DELETE FROM %s.%s WHERE %s = %s", modelsSchema(), streamName, idCol, idValue);
  }

  protected void deleteCommand(final String streamName) {
    testdb.with("DELETE FROM %s.%s", modelsSchema(), streamName);
  }

  protected void updateCommand(final String streamName, final String modelCol, final String modelVal, final String idCol, final int idValue) {
    testdb.with("UPDATE %s.%s SET %s = '%s' WHERE %s = %s", modelsSchema(), streamName,
        modelCol, modelVal, COL_ID, 11);
  }

  static protected Set<AirbyteRecordMessage> removeDuplicates(final Set<AirbyteRecordMessage> messages) {
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
    assertExpectedRecords(expectedRecords, actualRecords, cdcStreams, STREAM_NAMES, modelsSchema());
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
    final AutoCloseableIterator<AirbyteMessage> read = source().read(config(), getConfiguredCatalog(), null);
    final List<AirbyteMessage> actualRecords = AutoCloseableIterators.toListAndClose(read);

    final Set<AirbyteRecordMessage> recordMessages = extractRecordMessages(actualRecords);
    final List<AirbyteStateMessage> stateMessages = extractStateMessages(actualRecords);

    assertNotNull(targetPosition);
    recordMessages.forEach(record -> {
      compareTargetPositionFromTheRecordsWithTargetPostionGeneratedBeforeSync(targetPosition, record);
    });

    assertExpectedRecords(new HashSet<>(MODEL_RECORDS), recordMessages);
    assertExpectedStateMessages(stateMessages);
  }

  protected void compareTargetPositionFromTheRecordsWithTargetPostionGeneratedBeforeSync(final CdcTargetPosition targetPosition,
                                                                                         final AirbyteRecordMessage record) {
    assertEquals(extractPosition(record.getData()), targetPosition);
  }

  @Test
  @DisplayName("When a record is deleted, produces a deletion record.")
  void testDelete() throws Exception {
    final AutoCloseableIterator<AirbyteMessage> read1 = source()
        .read(config(), getConfiguredCatalog(), null);
    final List<AirbyteMessage> actualRecords1 = AutoCloseableIterators.toListAndClose(read1);
    final List<AirbyteStateMessage> stateMessages1 = extractStateMessages(actualRecords1);
    assertExpectedStateMessages(stateMessages1);

    deleteMessageOnIdCol(MODELS_STREAM_NAME, COL_ID, 11);

    final JsonNode state = Jsons.jsonNode(Collections.singletonList(stateMessages1.get(stateMessages1.size() - 1)));
    final AutoCloseableIterator<AirbyteMessage> read2 = source()
        .read(config(), getConfiguredCatalog(), state);
    final List<AirbyteMessage> actualRecords2 = AutoCloseableIterators.toListAndClose(read2);
    final List<AirbyteRecordMessage> recordMessages2 = new ArrayList<>(
        extractRecordMessages(actualRecords2));
    final List<AirbyteStateMessage> stateMessages2 = extractStateMessages(actualRecords2);
    assertExpectedStateMessagesFromIncrementalSync(stateMessages2);
    assertEquals(1, recordMessages2.size());
    assertEquals(11, recordMessages2.get(0).getData().get(COL_ID).asInt());
    assertCdcMetaData(recordMessages2.get(0).getData(), false);
  }

  protected void assertExpectedStateMessagesFromIncrementalSync(final List<AirbyteStateMessage> stateMessages) {
    assertExpectedStateMessages(stateMessages);
  }

  @Test
  @DisplayName("When a record is updated, produces an update record.")
  void testUpdate() throws Exception {
    final String updatedModel = "Explorer";
    final AutoCloseableIterator<AirbyteMessage> read1 = source()
        .read(config(), getConfiguredCatalog(), null);
    final List<AirbyteMessage> actualRecords1 = AutoCloseableIterators.toListAndClose(read1);
    final List<AirbyteStateMessage> stateMessages1 = extractStateMessages(actualRecords1);
    assertExpectedStateMessages(stateMessages1);

    updateCommand(MODELS_STREAM_NAME, COL_MODEL, updatedModel, COL_ID, 11);

    final JsonNode state = Jsons.jsonNode(Collections.singletonList(stateMessages1.get(stateMessages1.size() - 1)));
    final AutoCloseableIterator<AirbyteMessage> read2 = source()
        .read(config(), getConfiguredCatalog(), state);
    final List<AirbyteMessage> actualRecords2 = AutoCloseableIterators.toListAndClose(read2);
    final List<AirbyteRecordMessage> recordMessages2 = new ArrayList<>(
        extractRecordMessages(actualRecords2));
    final List<AirbyteStateMessage> stateMessages2 = extractStateMessages(actualRecords2);
    assertExpectedStateMessagesFromIncrementalSync(stateMessages2);
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

    final AutoCloseableIterator<AirbyteMessage> firstBatchIterator = source()
        .read(config(), getConfiguredCatalog(), null);
    final List<AirbyteMessage> dataFromFirstBatch = AutoCloseableIterators
        .toListAndClose(firstBatchIterator);
    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessages(dataFromFirstBatch);
    assertExpectedStateMessagesForRecordsProducedDuringAndAfterSync(stateAfterFirstBatch);
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

    final JsonNode state = Jsons.jsonNode(Collections.singletonList(stateAfterFirstBatch.get(stateAfterFirstBatch.size() - 1)));
    final AutoCloseableIterator<AirbyteMessage> secondBatchIterator = source()
        .read(config(), getConfiguredCatalog(), state);
    final List<AirbyteMessage> dataFromSecondBatch = AutoCloseableIterators
        .toListAndClose(secondBatchIterator);

    final List<AirbyteStateMessage> stateAfterSecondBatch = extractStateMessages(dataFromSecondBatch);
    assertExpectedStateMessagesFromIncrementalSync(stateAfterSecondBatch);

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

  protected void assertExpectedStateMessagesForRecordsProducedDuringAndAfterSync(final List<AirbyteStateMessage> stateAfterFirstBatch) {
    assertExpectedStateMessages(stateAfterFirstBatch);
  }

  @Test
  @DisplayName("When both incremental CDC and full refresh are configured for different streams in a sync, the data is replicated as expected.")
  void testCdcAndFullRefreshInSameSync() throws Exception {
    final ConfiguredAirbyteCatalog configuredCatalog = Jsons.clone(getConfiguredCatalog());

    final List<JsonNode> MODEL_RECORDS_2 = ImmutableList.of(
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 110, COL_MAKE_ID, 1, COL_MODEL, "Fiesta-2")),
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 120, COL_MAKE_ID, 1, COL_MODEL, "Focus-2")),
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 130, COL_MAKE_ID, 1, COL_MODEL, "Ranger-2")),
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 140, COL_MAKE_ID, 2, COL_MODEL, "GLA-2")),
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 150, COL_MAKE_ID, 2, COL_MODEL, "A 220-2")),
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 160, COL_MAKE_ID, 2, COL_MODEL, "E 350-2")));

    final var columns = ImmutableMap.of(COL_ID, "INTEGER", COL_MAKE_ID, "INTEGER", COL_MODEL, "VARCHAR(200)");
    testdb.with(createTableSqlFmt(), modelsSchema(), MODELS_STREAM_NAME + "_2", columnClause(columns, Optional.of(COL_ID)));

    for (final JsonNode recordJson : MODEL_RECORDS_2) {
      writeRecords(recordJson, modelsSchema(), MODELS_STREAM_NAME + "_2", COL_ID, COL_MAKE_ID, COL_MODEL);
    }

    final ConfiguredAirbyteStream airbyteStream = new ConfiguredAirbyteStream()
        .withStream(CatalogHelpers.createAirbyteStream(
            MODELS_STREAM_NAME + "_2",
            modelsSchema(),
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

    final AutoCloseableIterator<AirbyteMessage> read1 = source()
        .read(config(), configuredCatalog, null);
    final List<AirbyteMessage> actualRecords1 = AutoCloseableIterators.toListAndClose(read1);

    final Set<AirbyteRecordMessage> recordMessages1 = extractRecordMessages(actualRecords1);
    final List<AirbyteStateMessage> stateMessages1 = extractStateMessages(actualRecords1);
    final HashSet<String> names = new HashSet<>(STREAM_NAMES);
    names.add(MODELS_STREAM_NAME + "_2");
    assertExpectedStateMessages(stateMessages1);
    assertExpectedRecords(Streams.concat(MODEL_RECORDS_2.stream(), MODEL_RECORDS.stream())
        .collect(Collectors.toSet()),
        recordMessages1,
        Collections.singleton(MODELS_STREAM_NAME),
        names,
        modelsSchema());

    final JsonNode puntoRecord = Jsons
        .jsonNode(ImmutableMap.of(COL_ID, 100, COL_MAKE_ID, 3, COL_MODEL, "Punto"));
    writeModelRecord(puntoRecord);

    final JsonNode state = Jsons.jsonNode(Collections.singletonList(stateMessages1.get(stateMessages1.size() - 1)));
    final AutoCloseableIterator<AirbyteMessage> read2 = source()
        .read(config(), configuredCatalog, state);
    final List<AirbyteMessage> actualRecords2 = AutoCloseableIterators.toListAndClose(read2);

    final Set<AirbyteRecordMessage> recordMessages2 = extractRecordMessages(actualRecords2);
    final List<AirbyteStateMessage> stateMessages2 = extractStateMessages(actualRecords2);
    assertExpectedStateMessagesFromIncrementalSync(stateMessages2);
    assertExpectedRecords(
        Streams.concat(MODEL_RECORDS_2.stream(), Stream.of(puntoRecord))
            .collect(Collectors.toSet()),
        recordMessages2,
        Collections.singleton(MODELS_STREAM_NAME),
        names,
        modelsSchema());
  }

  @Test
  @DisplayName("When no records exist, no records are returned.")
  void testNoData() throws Exception {

    deleteCommand(MODELS_STREAM_NAME);
    final AutoCloseableIterator<AirbyteMessage> read = source().read(config(), getConfiguredCatalog(), null);
    final List<AirbyteMessage> actualRecords = AutoCloseableIterators.toListAndClose(read);

    final Set<AirbyteRecordMessage> recordMessages = extractRecordMessages(actualRecords);
    final List<AirbyteStateMessage> stateMessages = extractStateMessages(actualRecords);
    assertExpectedRecords(Collections.emptySet(), recordMessages);
    assertExpectedStateMessagesForNoData(stateMessages);
  }

  protected void assertExpectedStateMessagesForNoData(final List<AirbyteStateMessage> stateMessages) {
    assertExpectedStateMessages(stateMessages);
  }

  @Test
  @DisplayName("When no changes have been made to the database since the previous sync, no records are returned.")
  void testNoDataOnSecondSync() throws Exception {
    final AutoCloseableIterator<AirbyteMessage> read1 = source()
        .read(config(), getConfiguredCatalog(), null);
    final List<AirbyteMessage> actualRecords1 = AutoCloseableIterators.toListAndClose(read1);
    final List<AirbyteStateMessage> stateMessagesFromFirstSync = extractStateMessages(actualRecords1);
    final JsonNode state = Jsons.jsonNode(Collections.singletonList(stateMessagesFromFirstSync.get(stateMessagesFromFirstSync.size() - 1)));

    final AutoCloseableIterator<AirbyteMessage> read2 = source()
        .read(config(), getConfiguredCatalog(), state);
    final List<AirbyteMessage> actualRecords2 = AutoCloseableIterators.toListAndClose(read2);

    final Set<AirbyteRecordMessage> recordMessages2 = extractRecordMessages(actualRecords2);
    final List<AirbyteStateMessage> stateMessages2 = extractStateMessages(actualRecords2);

    assertExpectedRecords(Collections.emptySet(), recordMessages2);
    assertExpectedStateMessagesFromIncrementalSync(stateMessages2);
  }

  @Test
  void testCheck() throws Exception {
    final AirbyteConnectionStatus status = source().check(config());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.SUCCEEDED);
  }

  @Test
  void testDiscover() throws Exception {
    final AirbyteCatalog expectedCatalog = expectedCatalogForDiscover();
    final AirbyteCatalog actualCatalog = source().discover(config());

    assertEquals(
        expectedCatalog.getStreams().stream().sorted(Comparator.comparing(AirbyteStream::getName))
            .collect(Collectors.toList()),
        actualCatalog.getStreams().stream().sorted(Comparator.comparing(AirbyteStream::getName))
            .collect(Collectors.toList()));
  }

  @Test
  public void newTableSnapshotTest() throws Exception {
    final AutoCloseableIterator<AirbyteMessage> firstBatchIterator = source()
        .read(config(), getConfiguredCatalog(), null);
    final List<AirbyteMessage> dataFromFirstBatch = AutoCloseableIterators
        .toListAndClose(firstBatchIterator);
    final Set<AirbyteRecordMessage> recordsFromFirstBatch = extractRecordMessages(
        dataFromFirstBatch);
    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessages(dataFromFirstBatch);
    assertExpectedStateMessages(stateAfterFirstBatch);

    final AirbyteStateMessage stateMessageEmittedAfterFirstSyncCompletion = stateAfterFirstBatch.get(stateAfterFirstBatch.size() - 1);
    assertEquals(AirbyteStateMessage.AirbyteStateType.GLOBAL, stateMessageEmittedAfterFirstSyncCompletion.getType());
    assertNotNull(stateMessageEmittedAfterFirstSyncCompletion.getGlobal().getSharedState());
    final Set<StreamDescriptor> streamsInStateAfterFirstSyncCompletion = stateMessageEmittedAfterFirstSyncCompletion.getGlobal().getStreamStates()
        .stream()
        .map(AirbyteStreamState::getStreamDescriptor)
        .collect(Collectors.toSet());
    assertEquals(1, streamsInStateAfterFirstSyncCompletion.size());
    assertTrue(streamsInStateAfterFirstSyncCompletion.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(modelsSchema())));
    assertNotNull(stateMessageEmittedAfterFirstSyncCompletion.getData());

    assertEquals((MODEL_RECORDS.size()), recordsFromFirstBatch.size());
    assertExpectedRecords(new HashSet<>(MODEL_RECORDS), recordsFromFirstBatch);

    final JsonNode state = stateAfterFirstBatch.get(stateAfterFirstBatch.size() - 1).getData();

    final ConfiguredAirbyteCatalog newTables = CatalogHelpers
        .toDefaultConfiguredCatalog(new AirbyteCatalog().withStreams(List.of(
            CatalogHelpers.createAirbyteStream(
                RANDOM_TABLE_NAME,
                randomSchema(),
                Field.of(COL_ID + "_random", JsonSchemaType.NUMBER),
                Field.of(COL_MAKE_ID + "_random", JsonSchemaType.NUMBER),
                Field.of(COL_MODEL + "_random", JsonSchemaType.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID + "_random"))))));

    newTables.getStreams().forEach(s -> s.setSyncMode(SyncMode.INCREMENTAL));
    final List<ConfiguredAirbyteStream> combinedStreams = new ArrayList<>();
    combinedStreams.addAll(getConfiguredCatalog().getStreams());
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

    final AutoCloseableIterator<AirbyteMessage> secondBatchIterator = source()
        .read(config(), updatedCatalog, state);
    final List<AirbyteMessage> dataFromSecondBatch = AutoCloseableIterators
        .toListAndClose(secondBatchIterator);

    final List<AirbyteStateMessage> stateAfterSecondBatch = extractStateMessages(dataFromSecondBatch);
    assertStateMessagesForNewTableSnapshotTest(stateAfterSecondBatch, stateMessageEmittedAfterFirstSyncCompletion);

    final Map<String, Set<AirbyteRecordMessage>> recordsStreamWise = extractRecordMessagesStreamWise(dataFromSecondBatch);
    assertTrue(recordsStreamWise.containsKey(MODELS_STREAM_NAME));
    assertTrue(recordsStreamWise.containsKey(RANDOM_TABLE_NAME));

    final Set<AirbyteRecordMessage> recordsForModelsStreamFromSecondBatch = recordsStreamWise.get(MODELS_STREAM_NAME);
    final Set<AirbyteRecordMessage> recordsForModelsRandomStreamFromSecondBatch = recordsStreamWise.get(RANDOM_TABLE_NAME);

    assertEquals((MODEL_RECORDS_RANDOM.size()), recordsForModelsRandomStreamFromSecondBatch.size());
    assertEquals(20, recordsForModelsStreamFromSecondBatch.size());
    assertExpectedRecords(new HashSet<>(MODEL_RECORDS_RANDOM), recordsForModelsRandomStreamFromSecondBatch,
        recordsForModelsRandomStreamFromSecondBatch.stream().map(AirbyteRecordMessage::getStream).collect(
            Collectors.toSet()),
        Sets
            .newHashSet(RANDOM_TABLE_NAME),
        randomSchema());
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
      writeRecords(record2, randomSchema(), RANDOM_TABLE_NAME,
          COL_ID + "_random", COL_MAKE_ID + "_random", COL_MODEL + "_random");
      recordsWrittenInRandomTable.add(record2);
    }

    final JsonNode state2 = stateAfterSecondBatch.get(stateAfterSecondBatch.size() - 1).getData();
    final AutoCloseableIterator<AirbyteMessage> thirdBatchIterator = source()
        .read(config(), updatedCatalog, state2);
    final List<AirbyteMessage> dataFromThirdBatch = AutoCloseableIterators
        .toListAndClose(thirdBatchIterator);

    final List<AirbyteStateMessage> stateAfterThirdBatch = extractStateMessages(dataFromThirdBatch);
    assertTrue(stateAfterThirdBatch.size() >= 1);

    final AirbyteStateMessage stateMessageEmittedAfterThirdSyncCompletion = stateAfterThirdBatch.get(stateAfterThirdBatch.size() - 1);
    assertEquals(AirbyteStateMessage.AirbyteStateType.GLOBAL, stateMessageEmittedAfterThirdSyncCompletion.getType());
    assertNotEquals(stateMessageEmittedAfterThirdSyncCompletion.getGlobal().getSharedState(),
        stateAfterSecondBatch.get(stateAfterSecondBatch.size() - 1).getGlobal().getSharedState());
    final Set<StreamDescriptor> streamsInSyncCompletionStateAfterThirdSync = stateMessageEmittedAfterThirdSyncCompletion.getGlobal().getStreamStates()
        .stream()
        .map(AirbyteStreamState::getStreamDescriptor)
        .collect(Collectors.toSet());
    assertTrue(
        streamsInSyncCompletionStateAfterThirdSync.contains(
            new StreamDescriptor().withName(RANDOM_TABLE_NAME).withNamespace(randomSchema())));
    assertTrue(
        streamsInSyncCompletionStateAfterThirdSync.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(modelsSchema())));
    assertNotNull(stateMessageEmittedAfterThirdSyncCompletion.getData());

    final Map<String, Set<AirbyteRecordMessage>> recordsStreamWiseFromThirdBatch = extractRecordMessagesStreamWise(dataFromThirdBatch);
    assertTrue(recordsStreamWiseFromThirdBatch.containsKey(MODELS_STREAM_NAME));
    assertTrue(recordsStreamWiseFromThirdBatch.containsKey(RANDOM_TABLE_NAME));

    final Set<AirbyteRecordMessage> recordsForModelsStreamFromThirdBatch = recordsStreamWiseFromThirdBatch.get(MODELS_STREAM_NAME);
    final Set<AirbyteRecordMessage> recordsForModelsRandomStreamFromThirdBatch = recordsStreamWiseFromThirdBatch.get(RANDOM_TABLE_NAME);

    assertEquals(20, recordsForModelsStreamFromThirdBatch.size());
    assertEquals(20, recordsForModelsRandomStreamFromThirdBatch.size());
    assertExpectedRecords(recordsWritten, recordsForModelsStreamFromThirdBatch);
    assertExpectedRecords(recordsWrittenInRandomTable, recordsForModelsRandomStreamFromThirdBatch,
        recordsForModelsRandomStreamFromThirdBatch.stream().map(AirbyteRecordMessage::getStream).collect(
            Collectors.toSet()),
        Sets
            .newHashSet(RANDOM_TABLE_NAME),
        randomSchema());
  }

  protected void assertStateMessagesForNewTableSnapshotTest(final List<AirbyteStateMessage> stateMessages,
                                                            final AirbyteStateMessage stateMessageEmittedAfterFirstSyncCompletion) {
    assertEquals(2, stateMessages.size());
    final AirbyteStateMessage stateMessageEmittedAfterSnapshotCompletionInSecondSync = stateMessages.get(0);
    assertEquals(AirbyteStateMessage.AirbyteStateType.GLOBAL, stateMessageEmittedAfterSnapshotCompletionInSecondSync.getType());
    assertEquals(stateMessageEmittedAfterFirstSyncCompletion.getGlobal().getSharedState(),
        stateMessageEmittedAfterSnapshotCompletionInSecondSync.getGlobal().getSharedState());
    final Set<StreamDescriptor> streamsInSnapshotState = stateMessageEmittedAfterSnapshotCompletionInSecondSync.getGlobal().getStreamStates()
        .stream()
        .map(AirbyteStreamState::getStreamDescriptor)
        .collect(Collectors.toSet());
    assertEquals(2, streamsInSnapshotState.size());
    assertTrue(
        streamsInSnapshotState.contains(new StreamDescriptor().withName(RANDOM_TABLE_NAME).withNamespace(randomSchema())));
    assertTrue(streamsInSnapshotState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(modelsSchema())));
    assertNotNull(stateMessageEmittedAfterSnapshotCompletionInSecondSync.getData());

    final AirbyteStateMessage stateMessageEmittedAfterSecondSyncCompletion = stateMessages.get(1);
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
            new StreamDescriptor().withName(RANDOM_TABLE_NAME).withNamespace(randomSchema())));
    assertTrue(streamsInSyncCompletionState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(modelsSchema())));
    assertNotNull(stateMessageEmittedAfterSecondSyncCompletion.getData());
  }

  protected AirbyteCatalog expectedCatalogForDiscover() {
    final AirbyteCatalog expectedCatalog = Jsons.clone(getCatalog());

    final var columns = ImmutableMap.of(COL_ID, "INTEGER", COL_MAKE_ID, "INTEGER", COL_MODEL, "VARCHAR(200)");
    testdb.with(createTableSqlFmt(), modelsSchema(), MODELS_STREAM_NAME + "_2", columnClause(columns, Optional.empty()));

    final List<AirbyteStream> streams = expectedCatalog.getStreams();
    // stream with PK
    streams.get(0).setSourceDefinedCursor(true);
    addCdcMetadataColumns(streams.get(0));
    addCdcDefaultCursorField(streams.get(0));

    final AirbyteStream streamWithoutPK = CatalogHelpers.createAirbyteStream(
        MODELS_STREAM_NAME + "_2",
        modelsSchema(),
        Field.of(COL_ID, JsonSchemaType.INTEGER),
        Field.of(COL_MAKE_ID, JsonSchemaType.INTEGER),
        Field.of(COL_MODEL, JsonSchemaType.STRING));
    streamWithoutPK.setSourceDefinedPrimaryKey(Collections.emptyList());
    streamWithoutPK.setSupportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    addCdcDefaultCursorField(streamWithoutPK);
    addCdcMetadataColumns(streamWithoutPK);

    final AirbyteStream randomStream = CatalogHelpers.createAirbyteStream(
        RANDOM_TABLE_NAME,
        randomSchema(),
        Field.of(COL_ID + "_random", JsonSchemaType.INTEGER),
        Field.of(COL_MAKE_ID + "_random", JsonSchemaType.INTEGER),
        Field.of(COL_MODEL + "_random", JsonSchemaType.STRING))
        .withSourceDefinedCursor(true)
        .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
        .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID + "_random")));

    addCdcDefaultCursorField(randomStream);
    addCdcMetadataColumns(randomStream);

    streams.add(streamWithoutPK);
    streams.add(randomStream);
    expectedCatalog.withStreams(streams);
    return expectedCatalog;
  }

}
