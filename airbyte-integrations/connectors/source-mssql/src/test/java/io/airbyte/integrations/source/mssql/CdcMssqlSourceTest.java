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

package io.airbyte.integrations.source.mssql;

import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_DELETED_AT;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_UPDATED_AT;
import static io.airbyte.integrations.source.mssql.MssqlSource.CDC_LSN;
import static io.airbyte.integrations.source.mssql.MssqlSource.DRIVER_CLASS;
import static io.airbyte.integrations.source.mssql.MssqlSource.MSSQL_CDC_OFFSET;
import static io.airbyte.integrations.source.mssql.MssqlSource.MSSQL_DB_HISTORY;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
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
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MSSQLServerContainer;

public class CdcMssqlSourceTest extends CdcSourceTest {

  private static final String CDC_ROLE_NAME = "cdc_selector";
  private static final String TEST_USER_NAME = "tester";
  private static final String TEST_USER_PASSWORD = "testerjester[1]";

  private MSSQLServerContainer<?> container;

  private String dbName;
  private Database database;
  private MssqlSource source;
  private JsonNode config;

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
        .put("username", TEST_USER_NAME)
        .put("password", TEST_USER_PASSWORD)
        .put("replication_method", "CDC")
        .build());

    database = Databases.createDatabase(
        container.getUsername(),
        container.getPassword(),
        String.format("jdbc:sqlserver://%s:%s",
            container.getHost(),
            container.getFirstMappedPort()),
        DRIVER_CLASS,
        null);

    executeQuery("CREATE DATABASE " + dbName + ";");
    executeQuery("ALTER DATABASE " + dbName + "\n\tSET ALLOW_SNAPSHOT_ISOLATION ON");
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

  private void grantCorrectPermissions() {
    executeQuery(String.format("USE %s;\n" + "GRANT SELECT ON SCHEMA :: [%s] TO %s", dbName, MODELS_SCHEMA, TEST_USER_NAME));
    executeQuery(String.format("USE %s;\n" + "GRANT SELECT ON SCHEMA :: [%s] TO %s", dbName, "cdc", TEST_USER_NAME));
    executeQuery(String.format("EXEC sp_addrolemember N'%s', N'%s';", CDC_ROLE_NAME, TEST_USER_NAME));
  }

  @Override
  public String createSchemaQuery(String schemaName) {
    return "CREATE SCHEMA " + schemaName;
  }

  @Override
  public void createTable(String schemaName, String tableName, String columnClause) {
    executeQuery("USE " + dbName + "\n" + "EXEC sys.sp_cdc_enable_db");
    super.createTable(schemaName, tableName, columnClause);

    // sometimes seeing an error that we can't enable cdc on a table while sql server agent is still
    // spinning up
    // solving with a simple while retry loop
    boolean failingToStart = true;
    int retryNum = 0;
    int maxRetries = 10;
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
      } catch (Exception e) {
        if (retryNum >= maxRetries) {
          throw e;
        } else {
          retryNum++;
          try {
            Thread.sleep(10000); // 10 seconds
          } catch (InterruptedException ex) {
            throw new RuntimeException(ex);
          }
        }
      }
    }
  }

  @Override
  public String columnClause(Map<String, String> columnsWithDataType, Optional<String> primaryKey) {
    StringBuilder columnClause = new StringBuilder();
    int i = 0;
    for (Map.Entry<String, String> column : columnsWithDataType.entrySet()) {
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
      database.close();
      container.close();
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  @Test
  @DisplayName("Ensure CHECK still works when we have permissions to check SQL Server Agent status")
  void testCheckWithElevatedPermissions() {
    executeQuery(String.format("USE master;\n" + "GRANT VIEW SERVER STATE TO %s", TEST_USER_NAME));
    final AirbyteConnectionStatus status = source.check(config);
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.SUCCEEDED);
  }

  @Test
  void testCheckWhenDbCdcDisabled() {
    executeQuery("USE " + dbName + "\n" + "EXEC sys.sp_cdc_disable_db");
    final AirbyteConnectionStatus status = source.check(config);
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
  }

  @Test
  void testCheckWithInadequatePermissions() {
    executeQuery(String.format("USE %s;\n" + "REVOKE SELECT ON SCHEMA :: [%s] TO %s", dbName, "cdc", TEST_USER_NAME));
    final AirbyteConnectionStatus status = source.check(config);
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
  }

  @Override
  protected void removeCDCColumns(ObjectNode data) {
    data.remove(CDC_LSN);
    data.remove(CDC_UPDATED_AT);
    data.remove(CDC_DELETED_AT);
  }

  @Override
  protected CdcTargetPosition cdcLatestTargetPosition() {
    JdbcDatabase jdbcDatabase = Databases.createStreamingJdbcDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:sqlserver://%s:%s;databaseName=%s;",
            config.get("host").asText(),
            config.get("port").asInt(),
            dbName),
        DRIVER_CLASS, new MssqlJdbcStreamingQueryConfiguration(), null);
    return MssqlCdcTargetPosition.getTargetPostion(jdbcDatabase);
  }

  @Override
  protected CdcTargetPosition extractPosition(JsonNode record) {
    return new MssqlCdcTargetPosition(Lsn.valueOf(record.get(CDC_LSN).asText()));
  }

  @Override
  protected void assertNullCdcMetaData(JsonNode data) {
    assertNull(data.get(CDC_LSN));
    assertNull(data.get(CDC_UPDATED_AT));
    assertNull(data.get(CDC_DELETED_AT));
  }

  @Override
  protected void assertCdcMetaData(JsonNode data, boolean deletedAtNull) {
    assertNotNull(data.get(CDC_LSN));
    assertNotNull(data.get(CDC_UPDATED_AT));
    if (deletedAtNull) {
      assertTrue(data.get(CDC_DELETED_AT).isNull());
    } else {
      assertFalse(data.get(CDC_DELETED_AT).isNull());
    }
  }

  @Override
  protected void addCdcMetadataColumns(AirbyteStream stream) {
    ObjectNode jsonSchema = (ObjectNode) stream.getJsonSchema();
    ObjectNode properties = (ObjectNode) jsonSchema.get("properties");

    final JsonNode numberType = Jsons.jsonNode(ImmutableMap.of("type", "number"));
    final JsonNode stringType = Jsons.jsonNode(ImmutableMap.of("type", "string"));
    properties.set(CDC_LSN, stringType);
    properties.set(CDC_UPDATED_AT, numberType);
    properties.set(CDC_DELETED_AT, numberType);

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
  protected void assertExpectedStateMessages(List<AirbyteStateMessage> stateMessages) {
    assertEquals(1, stateMessages.size());
    assertNotNull(stateMessages.get(0).getData());
    assertNotNull(stateMessages.get(0).getData().get("cdc_state").get("state").get(MSSQL_CDC_OFFSET));
    assertNotNull(stateMessages.get(0).getData().get("cdc_state").get("state").get(MSSQL_DB_HISTORY));
  }

}
