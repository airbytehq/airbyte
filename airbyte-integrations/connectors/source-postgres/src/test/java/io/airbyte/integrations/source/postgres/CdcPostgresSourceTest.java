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

package io.airbyte.integrations.source.postgres;

import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_DELETED_AT;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_UPDATED_AT;
import static io.airbyte.integrations.source.postgres.PostgresSource.CDC_LSN;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.db.PgLsn;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.debezium.CdcSourceTest;
import io.airbyte.integrations.debezium.CdcTargetPosition;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.sql.SQLException;
import java.util.List;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

class CdcPostgresSourceTest extends CdcSourceTest {

  private static final String SLOT_NAME_BASE = "debezium_slot";
  private static final String PUBLICATION = "publication";
  private PostgreSQLContainer<?> container;

  private String dbName;
  private Database database;
  private PostgresSource source;
  private JsonNode config;

  @AfterEach
  void tearDown() throws Exception {
    database.close();
    container.close();
  }

  @BeforeEach
  protected void setup() throws SQLException {
    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withCopyFileToContainer(MountableFile.forClasspathResource("postgresql.conf"), "/etc/postgresql/postgresql.conf")
        .withCommand("postgres -c config_file=/etc/postgresql/postgresql.conf");
    container.start();
    source = new PostgresSource();
    dbName = Strings.addRandomSuffix("db", "_", 10).toLowerCase();

    final String initScriptName = "init_" + dbName.concat(".sql");
    final String tmpFilePath = IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE " + dbName + ";");
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), container);

    config = getConfig(dbName);
    final String fullReplicationSlot = SLOT_NAME_BASE + "_" + dbName;
    database = getDatabaseFromConfig(config);
    database.query(ctx -> {
      ctx.execute("SELECT pg_create_logical_replication_slot('" + fullReplicationSlot + "', 'pgoutput');");
      ctx.execute("CREATE PUBLICATION " + PUBLICATION + " FOR ALL TABLES;");

      return null;
    });

    super.setup();
  }

  private JsonNode getConfig(String dbName) {
    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("replication_slot", SLOT_NAME_BASE + "_" + dbName)
        .put("publication", PUBLICATION)
        .build());

    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("database", dbName)
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .put("ssl", false)
        .put("replication_method", replicationMethod)
        .build());
  }

  private Database getDatabaseFromConfig(JsonNode config) {
    return Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:postgresql://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()),
        "org.postgresql.Driver",
        SQLDialect.POSTGRES);
  }

  @Test
  void testCheckWithoutPublication() throws SQLException {
    database.query(ctx -> ctx.execute("DROP PUBLICATION " + PUBLICATION + ";"));
    final AirbyteConnectionStatus status = source.check(config);
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
  }

  @Test
  void testCheckWithoutReplicationSlot() throws SQLException {
    final String fullReplicationSlot = SLOT_NAME_BASE + "_" + dbName;
    database.query(ctx -> ctx.execute("SELECT pg_drop_replication_slot('" + fullReplicationSlot + "');"));

    final AirbyteConnectionStatus status = source.check(config);
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
  }

  @Test
  void testReadWithoutPublication() throws SQLException {
    database.query(ctx -> ctx.execute("DROP PUBLICATION " + PUBLICATION + ";"));

    assertThrows(Exception.class, () -> {
      source.read(config, CONFIGURED_CATALOG, null);
    });
  }

  @Test
  void testReadWithoutReplicationSlot() throws SQLException {
    final String fullReplicationSlot = SLOT_NAME_BASE + "_" + dbName;
    database.query(ctx -> ctx.execute("SELECT pg_drop_replication_slot('" + fullReplicationSlot + "');"));

    assertThrows(Exception.class, () -> {
      source.read(config, CONFIGURED_CATALOG, null);
    });
  }

  @Override
  protected void assertExpectedStateMessages(List<AirbyteStateMessage> stateMessages) {
    assertEquals(1, stateMessages.size());
    assertNotNull(stateMessages.get(0).getData());
  }

  @Override
  protected CdcTargetPosition cdcLatestTargetPosition() {
    JdbcDatabase database = Databases.createJdbcDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:postgresql://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()),
        "org.postgresql.Driver");
    return PostgresCdcTargetPosition.targetPosition(database);
  }

  @Override
  protected CdcTargetPosition extractPosition(JsonNode record) {
    return new PostgresCdcTargetPosition(PgLsn.fromLong(record.get(CDC_LSN).asLong()));
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
  protected void removeCDCColumns(ObjectNode data) {
    data.remove(CDC_LSN);
    data.remove(CDC_UPDATED_AT);
    data.remove(CDC_DELETED_AT);
  }

  @Override
  protected void addCdcMetadataColumns(AirbyteStream stream) {
    ObjectNode jsonSchema = (ObjectNode) stream.getJsonSchema();
    ObjectNode properties = (ObjectNode) jsonSchema.get("properties");

    final JsonNode stringType = Jsons.jsonNode(ImmutableMap.of("type", "string"));
    final JsonNode numberType = Jsons.jsonNode(ImmutableMap.of("type", "number"));
    properties.set(CDC_LSN, numberType);
    properties.set(CDC_UPDATED_AT, stringType);
    properties.set(CDC_DELETED_AT, stringType);

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
  public String createSchemaQuery(String schemaName) {
    return "CREATE SCHEMA " + schemaName + ";";
  }

}
