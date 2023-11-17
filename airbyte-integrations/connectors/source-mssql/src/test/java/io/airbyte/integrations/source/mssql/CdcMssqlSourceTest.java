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
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.StreamingJdbcDatabase;
import io.airbyte.cdk.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.debezium.CdcSourceTest;
import io.airbyte.cdk.integrations.debezium.internals.mssql.MssqlCdcTargetPosition;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import io.debezium.connector.sqlserver.Lsn;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class CdcMssqlSourceTest extends CdcSourceTest {

  private static final String CDC_ROLE_NAME = "cdc_selector";

  private MsSQLTestDatabase testdb;

  static private MsSQLTestDatabase createCdcTestDatabase() {
    return MsSQLTestDatabase.in("mcr.microsoft.com/mssql/server:2022-latest", "withAgent");
  }

  @BeforeAll
  static public void waitToFindLsn() throws Exception {
    // Trigger shared testcontainer creation.
    createCdcTestDatabase().close();
    // Sleeping because sometimes the db is not yet completely ready and the lsn is not found
    Thread.sleep(20_000);
  }

  @BeforeEach
  public void setup() throws SQLException {
    testdb = createCdcTestDatabase().withSnapshotIsolation();
    super.setup();
    testdb
        .with("REVOKE ALL FROM %s CASCADE;", testdb.getUserName())
        .with("EXEC sp_msforeachtable \"REVOKE ALL ON '?' TO %s;\"", testdb.getUserName());
    alterPermissionsOnSchema(true, getModelsSchema());
    alterPermissionsOnSchema(true, getModelsSchema() + "_random");
    alterPermissionsOnSchema(true, "cdc");
    testdb.with("EXEC sp_addrolemember N'%s', N'%s';", CDC_ROLE_NAME, testdb.getUserName());
  }

  private JdbcDatabase getJdbcDatabase() {
    return new DefaultJdbcDatabase(testdb.getDataSource());
  }

  private void alterPermissionsOnSchema(final Boolean grant, final String schema) {
    testdb.with("%s SELECT ON SCHEMA :: [%s] TO %s", grant ? "GRANT" : "REVOKE", schema, testdb.getUserName());
  }

  @Override
  public String createSchemaQuery(final String schemaName) {
    return "CREATE SCHEMA " + schemaName;
  }

  // TODO : Delete this Override when MSSQL supports individual table snapshot
  @Override
  public void newTableSnapshotTest() {
    // Do nothing
  }

  @Override
  protected String randomTableSchema() {
    return getModelsSchema() + "_random";
  }

  @Override
  public void createTable(final String schemaName, final String tableName, final String columnClause) {
    testdb.withCdc();
    super.createTable(schemaName, tableName, columnClause);

    // sometimes seeing an error that we can't enable cdc on a table while sql server agent is still
    // spinning up
    // solving with a simple while retry loop
    boolean failingToStart = true;
    int retryNum = 0;
    final int maxRetries = 10;
    while (failingToStart) {
      try {
        executeQuery(String.format(
            "EXEC sys.sp_cdc_enable_table\n"
                + "\t@source_schema = N'%s',\n"
                + "\t@source_name   = N'%s', \n"
                + "\t@role_name     = N'%s',\n"
                + "\t@supports_net_changes = 0",
            schemaName, tableName, CDC_ROLE_NAME)); // enables cdc on MODELS_SCHEMA.MODELS_STREAM_NAME, giving CDC_ROLE_NAME select access
        failingToStart = false;
      } catch (final Exception e) {
        if (retryNum >= maxRetries) {
          throw e;
        } else {
          retryNum++;
          try {
            Thread.sleep(10_000); // 10 seconds
          } catch (final InterruptedException ex) {
            throw new RuntimeException(ex);
          }
        }
      }
    }
  }

  @Override
  public String columnClause(final Map<String, String> columnsWithDataType, final Optional<String> primaryKey) {
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

  @AfterEach
  public void tearDown() {
    testdb.close();
  }

  @Test
  void testAssertCdcEnabledInDb() {
    // since we enable cdc in setup, assert that we successfully pass this first
    assertDoesNotThrow(() -> new MssqlSource().assertCdcEnabledInDb(getConfig(), getJdbcDatabase()));
    // then disable cdc and assert the check fails
    testdb.withoutCdc();
    assertThrows(RuntimeException.class, () -> new MssqlSource().assertCdcEnabledInDb(getConfig(), getJdbcDatabase()));
  }

  @Test
  void testAssertCdcSchemaQueryable() {
    // correct access granted by setup so assert check passes
    assertDoesNotThrow(() -> new MssqlSource().assertCdcSchemaQueryable(getConfig(), getJdbcDatabase()));
    // now revoke perms and assert that check fails
    alterPermissionsOnSchema(false, "cdc");
    assertThrows(com.microsoft.sqlserver.jdbc.SQLServerException.class,
        () -> new MssqlSource().assertCdcSchemaQueryable(getConfig(), getJdbcDatabase()));
  }

  private void switchSqlServerAgentAndWait(final Boolean start) throws InterruptedException {
    final String startOrStop = start ? "START" : "STOP";
    executeQuery(String.format("EXEC xp_servicecontrol N'%s',N'SQLServerAGENT';", startOrStop));
    Thread.sleep(15_000); // 15 seconds to wait for change of agent state
  }

  @Test
  void testAssertSqlServerAgentRunning() throws InterruptedException {
    executeQuery(String.format("USE master;\n" + "GRANT VIEW SERVER STATE TO %s", testdb.getUserName()));
    // assert expected failure if sql server agent stopped
    switchSqlServerAgentAndWait(false);
    assertThrows(RuntimeException.class, () -> new MssqlSource().assertSqlServerAgentRunning(getJdbcDatabase()));
    // assert success if sql server agent running
    switchSqlServerAgentAndWait(true);
    assertDoesNotThrow(() -> new MssqlSource().assertSqlServerAgentRunning(getJdbcDatabase()));
  }

  @Test
  void testAssertSnapshotIsolationAllowed() {
    // snapshot isolation enabled by setup so assert check passes
    assertDoesNotThrow(() -> new MssqlSource().assertSnapshotIsolationAllowed(getConfig(), getJdbcDatabase()));
    // now disable snapshot isolation and assert that check fails
    testdb.withoutSnapshotIsolation();
    assertThrows(RuntimeException.class, () -> new MssqlSource().assertSnapshotIsolationAllowed(getConfig(), getJdbcDatabase()));
  }

  @Test
  void testAssertSnapshotIsolationDisabled() {
    final JsonNode replicationConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "CDC")
        .put("data_to_sync", "New Changes Only")
        // set snapshot_isolation level to "Read Committed" to disable snapshot
        .put("snapshot_isolation", "Read Committed")
        .build());
    final var config = getConfig();
    Jsons.replaceNestedValue(config, List.of("replication_method"), replicationConfig);
    assertDoesNotThrow(() -> new MssqlSource().assertSnapshotIsolationAllowed(config, getJdbcDatabase()));
    testdb.withoutSnapshotIsolation();
    assertDoesNotThrow(() -> new MssqlSource().assertSnapshotIsolationAllowed(config, getJdbcDatabase()));
  }

  // Ensure the CDC check operations are included when CDC is enabled
  // todo: make this better by checking the returned checkOperations from source.getCheckOperations
  @Test
  void testCdcCheckOperations() throws Exception {
    // assertCdcEnabledInDb
    testdb.withoutCdc();
    AirbyteConnectionStatus status = getSource().check(getConfig());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
    testdb.withCdc();
    // assertCdcSchemaQueryable
    alterPermissionsOnSchema(false, "cdc");
    status = getSource().check(getConfig());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
    alterPermissionsOnSchema(true, "cdc");
    // assertSqlServerAgentRunning
    executeQuery(String.format("USE master;\n" + "GRANT VIEW SERVER STATE TO %s", testdb.getUserName()));
    switchSqlServerAgentAndWait(false);
    status = getSource().check(getConfig());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
    switchSqlServerAgentAndWait(true);
    // assertSnapshotIsolationAllowed
    testdb.withoutSnapshotIsolation();
    status = getSource().check(getConfig());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
  }

  @Test
  void testCdcCheckOperationsWithDot() throws Exception {
    final String dbNameWithDot = testdb.getDatabaseName().replace("_", ".");
    testdb.with("CREATE DATABASE [%s];", dbNameWithDot)
        .with("USE [%s]", dbNameWithDot)
        .with("EXEC sys.sp_cdc_enable_db;");
    final AirbyteConnectionStatus status = getSource().check(getConfig());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.SUCCEEDED);
  }

  // todo: check LSN returned is actually the max LSN
  // todo: check we fail as expected under certain conditions
  @Test
  void testGetTargetPosition() throws InterruptedException {
    // check that getTargetPosition returns higher Lsn after inserting new row
    final Lsn firstLsn = MssqlCdcTargetPosition.getTargetPosition(getJdbcDatabase(), testdb.getDatabaseName()).targetLsn;
    executeQuery(String.format("USE %s; INSERT INTO %s.%s (%s, %s, %s) VALUES (%s, %s, '%s');",
        testdb.getDatabaseName(), getModelsSchema(), MODELS_STREAM_NAME, COL_ID, COL_MAKE_ID, COL_MODEL, 910019, 1, "another car"));
    Thread.sleep(15 * 1000); // 15 seconds to wait for Agent capture job to log cdc change
    final Lsn secondLsn = MssqlCdcTargetPosition.getTargetPosition(getJdbcDatabase(), testdb.getDatabaseName()).targetLsn;
    assertTrue(secondLsn.compareTo(firstLsn) > 0);
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
    try {
      // Sleeping because sometimes the db is not yet completely ready and the lsn is not found
      Thread.sleep(5000);
    } catch (final InterruptedException e) {
      throw new RuntimeException(e);
    }
    final JdbcDatabase jdbcDatabase = new StreamingJdbcDatabase(
        testdb.getDataSource(),
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
  protected Source getSource() {
    return new MssqlSource();
  }

  @Override
  protected JsonNode getConfig() {
    return testdb.testConfigBuilder()
        .withSchemas(getModelsSchema(), getModelsSchema() + "_random")
        .withCdcReplication()
        .withoutSsl()
        .build();
  }

  @Override
  protected Database getDatabase() {
    return testdb.getDatabase();
  }

  @Override
  protected void assertExpectedStateMessages(final List<AirbyteStateMessage> stateMessages) {
    assertEquals(1, stateMessages.size());
    assertNotNull(stateMessages.get(0).getData());
    assertNotNull(stateMessages.get(0).getData().get("cdc_state").get("state").get(MSSQL_CDC_OFFSET));
    assertNotNull(stateMessages.get(0).getData().get("cdc_state").get("state").get(MSSQL_DB_HISTORY));
  }

}
