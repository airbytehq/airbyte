/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS_PROPERTY;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventUtils.CDC_DELETED_AT;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventUtils.CDC_UPDATED_AT;
import static io.airbyte.cdk.integrations.debezium.internals.mysql.MysqlCdcStateConstants.IS_COMPRESSED;
import static io.airbyte.cdk.integrations.debezium.internals.mysql.MysqlCdcStateConstants.MYSQL_CDC_OFFSET;
import static io.airbyte.cdk.integrations.debezium.internals.mysql.MysqlCdcStateConstants.MYSQL_DB_HISTORY;
import static io.airbyte.integrations.source.mysql.MySqlSource.CDC_DEFAULT_CURSOR;
import static io.airbyte.integrations.source.mysql.MySqlSource.CDC_LOG_FILE;
import static io.airbyte.integrations.source.mysql.MySqlSource.CDC_LOG_POS;
import static io.airbyte.integrations.source.mysql.MySqlSource.DRIVER_CLASS;
import static io.airbyte.integrations.source.mysql.initialsync.MySqlInitialLoadStateManager.PRIMARY_KEY_STATE_TYPE;
import static io.airbyte.integrations.source.mysql.initialsync.MySqlInitialLoadStateManager.STATE_TYPE_KEY;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Iterables;
import com.google.common.collect.Lists;
import com.google.common.collect.Streams;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.factory.DSLContextFactory;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.debezium.CdcSourceTest;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteSchemaHistoryStorage;
import io.airbyte.cdk.integrations.debezium.internals.mysql.MySqlCdcTargetPosition;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteGlobalState;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import io.airbyte.protocol.models.v0.SyncMode;
import java.sql.SQLException;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Properties;
import java.util.Random;
import java.util.Set;
import java.util.stream.Collectors;
import javax.sql.DataSource;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Tags;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;
import org.junit.jupiter.api.Timeout;
import org.junit.jupiter.api.extension.ExtendWith;
import org.testcontainers.containers.MySQLContainer;
import uk.org.webcompere.systemstubs.environment.EnvironmentVariables;
import uk.org.webcompere.systemstubs.jupiter.SystemStub;
import uk.org.webcompere.systemstubs.jupiter.SystemStubsExtension;

@ExtendWith(SystemStubsExtension.class)
public class CdcMysqlSourceTest extends CdcSourceTest {

  private static final String START_DB_CONTAINER_WITH_INVALID_TIMEZONE = "START-DB-CONTAINER-WITH-INVALID-TIMEZONE";
  private static final String INVALID_TIMEZONE_CEST = "CEST";

  @SystemStub
  private EnvironmentVariables environmentVariables;

  private static final String DB_NAME = MODELS_SCHEMA;
  private MySQLContainer<?> container;
  private Database database;
  private MySqlSource source;
  private JsonNode config;
  private static final Random RANDOM = new Random();

  @BeforeEach
  public void setup(final TestInfo testInfo) throws SQLException {
    environmentVariables.set(EnvVariableFeatureFlags.USE_STREAM_CAPABLE_STATE, "true");
    init(testInfo);
    revokeAllPermissions();
    grantCorrectPermissions();
    super.setup();
  }

  private void init(final TestInfo testInfo) {
    container = new MySQLContainer<>("mysql:8.0");
    if (testInfo.getTags().contains(START_DB_CONTAINER_WITH_INVALID_TIMEZONE)) {
      container.withEnv(Map.of("TZ", INVALID_TIMEZONE_CEST));
    }
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

    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "CDC")
        .put("initial_waiting_seconds", INITIAL_WAITING_SECONDS)
        .put("server_time_zone", "America/Los_Angeles")
        .build());

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("database", DB_NAME)
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .put("replication_method", replicationMethod)
        .put(SYNC_CHECKPOINT_RECORDS_PROPERTY, 1)
        .put("is_test", true)
        .build());
  }

  private void revokeAllPermissions() {
    executeQuery("REVOKE ALL PRIVILEGES, GRANT OPTION FROM " + container.getUsername() + "@'%';");
  }

  private void revokeReplicationClientPermission() {
    executeQuery("REVOKE REPLICATION CLIENT ON *.* FROM " + container.getUsername() + "@'%';");
  }

  private void grantCorrectPermissions() {
    executeQuery("GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO " + container.getUsername() + "@'%';");
  }

  protected void purgeAllBinaryLogs() {
    executeQuery("RESET MASTER;");
  }

  @AfterEach
  public void tearDown() {
    try {
      container.close();
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  protected MySqlCdcTargetPosition cdcLatestTargetPosition() {
    final DataSource dataSource = DataSourceFactory.create(
        "root",
        "test",
        DRIVER_CLASS,
        String.format("jdbc:mysql://%s:%s",
            container.getHost(),
            container.getFirstMappedPort()),
        Collections.emptyMap());
    return MySqlCdcTargetPosition.targetPosition(new DefaultJdbcDatabase(dataSource));
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
  protected String randomTableSchema() {
    return MODELS_SCHEMA;
  }

  @Test
  protected void syncWithReplicationClientPrivilegeRevokedFailsCheck() throws Exception {
    revokeReplicationClientPermission();
    final AirbyteConnectionStatus status = getSource().check(getConfig());
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

    final AutoCloseableIterator<AirbyteMessage> firstBatchIterator = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, null);
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
    final AutoCloseableIterator<AirbyteMessage> secondBatchIterator = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, state);
    final List<AirbyteMessage> dataFromSecondBatch = AutoCloseableIterators
        .toListAndClose(secondBatchIterator);

    final List<AirbyteStateMessage> stateAfterSecondBatch = extractStateMessages(dataFromSecondBatch);
    assertStateForSyncShouldHandlePurgedLogsGracefully(stateAfterSecondBatch, 2);

    final Set<AirbyteRecordMessage> recordsFromSecondBatch = extractRecordMessages(
        dataFromSecondBatch);
    assertEquals((recordsToCreate * 2) + recordsCreatedBeforeTestCount, recordsFromSecondBatch.size(),
        "Expected 46 records to be replicated in the second sync.");
  }

  /**
   * This test verifies that multiple states are sent during the CDC process based on number of
   * records. We can ensure that more than one `STATE` type of message is sent, but we are not able to
   * assert the exact number of messages sent as depends on Debezium.
   *
   * @throws Exception Exception happening in the test.
   */
  @Test
  protected void verifyCheckpointStatesByRecords() throws Exception {
    // We require a huge amount of records, otherwise Debezium will notify directly the last offset.
    final int recordsToCreate = 20000;

    final AutoCloseableIterator<AirbyteMessage> firstBatchIterator = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, null);
    final List<AirbyteMessage> dataFromFirstBatch = AutoCloseableIterators
        .toListAndClose(firstBatchIterator);
    final List<AirbyteStateMessage> stateMessages = extractStateMessages(dataFromFirstBatch);

    // As first `read` operation is from snapshot, it would generate only one state message at the end
    // of the process.
    assertExpectedStateMessages(stateMessages);

    for (int recordsCreated = 0; recordsCreated < recordsToCreate; recordsCreated++) {
      final JsonNode record =
          Jsons.jsonNode(ImmutableMap
              .of(COL_ID, 200 + recordsCreated, COL_MAKE_ID, 1, COL_MODEL,
                  "F-" + recordsCreated));
      writeModelRecord(record);
    }

    final JsonNode stateAfterFirstSync = Jsons.jsonNode(Collections.singletonList(stateMessages.get(stateMessages.size() - 1)));
    final AutoCloseableIterator<AirbyteMessage> secondBatchIterator = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, stateAfterFirstSync);
    final List<AirbyteMessage> dataFromSecondBatch = AutoCloseableIterators
        .toListAndClose(secondBatchIterator);
    assertEquals(recordsToCreate, extractRecordMessages(dataFromSecondBatch).size());
    final List<AirbyteStateMessage> stateMessagesCDC = extractStateMessages(dataFromSecondBatch);
    assertTrue(stateMessagesCDC.size() > 1, "Generated only the final state.");
    assertEquals(stateMessagesCDC.size(), stateMessagesCDC.stream().distinct().count(), "There are duplicated states.");
  }

  @Override
  protected void assertExpectedStateMessages(final List<AirbyteStateMessage> stateMessages) {
    assertEquals(7, stateMessages.size());
    assertStateTypes(stateMessages, 4);
  }

  @Override
  protected void assertExpectedStateMessagesFromIncrementalSync(final List<AirbyteStateMessage> stateMessages) {
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
  protected void assertExpectedStateMessagesForRecordsProducedDuringAndAfterSync(final List<AirbyteStateMessage> stateAfterFirstBatch) {
    assertEquals(27, stateAfterFirstBatch.size());
    assertStateTypes(stateAfterFirstBatch, 24);
  }

  @Override
  protected void assertExpectedStateMessagesForNoData(final List<AirbyteStateMessage> stateMessages) {
    assertEquals(2, stateMessages.size());
  }

  private void assertStateTypes(final List<AirbyteStateMessage> stateMessages, final int indexTillWhichExpectPkState) {
    JsonNode sharedState = null;
    for (int i = 0; i < stateMessages.size(); i++) {
      final AirbyteStateMessage stateMessage = stateMessages.get(i);
      assertEquals(AirbyteStateType.GLOBAL, stateMessage.getType());
      final AirbyteGlobalState global = stateMessage.getGlobal();
      assertNotNull(global.getSharedState());
      if (Objects.isNull(sharedState)) {
        sharedState = global.getSharedState();
      } else {
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
  protected void assertStateMessagesForNewTableSnapshotTest(final List<AirbyteStateMessage> stateMessages,
                                                            final AirbyteStateMessage stateMessageEmittedAfterFirstSyncCompletion) {
    assertEquals(7, stateMessages.size());
    for (int i = 0; i <= 4; i++) {
      final AirbyteStateMessage stateMessage = stateMessages.get(i);
      assertEquals(AirbyteStateMessage.AirbyteStateType.GLOBAL, stateMessage.getType());
      assertEquals(stateMessageEmittedAfterFirstSyncCompletion.getGlobal().getSharedState(),
          stateMessage.getGlobal().getSharedState());
      final Set<StreamDescriptor> streamsInSnapshotState = stateMessage.getGlobal().getStreamStates()
          .stream()
          .map(AirbyteStreamState::getStreamDescriptor)
          .collect(Collectors.toSet());
      assertEquals(2, streamsInSnapshotState.size());
      assertTrue(
          streamsInSnapshotState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME + "_random").withNamespace(randomTableSchema())));
      assertTrue(streamsInSnapshotState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(MODELS_SCHEMA)));

      stateMessage.getGlobal().getStreamStates().forEach(s -> {
        final JsonNode streamState = s.getStreamState();
        if (s.getStreamDescriptor().equals(new StreamDescriptor().withName(MODELS_STREAM_NAME + "_random").withNamespace(randomTableSchema()))) {
          assertEquals(PRIMARY_KEY_STATE_TYPE, streamState.get(STATE_TYPE_KEY).asText());
        } else if (s.getStreamDescriptor().equals(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(MODELS_SCHEMA))) {
          assertFalse(streamState.has(STATE_TYPE_KEY));
        } else {
          throw new RuntimeException("Unknown stream");
        }
      });
    }

    final AirbyteStateMessage secondLastSateMessage = stateMessages.get(5);
    assertEquals(AirbyteStateMessage.AirbyteStateType.GLOBAL, secondLastSateMessage.getType());
    assertEquals(stateMessageEmittedAfterFirstSyncCompletion.getGlobal().getSharedState(),
        secondLastSateMessage.getGlobal().getSharedState());
    final Set<StreamDescriptor> streamsInSnapshotState = secondLastSateMessage.getGlobal().getStreamStates()
        .stream()
        .map(AirbyteStreamState::getStreamDescriptor)
        .collect(Collectors.toSet());
    assertEquals(2, streamsInSnapshotState.size());
    assertTrue(
        streamsInSnapshotState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME + "_random").withNamespace(randomTableSchema())));
    assertTrue(streamsInSnapshotState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(MODELS_SCHEMA)));
    secondLastSateMessage.getGlobal().getStreamStates().forEach(s -> {
      final JsonNode streamState = s.getStreamState();
      assertFalse(streamState.has(STATE_TYPE_KEY));
    });

    final AirbyteStateMessage stateMessageEmittedAfterSecondSyncCompletion = stateMessages.get(6);
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
  }

  @Test
  @Timeout(value = 60)
  @Tags(value = {@Tag(START_DB_CONTAINER_WITH_INVALID_TIMEZONE)})
  public void syncWouldWorkWithDBWithInvalidTimezone() throws Exception {
    final String systemTimeZone = "@@system_time_zone";
    final JdbcDatabase jdbcDatabase = ((MySqlSource) getSource()).createDatabase(getConfig());
    final Properties properties = MySqlCdcProperties.getDebeziumProperties(jdbcDatabase);
    final String databaseTimezone = jdbcDatabase.unsafeQuery(String.format("SELECT %s;", systemTimeZone)).toList().get(0).get(systemTimeZone)
        .asText();
    final String debeziumEngineTimezone = properties.getProperty("database.connectionTimeZone");

    assertEquals(INVALID_TIMEZONE_CEST, databaseTimezone);
    assertEquals("America/Los_Angeles", debeziumEngineTimezone);

    final AutoCloseableIterator<AirbyteMessage> read = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, null);

    final List<AirbyteMessage> actualRecords = AutoCloseableIterators.toListAndClose(read);

    final Set<AirbyteRecordMessage> recordMessages = extractRecordMessages(actualRecords);
    final List<AirbyteStateMessage> stateMessages = extractStateMessages(actualRecords);

    assertExpectedRecords(new HashSet<>(MODEL_RECORDS), recordMessages);
    assertExpectedStateMessages(stateMessages);
  }

  @Test
  public void testCompositeIndexInitialLoad() throws Exception {
    // Simulate adding a composite index by modifying the catalog.
    final ConfiguredAirbyteCatalog configuredCatalog = Jsons.clone(CONFIGURED_CATALOG);
    final List<List<String>> primaryKeys = configuredCatalog.getStreams().get(0).getStream().getSourceDefinedPrimaryKey();
    primaryKeys.add(List.of("make_id"));

    final AutoCloseableIterator<AirbyteMessage> read1 = getSource()
        .read(getConfig(), configuredCatalog, null);

    final List<AirbyteMessage> actualRecords1 = AutoCloseableIterators.toListAndClose(read1);

    final Set<AirbyteRecordMessage> recordMessages1 = extractRecordMessages(actualRecords1);
    final List<AirbyteStateMessage> stateMessages1 = extractStateMessages(actualRecords1);
    assertExpectedRecords(new HashSet<>(MODEL_RECORDS), recordMessages1);
    assertExpectedStateMessages(stateMessages1);

    // Re-run the sync with state associated with record w/ id = 15 (second to last record).
    // We expect to read 2 records, since in the case of a composite PK we issue a >= query.
    // We also expect 3 state records. One associated with the pk state, one to signify end of initial
    // load, and
    // the last one indicating the cdc position we have synced until.
    final JsonNode state = Jsons.jsonNode(Collections.singletonList(stateMessages1.get(4)));
    final AutoCloseableIterator<AirbyteMessage> read2 = getSource()
        .read(getConfig(), configuredCatalog, state);

    final List<AirbyteMessage> actualRecords2 = AutoCloseableIterators.toListAndClose(read2);
    final Set<AirbyteRecordMessage> recordMessages2 = extractRecordMessages(actualRecords2);
    final List<AirbyteStateMessage> stateMessages2 = extractStateMessages(actualRecords2);

    assertExpectedRecords(new HashSet<>(MODEL_RECORDS.subList(4, 6)), recordMessages2);
    assertEquals(3, stateMessages2.size());
    assertStateTypes(stateMessages2, 0);
  }

  @Test
  public void testTwoStreamSync() throws Exception {
    // Add another stream models_2 and read that one as well.
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
    airbyteStream.setSyncMode(SyncMode.INCREMENTAL);

    final List<ConfiguredAirbyteStream> streams = configuredCatalog.getStreams();
    streams.add(airbyteStream);
    configuredCatalog.withStreams(streams);

    final AutoCloseableIterator<AirbyteMessage> read1 = getSource()
        .read(getConfig(), configuredCatalog, null);
    final List<AirbyteMessage> actualRecords1 = AutoCloseableIterators.toListAndClose(read1);

    final Set<AirbyteRecordMessage> recordMessages1 = extractRecordMessages(actualRecords1);
    final List<AirbyteStateMessage> stateMessages1 = extractStateMessages(actualRecords1);
    assertEquals(13, stateMessages1.size());
    JsonNode sharedState = null;
    StreamDescriptor firstStreamInState = null;
    for (int i = 0; i < stateMessages1.size(); i++) {
      final AirbyteStateMessage stateMessage = stateMessages1.get(i);
      assertEquals(AirbyteStateType.GLOBAL, stateMessage.getType());
      final AirbyteGlobalState global = stateMessage.getGlobal();
      assertNotNull(global.getSharedState());
      if (Objects.isNull(sharedState)) {
        sharedState = global.getSharedState();
      } else {
        assertEquals(sharedState, global.getSharedState());
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
        MODELS_SCHEMA);

    assertEquals(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(MODELS_SCHEMA), firstStreamInState);

    // Triggering a sync with a primary_key state for 1 stream and complete state for other stream
    final AutoCloseableIterator<AirbyteMessage> read2 = getSource()
        .read(getConfig(), configuredCatalog, Jsons.jsonNode(Collections.singletonList(stateMessages1.get(6))));
    final List<AirbyteMessage> actualRecords2 = AutoCloseableIterators.toListAndClose(read2);

    final List<AirbyteStateMessage> stateMessages2 = extractStateMessages(actualRecords2);

    assertEquals(6, stateMessages2.size());
    for (int i = 0; i < stateMessages2.size(); i++) {
      final AirbyteStateMessage stateMessage = stateMessages2.get(i);
      assertEquals(AirbyteStateType.GLOBAL, stateMessage.getType());
      final AirbyteGlobalState global = stateMessage.getGlobal();
      assertNotNull(global.getSharedState());
      assertEquals(2, global.getStreamStates().size());

      if (i <= 3) {
        final StreamDescriptor finalFirstStreamInState = firstStreamInState;
        global.getStreamStates().forEach(c -> {
          // First 4 state messages are primary_key state for the stream that didn't complete primary_key sync
          // the first time
          if (c.getStreamDescriptor().equals(finalFirstStreamInState)) {
            assertFalse(c.getStreamState().has(STATE_TYPE_KEY));
          } else {
            assertTrue(c.getStreamState().has(STATE_TYPE_KEY));
            assertEquals(PRIMARY_KEY_STATE_TYPE, c.getStreamState().get(STATE_TYPE_KEY).asText());
          }
        });
      } else {
        // last 2 state messages don't contain primary_key info cause primary_key sync should be complete
        global.getStreamStates().forEach(c -> assertFalse(c.getStreamState().has(STATE_TYPE_KEY)));
      }
    }

    final Set<AirbyteRecordMessage> recordMessages2 = extractRecordMessages(actualRecords2);
    assertEquals(5, recordMessages2.size());
    assertExpectedRecords(new HashSet<>(MODEL_RECORDS_2.subList(1, MODEL_RECORDS_2.size())),
        recordMessages2,
        names,
        names,
        MODELS_SCHEMA);
  }

  /**
   * This test creates lots of tables increasing the schema history size above the limit of
   * {@link AirbyteSchemaHistoryStorage#SIZE_LIMIT_TO_COMPRESS_MB} forcing the
   * {@link AirbyteSchemaHistoryStorage#read()} method to compress the schema history blob as part of
   * the state message which allows us to test that the next sync is able to work fine when provided
   * with a compressed blob in the state.
   */
  @Test
  public void testCompressedSchemaHistory() throws Exception {
    createTablesToIncreaseSchemaHistorySize();
    final AutoCloseableIterator<AirbyteMessage> firstBatchIterator = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, null);
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

    final AutoCloseableIterator<AirbyteMessage> secondBatchIterator = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, Jsons.jsonNode(Collections.singletonList(lastStateMessageFromFirstBatch)));
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

  private void createTablesToIncreaseSchemaHistorySize() {
    for (int i = 0; i <= 200; i++) {
      final String tableName = generateRandomStringOf32Characters();
      final StringBuilder createTableQuery = new StringBuilder("CREATE TABLE models_schema." + tableName + "(");
      String firstCol = null;
      for (int j = 1; j <= 250; j++) {
        final String columnName = generateRandomStringOf32Characters();
        if (j == 1) {
          firstCol = columnName;

        }
        createTableQuery.append(columnName).append(" INTEGER, ");
      }
      createTableQuery.append("PRIMARY KEY (").append(firstCol).append("));");
      executeQuery(createTableQuery.toString());
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
