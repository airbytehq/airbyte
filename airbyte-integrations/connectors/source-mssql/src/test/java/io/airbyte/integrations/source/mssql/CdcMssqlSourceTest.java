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
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
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
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteGlobalState;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
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
    stateMessages.stream().forEach(stateMessage -> count.addAndGet(stateMessage.getSourceStats().getRecordCount().longValue()));
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
