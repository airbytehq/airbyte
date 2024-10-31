/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS_PROPERTY;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_DELETED_AT;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_UPDATED_AT;
import static io.airbyte.integrations.source.mssql.MssqlSource.CDC_DEFAULT_CURSOR;
import static io.airbyte.integrations.source.mssql.MssqlSource.CDC_EVENT_SERIAL_NO;
import static io.airbyte.integrations.source.mssql.MssqlSource.CDC_LSN;
import static io.airbyte.integrations.source.mssql.MssqlSource.MSSQL_CDC_OFFSET;
import static io.airbyte.integrations.source.mssql.MssqlSource.MSSQL_DB_HISTORY;
import static io.airbyte.integrations.source.mssql.initialsync.MssqlInitialLoadStateManager.ORDERED_COL_STATE_TYPE;
import static io.airbyte.integrations.source.mssql.initialsync.MssqlInitialLoadStateManager.STATE_TYPE_KEY;
import static org.awaitility.Awaitility.await;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Streams;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.db.jdbc.StreamingJdbcDatabase;
import io.airbyte.cdk.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.cdk.integrations.JdbcConnector;
import io.airbyte.cdk.integrations.debezium.CdcSourceTest;
import io.airbyte.cdk.integrations.debezium.CdcTargetPosition;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.BaseImage;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.ContainerModifier;
import io.airbyte.integrations.source.mssql.cdc.MssqlDebeziumStateUtil;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
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
import io.debezium.connector.sqlserver.Lsn;
import java.sql.SQLException;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;
import javax.sql.DataSource;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.TestInstance.Lifecycle;
import org.junit.jupiter.api.parallel.Execution;
import org.junit.jupiter.api.parallel.ExecutionMode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@TestInstance(Lifecycle.PER_METHOD)
@Execution(ExecutionMode.CONCURRENT)
@edu.umd.cs.findbugs.annotations.SuppressWarnings(value = "NP_NULL_ON_SOME_PATH")
public class CdcMssqlSourceTest extends CdcSourceTest<MssqlSource, MsSQLTestDatabase> {

  private static final Logger LOGGER = LoggerFactory.getLogger(CdcSourceTest.class);

  static private final String CDC_ROLE_NAME = "cdc_selector";

  static private final String TEST_USER_NAME_PREFIX = "cdc_test_user";

  private DataSource testDataSource;

  protected final String testUserName() {
    return testdb.withNamespace(TEST_USER_NAME_PREFIX);
  }

  @Override
  protected MsSQLTestDatabase createTestDatabase() {
    return MsSQLTestDatabase.in(BaseImage.MSSQL_2022, ContainerModifier.AGENT)
        .withWaitUntilAgentRunning()
        .withCdc();
  }

  @Override
  protected MssqlSource source() {
    return new MssqlSource();
  }

  @Override
  protected JsonNode config() {
    return testdb.configBuilder()
        .withHostAndPort()
        .withDatabase()
        .with(JdbcUtils.USERNAME_KEY, testUserName())
        .with(JdbcUtils.PASSWORD_KEY, testdb.getPassword())
        .withSchemas(modelsSchema(), randomSchema())
        .withCdcReplication()
        .withoutSsl()
        .with(SYNC_CHECKPOINT_RECORDS_PROPERTY, 1)
        .build();
  }

  @Override
  protected void assertExpectedStateMessageCountMatches(final List<? extends AirbyteStateMessage> stateMessages, long totalCount) {
    AtomicLong count = new AtomicLong(0L);
    stateMessages.stream().forEach(
        stateMessage -> count.addAndGet(stateMessage.getSourceStats() != null ? stateMessage.getSourceStats().getRecordCount().longValue() : 0L));
    assertEquals(totalCount, count.get());
  }

  @Override
  @BeforeEach
  protected void setup() {
    testdb = createTestDatabase();
    createTables();
    // Enables cdc on MODELS_SCHEMA.MODELS_STREAM_NAME, giving CDC_ROLE_NAME select access.
    testdb
        .withCdcForTable(modelsSchema(), MODELS_STREAM_NAME, CDC_ROLE_NAME)
        .withCdcForTable(randomSchema(), RANDOM_TABLE_NAME, CDC_ROLE_NAME);

    // Create a test user to be used by the source, with proper permissions.
    testdb
        .with("CREATE LOGIN %s WITH PASSWORD = '%s', DEFAULT_DATABASE = %s", testUserName(), testdb.getPassword(), testdb.getDatabaseName())
        .with("CREATE USER %s FOR LOGIN %s WITH DEFAULT_SCHEMA = [dbo]", testUserName(), testUserName())
        .with("REVOKE ALL FROM %s CASCADE;", testUserName())
        .with("EXEC sp_msforeachtable \"REVOKE ALL ON '?' TO %s;\"", testUserName())
        .with("GRANT SELECT ON SCHEMA :: [%s] TO %s", modelsSchema(), testUserName())
        .with("GRANT SELECT ON SCHEMA :: [%s] TO %s", randomSchema(), testUserName())
        .with("GRANT SELECT ON SCHEMA :: [cdc] TO %s", testUserName())
        .with("USE [master]")
        .with("GRANT VIEW SERVER STATE TO %s", testUserName())
        .with("USE [%s]", testdb.getDatabaseName())
        .with("EXEC sp_addrolemember N'%s', N'%s';", CDC_ROLE_NAME, testUserName());

    populateTables();
    waitForCdcRecords();
    testDataSource = createTestDataSource();
  }

  public void waitForCdcRecords() {
    testdb.waitForCdcRecords(modelsSchema(), MODELS_STREAM_NAME, MODEL_RECORDS.size());
    testdb.waitForCdcRecords(randomSchema(), RANDOM_TABLE_NAME, MODEL_RECORDS_RANDOM.size());

  }

  protected DataSource createTestDataSource() {
    return DataSourceFactory.create(
        testUserName(),
        testdb.getPassword(),
        testdb.getDatabaseDriver().getDriverClassName(),
        testdb.getJdbcUrl(),
        Map.of("encrypt", "false", "trustServerCertificate", "true"),
        JdbcConnector.CONNECT_TIMEOUT_DEFAULT);
  }

  @Override
  @AfterEach
  protected void tearDown() {
    try {
      DataSourceFactory.close(testDataSource);
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
    super.tearDown();
  }

  private JdbcDatabase testDatabase() {
    return new DefaultJdbcDatabase(testDataSource);
  }

  // TODO : Delete this Override when MSSQL supports individual table snapshot
  @Override
  public void newTableSnapshotTest() {
    // Do nothing
  }

  @Override
  protected void addIsResumableFlagForNonPkTable(final AirbyteStream stream) {
    stream.setIsResumable(false);
  }

  // Utilize the setup to do test on MssqlDebeziumStateUtil.
  @Test
  public void testCdcSnapshot() {

    JdbcDatabase testDatabase = testDatabase();
    testDatabase.setSourceConfig(config());
    testDatabase.setDatabaseConfig(source().toDatabaseConfig(config()));

    JsonNode debeziumState =
        MssqlDebeziumStateUtil.constructInitialDebeziumState(MssqlCdcHelper.getDebeziumProperties(testDatabase, getConfiguredCatalog(), true),
            getConfiguredCatalog(), testDatabase);

    Assertions.assertEquals(3, Jsons.object(debeziumState, Map.class).size());
    Assertions.assertTrue(debeziumState.has("is_compressed"));
    Assertions.assertFalse(debeziumState.get("is_compressed").asBoolean());
    Assertions.assertTrue(debeziumState.has("mssql_db_history"));
    Assertions.assertNotNull(debeziumState.get("mssql_db_history"));
    Assertions.assertTrue(debeziumState.has("mssql_cdc_offset"));
  }

  // Tests even with consistent inserting operations, CDC snapshot and incremental load will not lose
  // data.
  @Test
  @Timeout(value = 5,
           unit = TimeUnit.MINUTES)
  public void testCdcNotLoseDataWithConsistentWriting() throws Exception {
    ExecutorService executor = Executors.newFixedThreadPool(10);

    // Inserting 50 records in 10 seconds.
    // Intention is to insert records while we are running the first snapshot read. And we check with
    // the first snapshot read operations
    // and a following incremental read operation, we will be able to capture all data.
    int numberOfRecordsToInsert = 50;
    var insertingProcess = executor.submit(() -> {
      for (int i = 0; i < numberOfRecordsToInsert; i++) {
        testdb.with("INSERT INTO %s.%s (%s, %s, %s) VALUES (%s, %s, '%s');",
            modelsSchema(), MODELS_STREAM_NAME, COL_ID, COL_MAKE_ID, COL_MODEL, 910019 + i, i, "car description");
        try {
          Thread.sleep(200);
        } catch (InterruptedException e) {
          throw new RuntimeException(e);
        }
      }
    });

    final AutoCloseableIterator<AirbyteMessage> read1 = source()
        .read(config(), getConfiguredCatalog(), null);
    final List<AirbyteMessage> actualRecords1 = AutoCloseableIterators.toListAndClose(read1);
    final Set<AirbyteRecordMessage> recordMessages = extractRecordMessages(actualRecords1);
    final List<AirbyteStateMessage> stateMessagesFromFirstSync = extractStateMessages(actualRecords1);
    final JsonNode state = Jsons.jsonNode(Collections.singletonList(stateMessagesFromFirstSync.get(stateMessagesFromFirstSync.size() - 1)));
    // Make sure we have finished inserting process and read from previous state.
    insertingProcess.get();

    final AutoCloseableIterator<AirbyteMessage> read2 = source()
        .read(config(), getConfiguredCatalog(), state);
    final List<AirbyteMessage> actualRecords2 = AutoCloseableIterators.toListAndClose(read2);

    recordMessages.addAll(extractRecordMessages(actualRecords2));

    final Set<Integer> ids = recordMessages.stream().map(message -> message.getData().get("id").intValue()).collect(Collectors.toSet());
    // Originally in setup we have inserted 6 records in the table.
    assertEquals(ids.size(), numberOfRecordsToInsert + 6);
  }

  @Override
  protected String columnClause(final Map<String, String> columnsWithDataType, final Optional<String> primaryKey) {
    final StringBuilder columnClause = new StringBuilder();
    int i = 0;
    for (final Map.Entry<String, String> column : columnsWithDataType.entrySet()) {
      columnClause.append(column.getKey());
      columnClause.append(" ");
      columnClause.append(column.getValue());
      if (primaryKey.isPresent() && primaryKey.get().equals(column.getKey())) {
        columnClause.append(" PRIMARY KEY");
      }
      if (i < (columnsWithDataType.size() - 1)) {
        columnClause.append(",");
        columnClause.append(" ");
      }
      i++;
    }
    return columnClause.toString();
  }

  @Test
  void testAssertCdcEnabledInDb() {
    // since we enable cdc in setup, assert that we successfully pass this first
    assertDoesNotThrow(() -> source().assertCdcEnabledInDb(config(), testDatabase()));
    // then disable cdc and assert the check fails
    testdb.withoutCdc();
    assertThrows(RuntimeException.class, () -> source().assertCdcEnabledInDb(config(), testDatabase()));
  }

  @Test
  void testAssertCdcSchemaQueryable() {
    // correct access granted by setup so assert check passes
    assertDoesNotThrow(() -> source().assertCdcSchemaQueryable(config(), testDatabase()));
    // now revoke perms and assert that check fails
    testdb.with("REVOKE SELECT ON SCHEMA :: [cdc] TO %s", testUserName());
    assertThrows(com.microsoft.sqlserver.jdbc.SQLServerException.class,
        () -> source().assertCdcSchemaQueryable(config(), testDatabase()));
  }

  @Test
  void testCdcCheckOperationsWithDot() throws Exception {
    final String dbNameWithDot = testdb.getDatabaseName().replace("_", ".");
    testdb.with("CREATE DATABASE [%s];", dbNameWithDot)
        .with("USE [%s]", dbNameWithDot)
        .with("EXEC sys.sp_cdc_enable_db;");
    final AirbyteConnectionStatus status = source().check(config());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.SUCCEEDED);
  }

  // todo: check LSN returned is actually the max LSN
  // todo: check we fail as expected under certain conditions
  @Test
  void testGetTargetPosition() throws Exception {
    // check that getTargetPosition returns higher Lsn after inserting new row
    testdb.withWaitUntilMaxLsnAvailable();
    final Lsn firstLsn = MssqlCdcTargetPosition.getTargetPosition(testDatabase(), testdb.getDatabaseName()).targetLsn;
    testdb.with("INSERT INTO %s.%s (%s, %s, %s) VALUES (%s, %s, '%s');",
        modelsSchema(), MODELS_STREAM_NAME, COL_ID, COL_MAKE_ID, COL_MODEL, 910019, 1, "another car");
    // Wait for Agent capture job to log CDC change.
    await().atMost(Duration.ofSeconds(45)).until(() -> {
      final Lsn secondLsn = MssqlCdcTargetPosition.getTargetPosition(testDatabase(), testdb.getDatabaseName()).targetLsn;
      return secondLsn.compareTo(firstLsn) > 0;
    });
  }

  // Remove all timestamp related fields in shared state. We want to make sure other information will
  // not change.
  private void pruneSharedStateTimestamp(final JsonNode rootNode) throws Exception {
    ObjectMapper mapper = new ObjectMapper();

    // Navigate to the specific node
    JsonNode historyNode = rootNode.path("state").path("mssql_db_history");
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

    JsonNode offsetNode = rootNode.path("state").path("mssql_cdc_offset");
    JsonNode offsetJsonNode = mapper.readTree(offsetNode.asText());
    if (offsetJsonNode.has("ts_sec")) {
      ((ObjectNode) offsetJsonNode).remove("ts_sec");
    }

    // Replace the original string with the modified one
    ((ObjectNode) rootNode.path("state")).put("mssql_db_history", mapper.writeValueAsString(historyJsonNode));
    ((ObjectNode) rootNode.path("state")).put("mssql_cdc_offset", mapper.writeValueAsString(offsetJsonNode));
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

    testdb.with(createTableSqlFmt(), modelsSchema(), MODELS_STREAM_NAME + "_2",
        columnClause(ImmutableMap.of(COL_ID, "INTEGER", COL_MAKE_ID, "INTEGER", COL_MODEL, "VARCHAR(200)"), Optional.of(COL_ID)));

    for (final JsonNode recordJson : MODEL_RECORDS_2) {
      writeRecords(recordJson, modelsSchema(), MODELS_STREAM_NAME + "_2", COL_ID,
          COL_MAKE_ID, COL_MODEL);
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
        assertEquals(ORDERED_COL_STATE_TYPE, streamState.getStreamState().get(STATE_TYPE_KEY).asText());
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
            assertEquals(ORDERED_COL_STATE_TYPE, c.getStreamState().get(STATE_TYPE_KEY).asText());
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
        modelsSchema());

    assertEquals(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(modelsSchema()), firstStreamInState);

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
            assertEquals(ORDERED_COL_STATE_TYPE, c.getStreamState().get(STATE_TYPE_KEY).asText());
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
        modelsSchema());
  }

  protected void assertExpectedStateMessagesWithTotalCount(final List<AirbyteStateMessage> stateMessages, final long totalRecordCount) {
    long actualRecordCount = 0L;
    for (final AirbyteStateMessage message : stateMessages) {
      actualRecordCount += message.getSourceStats().getRecordCount();
    }
    assertEquals(actualRecordCount, totalRecordCount);
  }

  @Override
  protected void removeCDCColumns(final ObjectNode data) {
    data.remove(CDC_LSN);
    data.remove(CDC_UPDATED_AT);
    data.remove(CDC_DELETED_AT);
    data.remove(CDC_EVENT_SERIAL_NO);
    data.remove(CDC_DEFAULT_CURSOR);
  }

  @Override
  protected MssqlCdcTargetPosition cdcLatestTargetPosition() {
    testdb.withWaitUntilMaxLsnAvailable();
    final JdbcDatabase jdbcDatabase = new StreamingJdbcDatabase(
        testDataSource,
        new MssqlSourceOperations(),
        AdaptiveStreamingQueryConfig::new);
    return MssqlCdcTargetPosition.getTargetPosition(jdbcDatabase, testdb.getDatabaseName());
  }

  @Override
  protected MssqlCdcTargetPosition extractPosition(final JsonNode record) {
    return new MssqlCdcTargetPosition(Lsn.valueOf(record.get(CDC_LSN).asText()));
  }

  @Override
  protected void assertNullCdcMetaData(final JsonNode data) {
    assertNull(data.get(CDC_LSN));
    assertNull(data.get(CDC_UPDATED_AT));
    assertNull(data.get(CDC_DELETED_AT));
    assertNull(data.get(CDC_EVENT_SERIAL_NO));
    assertNull(data.get(CDC_DEFAULT_CURSOR));
  }

  @Override
  protected void assertCdcMetaData(final JsonNode data, final boolean deletedAtNull) {
    assertNotNull(data.get(CDC_LSN));
    assertNotNull(data.get(CDC_EVENT_SERIAL_NO));
    assertNotNull(data.get(CDC_UPDATED_AT));
    assertNotNull(data.get(CDC_DEFAULT_CURSOR));
    if (deletedAtNull) {
      assertTrue(data.get(CDC_DELETED_AT).isNull());
    } else {
      assertFalse(data.get(CDC_DELETED_AT).isNull());
    }
  }

  @Override
  protected void addCdcMetadataColumns(final AirbyteStream stream) {
    final ObjectNode jsonSchema = (ObjectNode) stream.getJsonSchema();
    final ObjectNode properties = (ObjectNode) jsonSchema.get("properties");

    final JsonNode airbyteIntegerType = Jsons.jsonNode(ImmutableMap.of("type", "number", "airbyte_type", "integer"));
    final JsonNode stringType = Jsons.jsonNode(ImmutableMap.of("type", "string"));
    properties.set(CDC_LSN, stringType);
    properties.set(CDC_UPDATED_AT, stringType);
    properties.set(CDC_DELETED_AT, stringType);
    properties.set(CDC_EVENT_SERIAL_NO, stringType);
    properties.set(CDC_DEFAULT_CURSOR, airbyteIntegerType);

  }

  @Override
  protected void addCdcDefaultCursorField(final AirbyteStream stream) {
    if (stream.getSupportedSyncModes().contains(SyncMode.INCREMENTAL)) {
      stream.setDefaultCursorField(ImmutableList.of(CDC_DEFAULT_CURSOR));
    }
  }

  @Override
  protected void assertExpectedStateMessages(final List<? extends AirbyteStateMessage> stateMessages) {
    assertEquals(7, stateMessages.size());
    assertStateTypes(stateMessages, 4);
  }

  @Override
  protected void assertExpectedStateMessagesFromIncrementalSync(final List<? extends AirbyteStateMessage> stateMessages) {
    assertEquals(1, stateMessages.size());
    assertNotNull(stateMessages.get(0).getData());
    for (final AirbyteStateMessage stateMessage : stateMessages) {
      assertNotNull(stateMessage.getData().get("cdc_state").get("state").get(MSSQL_CDC_OFFSET));
      assertNotNull(stateMessage.getData().get("cdc_state").get("state").get(MSSQL_DB_HISTORY));
    }
  }

  @Override
  protected void assertExpectedStateMessagesForNoData(final List<? extends AirbyteStateMessage> stateMessages) {
    assertEquals(2, stateMessages.size());
  }

  @Override
  protected void assertExpectedStateMessagesForRecordsProducedDuringAndAfterSync(final List<? extends AirbyteStateMessage> stateAfterFirstBatch) {
    assertEquals(27, stateAfterFirstBatch.size());
    assertStateTypes(stateAfterFirstBatch, 24);
  }

  private void assertStateTypes(final List<? extends AirbyteStateMessage> stateMessages, final int indexTillWhichExpectOcState) {
    JsonNode sharedState = null;
    LOGGER.info("*** states to assert: {}", Arrays.deepToString(stateMessages.toArray()));
    for (int i = 0; i < stateMessages.size(); i++) {
      final AirbyteStateMessage stateMessage = stateMessages.get(i);
      assertEquals(AirbyteStateType.GLOBAL, stateMessage.getType());
      final AirbyteGlobalState global = stateMessage.getGlobal();
      assertNotNull(global.getSharedState());
      if (Objects.isNull(sharedState)) {
        sharedState = global.getSharedState();
      } else {
        assertEquals(sharedState, global.getSharedState(), "states were " + Arrays.deepToString(stateMessages.toArray()));
        // assertEquals(sharedState.toString().replaceAll("ts_ms\\\\\":\\d+", ""),
        // global.getSharedState().toString().replaceAll("ts_ms\\\\\":\\d+", ""));
      }
      assertEquals(1, global.getStreamStates().size());
      final AirbyteStreamState streamState = global.getStreamStates().get(0);
      if (i <= indexTillWhichExpectOcState) {
        assertTrue(streamState.getStreamState().has(STATE_TYPE_KEY));
        assertEquals(ORDERED_COL_STATE_TYPE, streamState.getStreamState().get(STATE_TYPE_KEY).asText());
      } else {
        assertFalse(streamState.getStreamState().has(STATE_TYPE_KEY));
      }
    }
  }

  @Override
  protected void compareTargetPositionFromTheRecordsWithTargetPostionGeneratedBeforeSync(final CdcTargetPosition targetPosition,
                                                                                         final AirbyteRecordMessage record) {
    // The LSN from records should be either equal or grater than the position value before the sync
    // started.
    // Since we're using shared containers, the current LSN can move forward without any data
    // modifications
    // (INSERT, UPDATE, DELETE) in the current DB
    assert targetPosition instanceof MssqlCdcTargetPosition;
    assertTrue(extractPosition(record.getData()).targetLsn.compareTo(((MssqlCdcTargetPosition) targetPosition).targetLsn) >= 0);
  }

  protected void waitForCdcRecords(String schemaName, String tableName, int recordCount)
      throws Exception {
    testdb.waitForCdcRecords(schemaName, tableName, recordCount);
  }

  protected void deleteCommand(final String streamName) {
    String selectCountSql = "SELECT COUNT(*) FROM %s.%s".formatted(modelsSchema(), streamName);
    try {
      int rowCount = testdb.query(ctx -> ctx.fetch(selectCountSql)).get(0).get(0, Integer.class);
      LOGGER.info("deleting all {} rows from table {}.{}", rowCount, modelsSchema(), streamName);
      super.deleteCommand(streamName);
    } catch (SQLException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  protected boolean supportResumableFullRefresh() {
    return true;
  }

  @Override
  protected void assertExpectedStateMessagesForFullRefresh(final List<? extends AirbyteStateMessage> stateMessages) {
    // Full refresh will only send 6 state messages - one for each record (including the final one).
    assertEquals(6, stateMessages.size());
  }

}
