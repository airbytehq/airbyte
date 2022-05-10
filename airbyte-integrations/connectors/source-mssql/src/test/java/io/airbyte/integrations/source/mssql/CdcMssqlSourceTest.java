/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_DELETED_AT;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_UPDATED_AT;
import static io.airbyte.integrations.source.mssql.MssqlSource.CDC_LSN;
import static io.airbyte.integrations.source.mssql.MssqlSource.DRIVER_CLASS;
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
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.StreamingJdbcDatabase;
import io.airbyte.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.debezium.CdcSourceTest;
import io.airbyte.integrations.debezium.CdcTargetPosition;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.debezium.connector.sqlserver.Lsn;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.jooq.DSLContext;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MSSQLServerContainer;

public class CdcMssqlSourceTest extends CdcSourceTest {

  private static final String CDC_ROLE_NAME = "cdc_selector";
  private static final String TEST_USER_NAME = "tester";
  private static final String TEST_USER_PASSWORD = "testerjester[1]";

  private MSSQLServerContainer<?> container;

  private String dbName;
  private Database database;
  private JdbcDatabase testJdbcDatabase;
  private MssqlSource source;
  private JsonNode config;
  private DSLContext dslContext;

  @BeforeEach
  public void setup() throws SQLException {
    init();
    setupTestUser();
    revokeAllPermissions();
    super.setup();
    grantCorrectPermissions();
  }

  private void init() {
    container = new MSSQLServerContainer<>("mcr.microsoft.com/mssql/server:2019-latest").acceptLicense();
    container.addEnv("MSSQL_AGENT_ENABLED", "True"); // need this running for cdc to work
    container.start();

    dbName = Strings.addRandomSuffix("db", "_", 10).toLowerCase();
    source = new MssqlSource();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("database", dbName)
        .put("schemas", List.of(MODELS_SCHEMA, MODELS_SCHEMA + "_random"))
        .put("username", TEST_USER_NAME)
        .put("password", TEST_USER_PASSWORD)
        .put("replication_method", "CDC")
        .build());

    dslContext = DSLContextFactory.create(
        container.getUsername(),
        container.getPassword(),
        DRIVER_CLASS,
        String.format("jdbc:sqlserver://%s:%s",
            container.getHost(),
            container.getFirstMappedPort()),
        null);

    database = new Database(dslContext);

    testJdbcDatabase = new DefaultJdbcDatabase(DataSourceFactory.create(
        TEST_USER_NAME,
        TEST_USER_PASSWORD,
        DRIVER_CLASS,
        String.format("jdbc:sqlserver://%s:%s",
            container.getHost(),
            container.getFirstMappedPort())));

    executeQuery("CREATE DATABASE " + dbName + ";");
    switchSnapshotIsolation(true, dbName);
  }

  private void switchSnapshotIsolation(final Boolean on, final String db) {
    final String onOrOff = on ? "ON" : "OFF";
    executeQuery("ALTER DATABASE " + db + "\n\tSET ALLOW_SNAPSHOT_ISOLATION " + onOrOff);
  }

  private void setupTestUser() {
    executeQuery("USE " + dbName);
    executeQuery("CREATE LOGIN " + TEST_USER_NAME + " WITH PASSWORD = '" + TEST_USER_PASSWORD + "';");
    executeQuery("CREATE USER " + TEST_USER_NAME + " FOR LOGIN " + TEST_USER_NAME + ";");
  }

  private void revokeAllPermissions() {
    executeQuery("REVOKE ALL FROM " + TEST_USER_NAME + " CASCADE;");
    executeQuery("EXEC sp_msforeachtable \"REVOKE ALL ON '?' TO " + TEST_USER_NAME + ";\"");
  }

  private void alterPermissionsOnSchema(final Boolean grant, final String schema) {
    final String grantOrRemove = grant ? "GRANT" : "REVOKE";
    executeQuery(String.format("USE %s;\n" + "%s SELECT ON SCHEMA :: [%s] TO %s", dbName, grantOrRemove, schema, TEST_USER_NAME));
  }

  private void grantCorrectPermissions() {
    alterPermissionsOnSchema(true, MODELS_SCHEMA);
    alterPermissionsOnSchema(true, MODELS_SCHEMA + "_random");
    alterPermissionsOnSchema(true, "cdc");
    executeQuery(String.format("EXEC sp_addrolemember N'%s', N'%s';", CDC_ROLE_NAME, TEST_USER_NAME));
  }

  @Override
  public String createSchemaQuery(final String schemaName) {
    return "CREATE SCHEMA " + schemaName;
  }

  private void switchCdcOnDatabase(final Boolean enable, final String db) {
    final String storedProc = enable ? "sys.sp_cdc_enable_db" : "sys.sp_cdc_disable_db";
    executeQuery("USE " + db + "\n" + "EXEC " + storedProc);
  }

  @Override
  public void createTable(final String schemaName, final String tableName, final String columnClause) {
    switchCdcOnDatabase(true, dbName);
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
            Thread.sleep(10000); // 10 seconds
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
    try {
      dslContext.close();
      testJdbcDatabase.close();
      container.close();
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  @Test
  void testAssertCdcEnabledInDb() {
    // since we enable cdc in setup, assert that we successfully pass this first
    assertDoesNotThrow(() -> source.assertCdcEnabledInDb(config, testJdbcDatabase));
    // then disable cdc and assert the check fails
    switchCdcOnDatabase(false, dbName);
    assertThrows(RuntimeException.class, () -> source.assertCdcEnabledInDb(config, testJdbcDatabase));
  }

  @Test
  void testAssertCdcSchemaQueryable() {
    // correct access granted by setup so assert check passes
    assertDoesNotThrow(() -> source.assertCdcSchemaQueryable(config, testJdbcDatabase));
    // now revoke perms and assert that check fails
    alterPermissionsOnSchema(false, "cdc");
    assertThrows(com.microsoft.sqlserver.jdbc.SQLServerException.class, () -> source.assertCdcSchemaQueryable(config, testJdbcDatabase));
  }

  private void switchSqlServerAgentAndWait(final Boolean start) throws InterruptedException {
    final String startOrStop = start ? "START" : "STOP";
    executeQuery(String.format("EXEC xp_servicecontrol N'%s',N'SQLServerAGENT';", startOrStop));
    Thread.sleep(15 * 1000); // 15 seconds to wait for change of agent state
  }

  @Test
  void testAssertSqlServerAgentRunning() throws InterruptedException {
    executeQuery(String.format("USE master;\n" + "GRANT VIEW SERVER STATE TO %s", TEST_USER_NAME));
    // assert expected failure if sql server agent stopped
    switchSqlServerAgentAndWait(false);
    assertThrows(RuntimeException.class, () -> source.assertSqlServerAgentRunning(testJdbcDatabase));
    // assert success if sql server agent running
    switchSqlServerAgentAndWait(true);
    assertDoesNotThrow(() -> source.assertSqlServerAgentRunning(testJdbcDatabase));
  }

  @Test
  void testAssertSnapshotIsolationAllowed() {
    // snapshot isolation enabled by setup so assert check passes
    assertDoesNotThrow(() -> source.assertSnapshotIsolationAllowed(config, testJdbcDatabase));
    // now disable snapshot isolation and assert that check fails
    switchSnapshotIsolation(false, dbName);
    assertThrows(RuntimeException.class, () -> source.assertSnapshotIsolationAllowed(config, testJdbcDatabase));
  }

  // Ensure the CDC check operations are included when CDC is enabled
  // todo: make this better by checking the returned checkOperations from source.getCheckOperations
  @Test
  void testCdcCheckOperations() throws Exception {
    // assertCdcEnabledInDb
    switchCdcOnDatabase(false, dbName);
    AirbyteConnectionStatus status = getSource().check(getConfig());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
    switchCdcOnDatabase(true, dbName);
    // assertCdcSchemaQueryable
    alterPermissionsOnSchema(false, "cdc");
    status = getSource().check(getConfig());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
    alterPermissionsOnSchema(true, "cdc");
    // assertSqlServerAgentRunning
    executeQuery(String.format("USE master;\n" + "GRANT VIEW SERVER STATE TO %s", TEST_USER_NAME));
    switchSqlServerAgentAndWait(false);
    status = getSource().check(getConfig());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
    switchSqlServerAgentAndWait(true);
    // assertSnapshotIsolationAllowed
    switchSnapshotIsolation(false, dbName);
    status = getSource().check(getConfig());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
  }

  // todo: check LSN returned is actually the max LSN
  // todo: check we fail as expected under certain conditions
  @Test
  void testGetTargetPosition() throws InterruptedException {
    Thread.sleep(10 * 1000); // Sleeping because sometimes the db is not yet completely ready and the lsn is not found
    // check that getTargetPosition returns higher Lsn after inserting new row
    final Lsn firstLsn = MssqlCdcTargetPosition.getTargetPosition(testJdbcDatabase, dbName).targetLsn;
    executeQuery(String.format("USE %s; INSERT INTO %s.%s (%s, %s, %s) VALUES (%s, %s, '%s');",
        dbName, MODELS_SCHEMA, MODELS_STREAM_NAME, COL_ID, COL_MAKE_ID, COL_MODEL, 910019, 1, "another car"));
    Thread.sleep(15 * 1000); // 15 seconds to wait for Agent capture job to log cdc change
    final Lsn secondLsn = MssqlCdcTargetPosition.getTargetPosition(testJdbcDatabase, dbName).targetLsn;
    assertTrue(secondLsn.compareTo(firstLsn) > 0);
  }

  @Override
  protected void removeCDCColumns(final ObjectNode data) {
    data.remove(CDC_LSN);
    data.remove(CDC_UPDATED_AT);
    data.remove(CDC_DELETED_AT);
  }

  @Override
  protected CdcTargetPosition cdcLatestTargetPosition() {
    try {
      // Sleeping because sometimes the db is not yet completely ready and the lsn is not found
      Thread.sleep(5000);
    } catch (final InterruptedException e) {
      throw new RuntimeException(e);
    }
    final JdbcDatabase jdbcDatabase = new StreamingJdbcDatabase(
        DataSourceFactory.create(config.get("username").asText(),
        config.get("password").asText(),
        DRIVER_CLASS,
        String.format("jdbc:sqlserver://%s:%s;databaseName=%s;",
            config.get("host").asText(),
            config.get("port").asInt(),
            dbName)),
        new MssqlSourceOperations(),
            AdaptiveStreamingQueryConfig::new
    );
    return MssqlCdcTargetPosition.getTargetPosition(jdbcDatabase, dbName);
  }

  @Override
  protected CdcTargetPosition extractPosition(final JsonNode record) {
    return new MssqlCdcTargetPosition(Lsn.valueOf(record.get(CDC_LSN).asText()));
  }

  @Override
  protected void assertNullCdcMetaData(final JsonNode data) {
    assertNull(data.get(CDC_LSN));
    assertNull(data.get(CDC_UPDATED_AT));
    assertNull(data.get(CDC_DELETED_AT));
  }

  @Override
  protected void assertCdcMetaData(final JsonNode data, final boolean deletedAtNull) {
    assertNotNull(data.get(CDC_LSN));
    assertNotNull(data.get(CDC_UPDATED_AT));
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

    final JsonNode stringType = Jsons.jsonNode(ImmutableMap.of("type", "string"));
    properties.set(CDC_LSN, stringType);
    properties.set(CDC_UPDATED_AT, stringType);
    properties.set(CDC_DELETED_AT, stringType);

  }

  @Override
  protected Source getSource() {
    return new MssqlSource();
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
  protected void assertExpectedStateMessages(final List<AirbyteStateMessage> stateMessages) {
    assertEquals(1, stateMessages.size());
    assertNotNull(stateMessages.get(0).getData());
    assertNotNull(stateMessages.get(0).getData().get("cdc_state").get("state").get(MSSQL_CDC_OFFSET));
    assertNotNull(stateMessages.get(0).getData().get("cdc_state").get("state").get(MSSQL_DB_HISTORY));
  }

}
