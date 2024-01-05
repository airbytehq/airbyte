/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventUtils.CDC_DELETED_AT;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventUtils.CDC_UPDATED_AT;
import static io.airbyte.integrations.source.mssql.MssqlSource.CDC_DEFAULT_CURSOR;
import static io.airbyte.integrations.source.mssql.MssqlSource.CDC_EVENT_SERIAL_NO;
import static io.airbyte.integrations.source.mssql.MssqlSource.CDC_LSN;
import static io.airbyte.integrations.source.mssql.MssqlSource.MSSQL_CDC_OFFSET;
import static io.airbyte.integrations.source.mssql.MssqlSource.MSSQL_DB_HISTORY;
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
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import io.debezium.connector.sqlserver.Lsn;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.api.TestInstance.Lifecycle;
import org.testcontainers.containers.MSSQLServerContainer;
import org.testcontainers.utility.DockerImageName;

@TestInstance(Lifecycle.PER_CLASS)
public class CdcMssqlSourceTest extends CdcSourceTest<MssqlSource, MsSQLTestDatabase> {

  static private final String CDC_ROLE_NAME = "cdc_selector";

  static private final String TEST_USER_NAME_PREFIX = "cdc_test_user";

  // Deliberately do not share this test container, as we're going to mutate the global SQL Server
  // state.
  protected final MSSQLServerContainer<?> privateContainer;

  private DataSource testDataSource;

  CdcMssqlSourceTest() {
    this.privateContainer = createContainer();
  }

  protected MSSQLServerContainer<?> createContainer() {
    return new MsSQLContainerFactory()
        .createNewContainer(DockerImageName.parse("mcr.microsoft.com/mssql/server:2022-latest"));
  }

  @BeforeAll
  public void beforeAll() {
    new MsSQLContainerFactory().withAgent(privateContainer);
    privateContainer.start();
  }

  @AfterAll
  void afterAll() {
    privateContainer.close();
  }

  protected final String testUserName() {
    return testdb.withNamespace(TEST_USER_NAME_PREFIX);
  }

  @Override
  protected MsSQLTestDatabase createTestDatabase() {
    final var testdb = new MsSQLTestDatabase(privateContainer);
    return testdb
        .withConnectionProperty("encrypt", "false")
        .withConnectionProperty("databaseName", testdb.getDatabaseName())
        .initialized()
        .withSnapshotIsolation()
        .withCdc()
        .withWaitUntilAgentRunning();
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
        .build();
  }

  @Override
  @BeforeEach
  protected void setup() {
    super.setup();

    // Enables cdc on MODELS_SCHEMA.MODELS_STREAM_NAME, giving CDC_ROLE_NAME select access.
    final var enableCdcSqlFmt = """
                                EXEC sys.sp_cdc_enable_table
                                \t@source_schema = N'%s',
                                \t@source_name   = N'%s',
                                \t@role_name     = N'%s',
                                \t@supports_net_changes = 0""";
    testdb
        .with(enableCdcSqlFmt, modelsSchema(), MODELS_STREAM_NAME, CDC_ROLE_NAME)
        .with(enableCdcSqlFmt, randomSchema(), RANDOM_TABLE_NAME, CDC_ROLE_NAME);

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

    testDataSource = createTestDataSource();
  }

  protected DataSource createTestDataSource() {
    return DataSourceFactory.create(
        testUserName(),
        testdb.getPassword(),
        testdb.getDatabaseDriver().getDriverClassName(),
        testdb.getJdbcUrl(),
        Map.of("encrypt", "false"),
        JdbcConnector.CONNECT_TIMEOUT_DEFAULT);
  }

  @Override
  @AfterEach
  protected void tearDown() {
    try {
      DataSourceFactory.close(testDataSource);
    } catch (Exception e) {
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
  void testAssertSqlServerAgentRunning() {
    testdb.withAgentStopped().withWaitUntilAgentStopped();
    // assert expected failure if sql server agent stopped
    assertThrows(RuntimeException.class, () -> source().assertSqlServerAgentRunning(testDatabase()));
    // assert success if sql server agent running
    testdb.withAgentStarted().withWaitUntilAgentRunning();
    assertDoesNotThrow(() -> source().assertSqlServerAgentRunning(testDatabase()));
  }

  @Test
  void testAssertSnapshotIsolationAllowed() {
    // snapshot isolation enabled by setup so assert check passes
    assertDoesNotThrow(() -> source().assertSnapshotIsolationAllowed(config(), testDatabase()));
    // now disable snapshot isolation and assert that check fails
    testdb.withoutSnapshotIsolation();
    assertThrows(RuntimeException.class, () -> source().assertSnapshotIsolationAllowed(config(), testDatabase()));
  }

  @Test
  void testAssertSnapshotIsolationDisabled() {
    final JsonNode replicationConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "CDC")
        .put("data_to_sync", "New Changes Only")
        // set snapshot_isolation level to "Read Committed" to disable snapshot
        .put("snapshot_isolation", "Read Committed")
        .build());
    final var config = config();
    Jsons.replaceNestedValue(config, List.of("replication_method"), replicationConfig);
    assertDoesNotThrow(() -> source().assertSnapshotIsolationAllowed(config, testDatabase()));
    testdb.withoutSnapshotIsolation();
    assertDoesNotThrow(() -> source().assertSnapshotIsolationAllowed(config, testDatabase()));
  }

  // Ensure the CDC check operations are included when CDC is enabled
  // todo: make this better by checking the returned checkOperations from source.getCheckOperations
  @Test
  void testCdcCheckOperations() throws Exception {
    // assertCdcEnabledInDb
    testdb.withoutCdc();
    AirbyteConnectionStatus status = source().check(config());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
    testdb.withCdc();
    // assertCdcSchemaQueryable
    testdb.with("REVOKE SELECT ON SCHEMA :: [cdc] TO %s", testUserName());
    status = source().check(config());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
    testdb.with("GRANT SELECT ON SCHEMA :: [cdc] TO %s", testUserName());

    // assertSqlServerAgentRunning

    testdb.withAgentStopped().withWaitUntilAgentStopped();
    status = source().check(config());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
    testdb.withAgentStarted().withWaitUntilAgentRunning();
    // assertSnapshotIsolationAllowed
    testdb.withoutSnapshotIsolation();
    status = source().check(config());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
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
  void testGetTargetPosition() {
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
  protected void assertExpectedStateMessages(final List<AirbyteStateMessage> stateMessages) {
    assertEquals(1, stateMessages.size());
    assertNotNull(stateMessages.get(0).getData());
    assertNotNull(stateMessages.get(0).getData().get("cdc_state").get("state").get(MSSQL_CDC_OFFSET));
    assertNotNull(stateMessages.get(0).getData().get("cdc_state").get("state").get(MSSQL_DB_HISTORY));
  }

}
