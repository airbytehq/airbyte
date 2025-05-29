/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS_PROPERTY;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_DELETED_AT;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_UPDATED_AT;
import static io.airbyte.integrations.source.mysql.MySqlSource.CDC_DEFAULT_CURSOR;
import static io.airbyte.integrations.source.mysql.MySqlSource.CDC_LOG_FILE;
import static io.airbyte.integrations.source.mysql.MySqlSource.CDC_LOG_POS;
import static io.airbyte.integrations.source.mysql.MySqlSpecConstants.FAIL_SYNC_OPTION;
import static io.airbyte.integrations.source.mysql.cdc.MysqlCdcStateConstants.IS_COMPRESSED;
import static io.airbyte.integrations.source.mysql.cdc.MysqlCdcStateConstants.MYSQL_CDC_OFFSET;
import static io.airbyte.integrations.source.mysql.cdc.MysqlCdcStateConstants.MYSQL_DB_HISTORY;
import static io.airbyte.integrations.source.mysql.initialsync.MySqlInitialLoadStateManager.PRIMARY_KEY_STATE_TYPE;
import static io.airbyte.integrations.source.mysql.initialsync.MySqlInitialLoadStateManager.STATE_TYPE_KEY;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Iterables;
import com.google.common.collect.Lists;
import com.google.common.collect.Streams;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.debezium.CdcSourceTest;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteSchemaHistoryStorage;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase.BaseImage;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase.ContainerModifier;
import io.airbyte.integrations.source.mysql.cdc.MySqlCdcProperties;
import io.airbyte.integrations.source.mysql.cdc.MySqlCdcTargetPosition;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteGlobalState;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.Properties;
import java.util.Random;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

@Order(1)
@edu.umd.cs.findbugs.annotations.SuppressWarnings(value = "NP_NULL_ON_SOME_PATH")
public class CdcMysqlSourceTest extends CdcSourceTest<MySqlSource, MySQLTestDatabase> {

  private static final String INVALID_TIMEZONE_CEST = "CEST";

  private static final Random RANDOM = new Random();

  private static final String TEST_DATE_STREAM_NAME = "TEST_DATE_TABLE";
  private static final String COL_DATE_TIME = "CAR_DATE";
  private static final List<JsonNode> DATE_TIME_RECORDS = ImmutableList.of(
      Jsons.jsonNode(ImmutableMap.of(COL_ID, 120, COL_DATE_TIME, "'2023-00-00 20:37:47'")));

  @Override
  protected void assertExpectedStateMessageCountMatches(final List<? extends AirbyteStateMessage> stateMessages, long totalCount) {
    AtomicLong count = new AtomicLong(0L);
    stateMessages.stream().forEach(
        stateMessage -> count.addAndGet(stateMessage.getSourceStats() != null ? stateMessage.getSourceStats().getRecordCount().longValue() : 0L));
    assertEquals(totalCount, count.get());
  }

  @Override
  protected MySQLTestDatabase createTestDatabase() {
    return MySQLTestDatabase.in(BaseImage.MYSQL_8, ContainerModifier.INVALID_TIMEZONE_CEST).withCdcPermissions();
  }

  @Override
  protected MySqlSource source() {
    return new MySqlSource();
  }

  @Override
  protected JsonNode config() {
    return testdb.testConfigBuilder()
        .withCdcReplication()
        .with(SYNC_CHECKPOINT_RECORDS_PROPERTY, 1)
        .build();
  }

  protected void purgeAllBinaryLogs() {
    testdb.with("RESET MASTER;");
  }

  @Override
  protected String createSchemaSqlFmt() {
    return "CREATE DATABASE IF NOT EXISTS `%s`;";
  }

  @Override
  protected String createTableSqlFmt() {
    return "CREATE TABLE `%s`.`%s`(%s);";
  }

  @Override
  protected String modelsSchema() {
    return getDatabaseName();
  }

  @Override
  protected String randomSchema() {
    return getDatabaseName();
  }

  protected String getDatabaseName() {
    return testdb.getDatabaseName();
  }

  @Override
  protected MySqlCdcTargetPosition cdcLatestTargetPosition() {
    return MySqlCdcTargetPosition.targetPosition(new DefaultJdbcDatabase(testdb.getDataSource()));
  }

  @Override
  protected MySqlCdcTargetPosition extractPosition(final JsonNode record) {
    return new MySqlCdcTargetPosition(record.get(CDC_LOG_FILE).asText(), record.get(CDC_LOG_POS).asLong());
  }

  @Override
  protected void assertNullCdcMetaData(final JsonNode data) {
    assertNull(data.get(CDC_LOG_FILE));
    assertNull(data.get(CDC_LOG_POS));
    assertNull(data.get(CDC_UPDATED_AT));
    assertNull(data.get(CDC_DELETED_AT));
    assertNull(data.get(CDC_DEFAULT_CURSOR));
  }

  @Override
  protected void assertCdcMetaData(final JsonNode data, final boolean deletedAtNull) {
    assertNotNull(data.get(CDC_LOG_FILE));
    assertNotNull(data.get(CDC_LOG_POS));
    assertNotNull(data.get(CDC_UPDATED_AT));
    assertNotNull(data.get(CDC_DEFAULT_CURSOR));
    if (deletedAtNull) {
      assertTrue(data.get(CDC_DELETED_AT).isNull());
    } else {
      assertFalse(data.get(CDC_DELETED_AT).isNull());
    }
  }

  @Override
  protected void removeCDCColumns(final ObjectNode data) {
    data.remove(CDC_LOG_FILE);
    data.remove(CDC_LOG_POS);
    data.remove(CDC_UPDATED_AT);
    data.remove(CDC_DELETED_AT);
    data.remove(CDC_DEFAULT_CURSOR);
  }

  @Override
  protected void addCdcMetadataColumns(final AirbyteStream stream) {
    final ObjectNode jsonSchema = (ObjectNode) stream.getJsonSchema();
    final ObjectNode properties = (ObjectNode) jsonSchema.get("properties");

    final JsonNode airbyteIntegerType = Jsons.jsonNode(ImmutableMap.of("type", "number", "airbyte_type", "integer"));
    final JsonNode numberType = Jsons.jsonNode(ImmutableMap.of("type", "number"));
    final JsonNode stringType = Jsons.jsonNode(ImmutableMap.of("type", "string"));
    properties.set(CDC_LOG_FILE, stringType);
    properties.set(CDC_LOG_POS, numberType);
    properties.set(CDC_UPDATED_AT, stringType);
    properties.set(CDC_DELETED_AT, stringType);
    properties.set(CDC_DEFAULT_CURSOR, airbyteIntegerType);
  }

  @Override
  protected void addCdcDefaultCursorField(final AirbyteStream stream) {
    if (stream.getSupportedSyncModes().contains(SyncMode.INCREMENTAL)) {
      stream.setDefaultCursorField(ImmutableList.of(CDC_DEFAULT_CURSOR));
    }
  }

  @Override
  protected void writeRecords(
                              final JsonNode recordJson,
                              final String dbName,
                              final String streamName,
                              final String idCol,
                              final String makeIdCol,
                              final String modelCol) {
    testdb.with("INSERT INTO `%s` .`%s` (%s, %s, %s) VALUES (%s, %s, '%s');", dbName, streamName,
        idCol, makeIdCol, modelCol,
        recordJson.get(idCol).asInt(), recordJson.get(makeIdCol).asInt(),
        recordJson.get(modelCol).asText());
  }

  @Override
  protected void deleteMessageOnIdCol(final String streamName, final String idCol, final int idValue) {
    testdb.with("DELETE FROM `%s`.`%s` WHERE %s = %s", modelsSchema(), streamName, idCol, idValue);
  }

  @Override
  protected void deleteCommand(final String streamName) {
    testdb.with("DELETE FROM `%s`.`%s`", modelsSchema(), streamName);
  }

  @Override
  protected void updateCommand(final String streamName, final String modelCol, final String modelVal, final String idCol, final int idValue) {
    testdb.with("UPDATE `%s`.`%s` SET %s = '%s' WHERE %s = %s", modelsSchema(), streamName,
        modelCol, modelVal, COL_ID, 11);
  }

  @Override
  protected boolean supportResumableFullRefresh() {
    return true;
  }

  @Override
  protected void addIsResumableFlagForNonPkTable(final AirbyteStream stream) {
    stream.setIsResumable(false);
  }

  @Test
  protected void syncWithReplicationClientPrivilegeRevokedFailsCheck() throws Exception {
    testdb.with("REVOKE REPLICATION CLIENT ON *.* FROM %s@'%%';", testdb.getUserName());
    final AirbyteConnectionStatus status = source().check(config());
    final String expectedErrorMessage = "Please grant REPLICATION CLIENT privilege, so that binary log files are available"
        + " for CDC mode.";
    assertTrue(status.getStatus().equals(Status.FAILED));
    assertTrue(status.getMessage().contains(expectedErrorMessage));
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

    final AutoCloseableIterator<AirbyteMessage> firstBatchIterator = source()
        .read(config(), getConfiguredCatalog(), null);
    final List<AirbyteMessage> dataFromFirstBatch = AutoCloseableIterators
        .toListAndClose(firstBatchIterator);
    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessages(dataFromFirstBatch);
    assertStateForSyncShouldHandlePurgedLogsGracefully(stateAfterFirstBatch, 1);
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

    final JsonNode state = Jsons.jsonNode(Collections.singletonList(stateAfterFirstBatch.get(stateAfterFirstBatch.size() - 1)));
    final AutoCloseableIterator<AirbyteMessage> secondBatchIterator = source()
        .read(config(), getConfiguredCatalog(), state);
    final List<AirbyteMessage> dataFromSecondBatch = AutoCloseableIterators
        .toListAndClose(secondBatchIterator);

    final List<AirbyteStateMessage> stateAfterSecondBatch = extractStateMessages(dataFromSecondBatch);
    assertStateForSyncShouldHandlePurgedLogsGracefully(stateAfterSecondBatch, 2);

    final Set<AirbyteRecordMessage> recordsFromSecondBatch = extractRecordMessages(
        dataFromSecondBatch);
    assertEquals((recordsToCreate * 2) + recordsCreatedBeforeTestCount, recordsFromSecondBatch.size(),
        "Expected 46 records to be replicated in the second sync.");

    JsonNode failSyncConfig = testdb.testConfigBuilder()
        .withCdcReplication(FAIL_SYNC_OPTION)
        .with(SYNC_CHECKPOINT_RECORDS_PROPERTY, 1)
        .build();
    assertThrows(ConfigErrorException.class, () -> source().read(failSyncConfig, getConfiguredCatalog(), state));
  }

  /**
   * This test verifies that multiple states are sent during the CDC process based on number of
   * records. We can ensure that more than one `STATE` type of message is sent, but we are not able to
   * assert the exact number of messages sent as depends on Debezium.
   *
   * @throws Exception Exception happening in the test.
   */
  @Test
  @Timeout(value = 5,
           unit = TimeUnit.MINUTES)
  protected void verifyCheckpointStatesByRecords() throws Exception {
    // We require a huge amount of records, otherwise Debezium will notify directly the last offset.
    final int recordsToCreate = 20_000;

    final AutoCloseableIterator<AirbyteMessage> firstBatchIterator = source()
        .read(config(), getConfiguredCatalog(), null);
    final List<AirbyteMessage> dataFromFirstBatch = AutoCloseableIterators
        .toListAndClose(firstBatchIterator);
    final List<AirbyteStateMessage> stateMessages = extractStateMessages(dataFromFirstBatch);

    // As first `read` operation is from snapshot, it would generate only one state message at the end
    // of the process.
    assertExpectedStateMessages(stateMessages);

    for (int recordsCreated = 0; recordsCreated < recordsToCreate; recordsCreated++) {
      final JsonNode record = Jsons.jsonNode(ImmutableMap
          .of(COL_ID, 200 + recordsCreated, COL_MAKE_ID, 1, COL_MODEL, "F-" + recordsCreated));
      writeModelRecord(record);
    }

    final JsonNode stateAfterFirstSync = Jsons.jsonNode(Collections.singletonList(stateMessages.get(stateMessages.size() - 1)));
    final AutoCloseableIterator<AirbyteMessage> secondBatchIterator = source()
        .read(config(), getConfiguredCatalog(), stateAfterFirstSync);
    final List<AirbyteMessage> dataFromSecondBatch = AutoCloseableIterators
        .toListAndClose(secondBatchIterator);
    assertEquals(recordsToCreate, extractRecordMessages(dataFromSecondBatch).size());
    final List<AirbyteStateMessage> stateMessagesCDC = extractStateMessages(dataFromSecondBatch);
    assertTrue(stateMessagesCDC.size() > 1, "Generated only the final state.");
    assertEquals(stateMessagesCDC.size(), stateMessagesCDC.stream().distinct().count(), "There are duplicated states.");
  }

  @Override
  protected void assertExpectedStateMessages(final List<? extends AirbyteStateMessage> stateMessages) {
    assertEquals(7, stateMessages.size());
    assertStateTypes(stateMessages, 4, supportResumableFullRefresh());
  }

  @Override
  protected void assertExpectedStateMessagesForFullRefresh(final List<? extends AirbyteStateMessage> stateMessages) {
    // Full refresh will only send 6 state messages - one for each record (including the final one).
    assertEquals(6, stateMessages.size());
  }

  protected void assertExpectedStateMessagesWithTotalCount(final List<AirbyteStateMessage> stateMessages, final long totalRecordCount) {
    long actualRecordCount = 0L;
    for (final AirbyteStateMessage message : stateMessages) {
      actualRecordCount += message.getSourceStats().getRecordCount();
    }
    assertEquals(actualRecordCount, totalRecordCount);
  }

  @Override
  protected void assertExpectedStateMessagesFromIncrementalSync(final List<? extends AirbyteStateMessage> stateMessages) {
    assertEquals(1, stateMessages.size());
    assertNotNull(stateMessages.get(0).getData());
    for (final AirbyteStateMessage stateMessage : stateMessages) {
      assertNotNull(stateMessage.getData().get("cdc_state").get("state").get(MYSQL_CDC_OFFSET));
      assertNotNull(stateMessage.getData().get("cdc_state").get("state").get(MYSQL_DB_HISTORY));
    }
  }

  private void assertStateForSyncShouldHandlePurgedLogsGracefully(final List<AirbyteStateMessage> stateMessages, final int syncNumber) {
    if (syncNumber == 1) {
      assertExpectedStateMessagesForRecordsProducedDuringAndAfterSync(stateMessages);
    } else if (syncNumber == 2) {
      // Sync number 2 uses the state from sync number 1 but before we trigger the sync 2 we purge the
      // binary logs and as a result the validation of
      // logs present on the server fails, and we trigger a sync from scratch
      assertEquals(47, stateMessages.size());
      assertStateTypes(stateMessages, 44);
    } else {
      throw new RuntimeException("Unknown sync number");
    }

  }

  @Override
  protected void assertExpectedStateMessagesForRecordsProducedDuringAndAfterSync(final List<? extends AirbyteStateMessage> stateAfterFirstBatch) {
    assertEquals(27, stateAfterFirstBatch.size());
    assertStateTypes(stateAfterFirstBatch, 24);
  }

  @Override
  protected void assertExpectedStateMessagesForNoData(final List<? extends AirbyteStateMessage> stateMessages) {
    assertEquals(2, stateMessages.size());
  }

  @Override
  protected void validateStreamStateInResumableFullRefresh(final JsonNode streamStateToBeTested) {
    // Pk should be pointing to the last element from MODEL_RECORDS table.
    assertEquals("16", streamStateToBeTested.get("pk_val").asText());
    assertEquals("id", streamStateToBeTested.get("pk_name").asText());
    assertEquals("primary_key", streamStateToBeTested.get("state_type").asText());
  }

  private void assertStateTypes(final List<? extends AirbyteStateMessage> stateMessages, final int indexTillWhichExpectPkState) {
    assertStateTypes(stateMessages, indexTillWhichExpectPkState, false);
  }

  private void assertStateTypes(final List<? extends AirbyteStateMessage> stateMessages,
                                final int indexTillWhichExpectPkState,
                                boolean expectSharedStateChange) {
    JsonNode sharedState = null;

    for (int i = 0; i < stateMessages.size(); i++) {
      final AirbyteStateMessage stateMessage = stateMessages.get(i);
      assertEquals(AirbyteStateType.GLOBAL, stateMessage.getType());
      final AirbyteGlobalState global = stateMessage.getGlobal();
      assertNotNull(global.getSharedState());
      if (Objects.isNull(sharedState)) {
        sharedState = global.getSharedState();
      } else if (expectSharedStateChange && i == indexTillWhichExpectPkState) {
        sharedState = global.getSharedState();
      } else if (i != stateMessages.size() - 1) {
        assertEquals(sharedState, global.getSharedState());
      }
      assertEquals(1, global.getStreamStates().size());
      final AirbyteStreamState streamState = global.getStreamStates().get(0);
      if (i <= indexTillWhichExpectPkState) {
        assertTrue(streamState.getStreamState().has(STATE_TYPE_KEY));
        assertEquals(PRIMARY_KEY_STATE_TYPE, streamState.getStreamState().get(STATE_TYPE_KEY).asText());
      } else {
        assertFalse(streamState.getStreamState().has(STATE_TYPE_KEY));
      }
    }
  }

  @Override
  protected void assertStateMessagesForNewTableSnapshotTest(final List<? extends AirbyteStateMessage> stateMessages,
                                                            final AirbyteStateMessage stateMessageEmittedAfterFirstSyncCompletion) {

    // First message emitted in the WASS case is a CDC state message. This should have a different
    // global state (LSN) as compared to the previous
    // finishing state. The streams in snapshot phase should be the one that is completed at that point.
    assertEquals(7, stateMessages.size());
    final AirbyteStateMessage cdcStateMessage = stateMessages.get(0);
    assertNotEquals(stateMessageEmittedAfterFirstSyncCompletion.getGlobal().getSharedState(), cdcStateMessage.getGlobal().getSharedState());
    Set<StreamDescriptor> streamsInSnapshotState = cdcStateMessage.getGlobal().getStreamStates()
        .stream()
        .map(AirbyteStreamState::getStreamDescriptor)
        .collect(Collectors.toSet());
    assertEquals(1, streamsInSnapshotState.size());
    assertTrue(streamsInSnapshotState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(getDatabaseName())));

    for (int i = 1; i <= 5; i++) {
      final AirbyteStateMessage stateMessage = stateMessages.get(i);
      assertEquals(AirbyteStateType.GLOBAL, stateMessage.getType());
      // Shared state should not be the same as the first (CDC) state message as it should not change in
      // initial sync.
      assertEquals(cdcStateMessage.getGlobal().getSharedState(), stateMessage.getGlobal().getSharedState());
      streamsInSnapshotState.clear();
      streamsInSnapshotState = stateMessage.getGlobal().getStreamStates()
          .stream()
          .map(AirbyteStreamState::getStreamDescriptor)
          .collect(Collectors.toSet());
      assertEquals(2, streamsInSnapshotState.size());
      assertTrue(
          streamsInSnapshotState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME + "_random").withNamespace(randomSchema())));
      assertTrue(streamsInSnapshotState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(getDatabaseName())));

      stateMessage.getGlobal().getStreamStates().forEach(s -> {
        final JsonNode streamState = s.getStreamState();
        if (s.getStreamDescriptor().equals(new StreamDescriptor().withName(MODELS_STREAM_NAME + "_random").withNamespace(randomSchema()))) {
          assertEquals(PRIMARY_KEY_STATE_TYPE, streamState.get(STATE_TYPE_KEY).asText());
        } else if (s.getStreamDescriptor().equals(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(getDatabaseName()))) {
          assertFalse(streamState.has(STATE_TYPE_KEY));
        } else {
          throw new RuntimeException("Unknown stream");
        }
      });
    }

    // The last message emitted should indicate that initial PK load has finished for both streams.
    final AirbyteStateMessage stateMessageEmittedAfterSecondSyncCompletion = stateMessages.get(6);
    assertEquals(AirbyteStateType.GLOBAL, stateMessageEmittedAfterSecondSyncCompletion.getType());
    assertEquals(cdcStateMessage.getGlobal().getSharedState(),
        stateMessageEmittedAfterSecondSyncCompletion.getGlobal().getSharedState());
    streamsInSnapshotState.clear();
    streamsInSnapshotState = stateMessageEmittedAfterSecondSyncCompletion.getGlobal().getStreamStates()
        .stream()
        .map(AirbyteStreamState::getStreamDescriptor)
        .collect(Collectors.toSet());
    assertEquals(2, streamsInSnapshotState.size());
    assertTrue(
        streamsInSnapshotState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME + "_random").withNamespace(randomSchema())));
    assertTrue(streamsInSnapshotState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(getDatabaseName())));
    stateMessageEmittedAfterSecondSyncCompletion.getGlobal().getStreamStates().forEach(s -> {
      final JsonNode streamState = s.getStreamState();
      assertFalse(streamState.has(STATE_TYPE_KEY));
    });
  }

  @Test
  @Timeout(value = 60)
  public void syncWouldWorkWithDBWithInvalidTimezone() throws Exception {
    final String systemTimeZone = "@@system_time_zone";
    final JdbcDatabase jdbcDatabase = source().createDatabase(config());
    final Properties properties = MySqlCdcProperties.getDebeziumProperties(jdbcDatabase);
    final String databaseTimezone = jdbcDatabase.unsafeQuery(String.format("SELECT %s;", systemTimeZone)).toList().get(0).get(systemTimeZone)
        .asText();
    final String debeziumEngineTimezone = properties.getProperty("database.connectionTimeZone");

    assertEquals(INVALID_TIMEZONE_CEST, databaseTimezone);
    assertEquals("America/Los_Angeles", debeziumEngineTimezone);

    final AutoCloseableIterator<AirbyteMessage> read = source()
        .read(config(), getConfiguredCatalog(), null);

    final List<AirbyteMessage> actualRecords = AutoCloseableIterators.toListAndClose(read);

    final Set<AirbyteRecordMessage> recordMessages = extractRecordMessages(actualRecords);
    final List<AirbyteStateMessage> stateMessages = extractStateMessages(actualRecords);

    assertExpectedRecords(new HashSet<>(MODEL_RECORDS), recordMessages);
    assertExpectedStateMessages(stateMessages);
    assertExpectedStateMessagesWithTotalCount(stateMessages, 6);
  }

  @Test
  public void testCompositeIndexInitialLoad() throws Exception {
    // Simulate adding a composite index by modifying the catalog.
    final ConfiguredAirbyteCatalog configuredCatalog = Jsons.clone(getConfiguredCatalog());
    final List<List<String>> primaryKeys = configuredCatalog.getStreams().get(0).getStream().getSourceDefinedPrimaryKey();
    primaryKeys.add(List.of("make_id"));

    final AutoCloseableIterator<AirbyteMessage> read1 = source()
        .read(config(), configuredCatalog, null);

    final List<AirbyteMessage> actualRecords1 = AutoCloseableIterators.toListAndClose(read1);

    final Set<AirbyteRecordMessage> recordMessages1 = extractRecordMessages(actualRecords1);
    final List<AirbyteStateMessage> stateMessages1 = extractStateMessages(actualRecords1);
    assertExpectedRecords(new HashSet<>(MODEL_RECORDS), recordMessages1);
    assertExpectedStateMessages(stateMessages1);
    assertExpectedStateMessagesWithTotalCount(stateMessages1, 6);

    // Re-run the sync with state associated with record w/ id = 15 (second to last record).
    // We expect to read 2 records, since in the case of a composite PK we issue a >= query.
    // We also expect 3 state records. One associated with the pk state, one to signify end of initial
    // load, and
    // the last one indicating the cdc position we have synced until.
    final JsonNode state = Jsons.jsonNode(Collections.singletonList(stateMessages1.get(4)));
    final AutoCloseableIterator<AirbyteMessage> read2 = source()
        .read(config(), configuredCatalog, state);

    final List<AirbyteMessage> actualRecords2 = AutoCloseableIterators.toListAndClose(read2);
    final Set<AirbyteRecordMessage> recordMessages2 = extractRecordMessages(actualRecords2);
    final List<AirbyteStateMessage> stateMessages2 = extractStateMessages(actualRecords2);

    assertExpectedRecords(new HashSet<>(MODEL_RECORDS.subList(4, 6)), recordMessages2);
    assertEquals(3, stateMessages2.size());
    // In the second sync (WASS case), the first state message is emitted via debezium use case, which
    // should still have the pk state encoded within. The second state message emitted will contain
    // state from the initial
    // sync and the last (3rd) state message will not have any pk state as the initial sync can now be
    // considered complete.
    assertStateTypes(stateMessages2, 1);
  }

  // Remove all timestamp related fields in shared state. We want to make sure other information will
  // not change.
  private void pruneSharedStateTimestamp(final JsonNode rootNode) throws Exception {
    ObjectMapper mapper = new ObjectMapper();

    // Navigate to the specific node
    JsonNode historyNode = rootNode.path("state").path("mysql_db_history");
    if (historyNode.isMissingNode()) {
      return; // Node not found, nothing to do
    }
    String historyJson = historyNode.asText();
    JsonNode historyJsonNode = mapper.readTree(historyJson);

    ObjectNode objectNode = (ObjectNode) historyJsonNode;
    objectNode.remove("ts_ms");

    if (objectNode.has("position") && objectNode.get("position").has("ts_sec")) {
      ((ObjectNode) objectNode.get("position")).remove("ts_sec");
    }

    JsonNode offsetNode = rootNode.path("state").path("mysql_cdc_offset");
    JsonNode offsetJsonNode = mapper.readTree(offsetNode.asText());
    if (offsetJsonNode.has("ts_sec")) {
      ((ObjectNode) offsetJsonNode).remove("ts_sec");
    }

    // Replace the original string with the modified one
    ((ObjectNode) rootNode.path("state")).put("mysql_db_history", mapper.writeValueAsString(historyJsonNode));
    ((ObjectNode) rootNode.path("state")).put("mysql_cdc_offset", mapper.writeValueAsString(offsetJsonNode));
  }

  @Test
  public void testTwoStreamSync() throws Exception {
    // Add another stream models_2 and read that one as well.
    final ConfiguredAirbyteCatalog configuredCatalog = Jsons.clone(getConfiguredCatalog());

    final List<JsonNode> MODEL_RECORDS_2 = ImmutableList.of(
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 110, COL_MAKE_ID, 1, COL_MODEL, "Fiesta-2")),
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 120, COL_MAKE_ID, 1, COL_MODEL, "Focus-2")),
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 130, COL_MAKE_ID, 1, COL_MODEL, "Ranger-2")),
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 140, COL_MAKE_ID, 2, COL_MODEL, "GLA-2")),
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 150, COL_MAKE_ID, 2, COL_MODEL, "A 220-2")),
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 160, COL_MAKE_ID, 2, COL_MODEL, "E 350-2")));

    testdb.with(createTableSqlFmt(), getDatabaseName(), MODELS_STREAM_NAME + "_2",
        columnClause(ImmutableMap.of(COL_ID, "INTEGER", COL_MAKE_ID, "INTEGER", COL_MODEL, "VARCHAR(200)"), Optional.of(COL_ID)));

    for (final JsonNode recordJson : MODEL_RECORDS_2) {
      writeRecords(recordJson, getDatabaseName(), MODELS_STREAM_NAME + "_2", COL_ID,
          COL_MAKE_ID, COL_MODEL);
    }

    final ConfiguredAirbyteStream airbyteStream = new ConfiguredAirbyteStream()
        .withStream(CatalogHelpers.createAirbyteStream(
            MODELS_STREAM_NAME + "_2",
            getDatabaseName(),
            Field.of(COL_ID, JsonSchemaType.INTEGER),
            Field.of(COL_MAKE_ID, JsonSchemaType.INTEGER),
            Field.of(COL_MODEL, JsonSchemaType.STRING))
            .withSupportedSyncModes(
                Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID))));
    airbyteStream.setSyncMode(SyncMode.INCREMENTAL);

    final List<ConfiguredAirbyteStream> streams = configuredCatalog.getStreams();
    streams.add(airbyteStream);
    configuredCatalog.withStreams(streams);

    final AutoCloseableIterator<AirbyteMessage> read1 = source()
        .read(config(), configuredCatalog, null);
    final List<AirbyteMessage> actualRecords1 = AutoCloseableIterators.toListAndClose(read1);

    final Set<AirbyteRecordMessage> recordMessages1 = extractRecordMessages(actualRecords1);
    final List<AirbyteStateMessage> stateMessages1 = extractStateMessages(actualRecords1);
    assertEquals(13, stateMessages1.size());
    assertExpectedStateMessagesWithTotalCount(stateMessages1, 12);

    JsonNode sharedState = null;
    StreamDescriptor firstStreamInState = null;
    for (int i = 0; i < stateMessages1.size(); i++) {
      final AirbyteStateMessage stateMessage = stateMessages1.get(i);
      assertEquals(AirbyteStateType.GLOBAL, stateMessage.getType());
      final AirbyteGlobalState global = stateMessage.getGlobal();
      assertNotNull(global.getSharedState());
      if (Objects.isNull(sharedState)) {
        ObjectMapper mapper = new ObjectMapper();
        sharedState = mapper.valueToTree(global.getSharedState());
        pruneSharedStateTimestamp(sharedState);
      } else {
        ObjectMapper mapper = new ObjectMapper();
        var newSharedState = mapper.valueToTree(global.getSharedState());
        pruneSharedStateTimestamp(newSharedState);
        assertEquals(sharedState, newSharedState);
      }

      if (Objects.isNull(firstStreamInState)) {
        assertEquals(1, global.getStreamStates().size());
        firstStreamInState = global.getStreamStates().get(0).getStreamDescriptor();
      }

      if (i <= 4) {
        // First 4 state messages are pk state
        assertEquals(1, global.getStreamStates().size());
        final AirbyteStreamState streamState = global.getStreamStates().get(0);
        assertTrue(streamState.getStreamState().has(STATE_TYPE_KEY));
        assertEquals(PRIMARY_KEY_STATE_TYPE, streamState.getStreamState().get(STATE_TYPE_KEY).asText());
      } else if (i == 5) {
        // 5th state message is the final state message emitted for the stream
        assertEquals(1, global.getStreamStates().size());
        final AirbyteStreamState streamState = global.getStreamStates().get(0);
        assertFalse(streamState.getStreamState().has(STATE_TYPE_KEY));
      } else if (i <= 10) {
        // 6th to 10th is the primary_key state message for the 2nd stream but final state message for 1st
        // stream
        assertEquals(2, global.getStreamStates().size());
        final StreamDescriptor finalFirstStreamInState = firstStreamInState;
        global.getStreamStates().forEach(c -> {
          if (c.getStreamDescriptor().equals(finalFirstStreamInState)) {
            assertFalse(c.getStreamState().has(STATE_TYPE_KEY));
          } else {
            assertTrue(c.getStreamState().has(STATE_TYPE_KEY));
            assertEquals(PRIMARY_KEY_STATE_TYPE, c.getStreamState().get(STATE_TYPE_KEY).asText());
          }
        });
      } else {
        // last 2 state messages don't contain primary_key info cause primary_key sync should be complete
        assertEquals(2, global.getStreamStates().size());
        global.getStreamStates().forEach(c -> assertFalse(c.getStreamState().has(STATE_TYPE_KEY)));
      }
    }

    final Set<String> names = new HashSet<>(STREAM_NAMES);
    names.add(MODELS_STREAM_NAME + "_2");
    assertExpectedRecords(Streams.concat(MODEL_RECORDS_2.stream(), MODEL_RECORDS.stream())
        .collect(Collectors.toSet()),
        recordMessages1,
        names,
        names,
        getDatabaseName());

    assertEquals(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(getDatabaseName()), firstStreamInState);

    // Triggering a sync with a primary_key state for 1 stream and complete state for other stream
    final AutoCloseableIterator<AirbyteMessage> read2 = source()
        .read(config(), configuredCatalog, Jsons.jsonNode(Collections.singletonList(stateMessages1.get(6))));
    final List<AirbyteMessage> actualRecords2 = AutoCloseableIterators.toListAndClose(read2);

    final List<AirbyteStateMessage> stateMessages2 = extractStateMessages(actualRecords2);

    assertEquals(6, stateMessages2.size());
    // State was reset to the 7th; thus 5 remaining records were expected to be reloaded.
    assertExpectedStateMessagesWithTotalCount(stateMessages2, 5);
    for (int i = 0; i < stateMessages2.size(); i++) {
      final AirbyteStateMessage stateMessage = stateMessages2.get(i);
      assertEquals(AirbyteStateType.GLOBAL, stateMessage.getType());
      final AirbyteGlobalState global = stateMessage.getGlobal();
      assertNotNull(global.getSharedState());
      assertEquals(2, global.getStreamStates().size());

      if (i <= 4) {
        final StreamDescriptor finalFirstStreamInState = firstStreamInState;
        global.getStreamStates().forEach(c -> {
          // First 5 state messages are primary_key state for the stream that didn't complete primary_key sync
          // the first time
          if (c.getStreamDescriptor().equals(finalFirstStreamInState)) {
            assertFalse(c.getStreamState().has(STATE_TYPE_KEY));
          } else {
            assertTrue(c.getStreamState().has(STATE_TYPE_KEY));
            assertEquals(PRIMARY_KEY_STATE_TYPE, c.getStreamState().get(STATE_TYPE_KEY).asText());
          }
        });
      } else {
        // last state messages doesn't contain primary_key info cause primary_key sync should be complete
        global.getStreamStates().forEach(c -> assertFalse(c.getStreamState().has(STATE_TYPE_KEY)));
      }
    }

    final Set<AirbyteRecordMessage> recordMessages2 = extractRecordMessages(actualRecords2);
    assertEquals(5, recordMessages2.size());
    assertExpectedRecords(new HashSet<>(MODEL_RECORDS_2.subList(1, MODEL_RECORDS_2.size())),
        recordMessages2,
        names,
        names,
        getDatabaseName());
  }

  /**
   * This test creates lots of tables increasing the schema history size above the limit of forcing
   * the {@link AirbyteSchemaHistoryStorage#read()} method to compress the schema history blob as part
   * of the state message which allows us to test that the next sync is able to work fine when
   * provided with a compressed blob in the state.
   */
  @Test
  @Timeout(value = 120)
  public void testCompressedSchemaHistory() throws Exception {
    createTablesToIncreaseSchemaHistorySize();
    final AutoCloseableIterator<AirbyteMessage> firstBatchIterator = source()
        .read(config(), getConfiguredCatalog(), null);
    final List<AirbyteMessage> dataFromFirstBatch = AutoCloseableIterators
        .toListAndClose(firstBatchIterator);
    final AirbyteStateMessage lastStateMessageFromFirstBatch = Iterables.getLast(extractStateMessages(dataFromFirstBatch));
    assertNotNull(lastStateMessageFromFirstBatch.getGlobal().getSharedState());
    assertNotNull(lastStateMessageFromFirstBatch.getGlobal().getSharedState().get("state"));
    assertNotNull(lastStateMessageFromFirstBatch.getGlobal().getSharedState().get("state").get(IS_COMPRESSED));
    assertNotNull(lastStateMessageFromFirstBatch.getGlobal().getSharedState().get("state").get(MYSQL_DB_HISTORY));
    assertNotNull(lastStateMessageFromFirstBatch.getGlobal().getSharedState().get("state").get(MYSQL_CDC_OFFSET));
    assertTrue(lastStateMessageFromFirstBatch.getGlobal().getSharedState().get("state").get(IS_COMPRESSED).asBoolean());

    // INSERT records so that events are written to binlog and Debezium tries to parse them
    final int recordsToCreate = 20;
    // first batch of records. 20 created here and 6 created in setup method.
    for (int recordsCreated = 0; recordsCreated < recordsToCreate; recordsCreated++) {
      final JsonNode record =
          Jsons.jsonNode(ImmutableMap
              .of(COL_ID, 100 + recordsCreated, COL_MAKE_ID, 1, COL_MODEL,
                  "F-" + recordsCreated));
      writeModelRecord(record);
    }

    final AutoCloseableIterator<AirbyteMessage> secondBatchIterator = source()
        .read(config(), getConfiguredCatalog(), Jsons.jsonNode(Collections.singletonList(lastStateMessageFromFirstBatch)));
    final List<AirbyteMessage> dataFromSecondBatch = AutoCloseableIterators
        .toListAndClose(secondBatchIterator);
    final AirbyteStateMessage lastStateMessageFromSecondBatch = Iterables.getLast(extractStateMessages(dataFromSecondBatch));
    assertNotNull(lastStateMessageFromSecondBatch.getGlobal().getSharedState());
    assertNotNull(lastStateMessageFromSecondBatch.getGlobal().getSharedState().get("state"));
    assertNotNull(lastStateMessageFromSecondBatch.getGlobal().getSharedState().get("state").get(IS_COMPRESSED));
    assertNotNull(lastStateMessageFromSecondBatch.getGlobal().getSharedState().get("state").get(MYSQL_DB_HISTORY));
    assertNotNull(lastStateMessageFromSecondBatch.getGlobal().getSharedState().get("state").get(MYSQL_CDC_OFFSET));
    assertTrue(lastStateMessageFromSecondBatch.getGlobal().getSharedState().get("state").get(IS_COMPRESSED).asBoolean());

    assertEquals(lastStateMessageFromFirstBatch.getGlobal().getSharedState().get("state").get(MYSQL_DB_HISTORY),
        lastStateMessageFromSecondBatch.getGlobal().getSharedState().get("state").get(MYSQL_DB_HISTORY));

    assertEquals(recordsToCreate, extractRecordMessages(dataFromSecondBatch).size());
  }

  private void writeDateRecords(
                                final JsonNode recordJson,
                                final String dbName,
                                final String streamName,
                                final String idCol,
                                final String dateCol) {
    testdb.with("INSERT INTO `%s` .`%s` (%s, %s) VALUES (%s, %s);", dbName, streamName,
        idCol, dateCol,
        recordJson.get(idCol).asInt(), recordJson.get(dateCol).asText());
  }

  @Test
  public void testInvalidDatetime_metaChangesPopulated() throws Exception {
    final ConfiguredAirbyteCatalog configuredCatalog = Jsons.clone(getConfiguredCatalog());

    // Add a datetime stream to the catalog
    testdb
        .withoutStrictMode()
        .with(createTableSqlFmt(), getDatabaseName(), TEST_DATE_STREAM_NAME,
            columnClause(ImmutableMap.of(COL_ID, "INTEGER", COL_DATE_TIME, "DATETIME"), Optional.of(COL_ID)));

    for (final JsonNode recordJson : DATE_TIME_RECORDS) {
      writeDateRecords(recordJson, getDatabaseName(), TEST_DATE_STREAM_NAME, COL_ID, COL_DATE_TIME);
    }

    final ConfiguredAirbyteStream airbyteStream = new ConfiguredAirbyteStream()
        .withStream(CatalogHelpers.createAirbyteStream(
            TEST_DATE_STREAM_NAME,
            getDatabaseName(),
            Field.of(COL_ID, JsonSchemaType.INTEGER),
            Field.of(COL_DATE_TIME, JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE))
            .withSupportedSyncModes(
                Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID))));
    airbyteStream.setSyncMode(SyncMode.INCREMENTAL);

    final List<ConfiguredAirbyteStream> streams = new ArrayList<>();
    streams.add(airbyteStream);
    configuredCatalog.withStreams(streams);

    final AutoCloseableIterator<AirbyteMessage> read1 = source()
        .read(config(), configuredCatalog, null);
    final List<AirbyteMessage> actualRecords = AutoCloseableIterators.toListAndClose(read1);

    // Sync is expected to succeed with one record. However, the meta changes column should be populated
    // for this record
    // as it is an invalid date. As a result, this field will be omitted as Airbyte is unable to
    // serialize the source value.
    final Set<AirbyteRecordMessage> recordMessages = extractRecordMessages(actualRecords);
    assertEquals(recordMessages.size(), 1);
    final AirbyteRecordMessage invalidDateRecord = recordMessages.stream().findFirst().get();

    final AirbyteRecordMessageMetaChange expectedChange =
        new AirbyteRecordMessageMetaChange().withReason(Reason.SOURCE_SERIALIZATION_ERROR).withChange(
            Change.NULLED).withField(COL_DATE_TIME);
    final AirbyteRecordMessageMeta expectedMessageMeta = new AirbyteRecordMessageMeta().withChanges(List.of(expectedChange));
    assertEquals(expectedMessageMeta, invalidDateRecord.getMeta());

    ObjectMapper mapper = new ObjectMapper();
    final JsonNode expectedDataWithoutCdcFields = mapper.readTree("{\"id\":120, \"CAR_DATE\":null}");
    removeCDCColumns((ObjectNode) invalidDateRecord.getData());
    assertEquals(expectedDataWithoutCdcFields, invalidDateRecord.getData());
  }

  private void createTablesToIncreaseSchemaHistorySize() {
    for (int i = 0; i <= 200; i++) {
      final String tableName = generateRandomStringOf32Characters();
      final StringBuilder createTableQuery = new StringBuilder("CREATE TABLE " + tableName + "(");
      String firstCol = null;
      for (int j = 1; j <= 250; j++) {
        final String columnName = generateRandomStringOf32Characters();
        if (j == 1) {
          firstCol = columnName;

        }
        createTableQuery.append(columnName).append(" INTEGER, ");
      }
      createTableQuery.append("PRIMARY KEY (").append(firstCol).append("));");
      testdb.with(createTableQuery.toString());
    }
  }

  private static String generateRandomStringOf32Characters() {
    final String characters = "abcdefghijklmnopqrstuvwxyz";
    final int length = 32;

    final StringBuilder randomString = new StringBuilder(length);

    for (int i = 0; i < length; i++) {
      final int index = RANDOM.nextInt(characters.length());
      final char randomChar = characters.charAt(index);
      randomString.append(randomChar);
    }

    return randomString.toString();
  }

}
