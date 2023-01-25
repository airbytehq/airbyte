/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_DELETED_AT;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_UPDATED_AT;
import static io.airbyte.integrations.source.mysql.MySqlSource.CDC_LOG_FILE;
import static io.airbyte.integrations.source.mysql.MySqlSource.CDC_LOG_POS;
import static io.airbyte.integrations.source.mysql.MySqlSource.DRIVER_CLASS;
import static io.airbyte.integrations.source.mysql.MySqlSource.MYSQL_CDC_OFFSET;
import static io.airbyte.integrations.source.mysql.MySqlSource.MYSQL_DB_HISTORY;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.debezium.CdcSourceTest;
import io.airbyte.integrations.debezium.CdcTargetPosition;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import java.sql.SQLException;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import javax.sql.DataSource;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.testcontainers.containers.MySQLContainer;
import uk.org.webcompere.systemstubs.environment.EnvironmentVariables;
import uk.org.webcompere.systemstubs.jupiter.SystemStub;
import uk.org.webcompere.systemstubs.jupiter.SystemStubsExtension;

@ExtendWith(SystemStubsExtension.class)
public class CdcMysqlSourceTest extends CdcSourceTest {

  @SystemStub
  private EnvironmentVariables environmentVariables;

  private static final String DB_NAME = MODELS_SCHEMA;
  private MySQLContainer<?> container;
  private Database database;
  private MySqlSource source;
  private JsonNode config;

  @BeforeEach
  public void setup() throws SQLException {
    environmentVariables.set(EnvVariableFeatureFlags.USE_STREAM_CAPABLE_STATE, "true");
    init();
    revokeAllPermissions();
    grantCorrectPermissions();
    super.setup();
  }

  private void init() {
    container = new MySQLContainer<>("mysql:8.0");
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
        .put("time_zone", "America/Los_Angeles")
        .build());

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("database", DB_NAME)
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .put("replication_method", replicationMethod)
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

  private void purgeAllBinaryLogs() {
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
  protected CdcTargetPosition cdcLatestTargetPosition() {
    final DataSource dataSource = DataSourceFactory.create(
        "root",
        "test",
        DRIVER_CLASS,
        String.format("jdbc:mysql://%s:%s",
            container.getHost(),
            container.getFirstMappedPort()),
        Collections.emptyMap());
    final JdbcDatabase jdbcDatabase = new DefaultJdbcDatabase(dataSource);

    return MySqlCdcTargetPosition.targetPosition(jdbcDatabase);
  }

  @Override
  protected CdcTargetPosition extractPosition(final JsonNode record) {
    return new MySqlCdcTargetPosition(record.get(CDC_LOG_FILE).asText(), record.get(CDC_LOG_POS).asInt());
  }

  @Override
  protected void assertNullCdcMetaData(final JsonNode data) {
    assertNull(data.get(CDC_LOG_FILE));
    assertNull(data.get(CDC_LOG_POS));
    assertNull(data.get(CDC_UPDATED_AT));
    assertNull(data.get(CDC_DELETED_AT));
  }

  @Override
  protected void assertCdcMetaData(final JsonNode data, final boolean deletedAtNull) {
    assertNotNull(data.get(CDC_LOG_FILE));
    assertNotNull(data.get(CDC_LOG_POS));
    assertNotNull(data.get(CDC_UPDATED_AT));
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
  }

  @Override
  protected void addCdcMetadataColumns(final AirbyteStream stream) {
    final ObjectNode jsonSchema = (ObjectNode) stream.getJsonSchema();
    final ObjectNode properties = (ObjectNode) jsonSchema.get("properties");

    final JsonNode numberType = Jsons.jsonNode(ImmutableMap.of("type", "number"));

    final JsonNode stringType = Jsons.jsonNode(ImmutableMap.of("type", "string"));
    properties.set(CDC_LOG_FILE, stringType);
    properties.set(CDC_LOG_POS, numberType);
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
  public void assertExpectedStateMessages(final List<AirbyteStateMessage> stateMessages) {
    for (final AirbyteStateMessage stateMessage : stateMessages) {
      assertNotNull(stateMessage.getData().get("cdc_state").get("state").get(MYSQL_CDC_OFFSET));
      assertNotNull(stateMessage.getData().get("cdc_state").get("state").get(MYSQL_DB_HISTORY));
    }
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
    assertEquals(1, stateAfterFirstBatch.size());
    assertNotNull(stateAfterFirstBatch.get(0).getData());
    assertExpectedStateMessages(stateAfterFirstBatch);
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

    final JsonNode state = Jsons.jsonNode(stateAfterFirstBatch);
    final AutoCloseableIterator<AirbyteMessage> secondBatchIterator = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, state);
    final List<AirbyteMessage> dataFromSecondBatch = AutoCloseableIterators
        .toListAndClose(secondBatchIterator);

    final List<AirbyteStateMessage> stateAfterSecondBatch = extractStateMessages(dataFromSecondBatch);
    assertEquals(1, stateAfterSecondBatch.size());
    assertNotNull(stateAfterSecondBatch.get(0).getData());
    assertExpectedStateMessages(stateAfterSecondBatch);

    final Set<AirbyteRecordMessage> recordsFromSecondBatch = extractRecordMessages(
        dataFromSecondBatch);
    assertEquals((recordsToCreate * 2) + recordsCreatedBeforeTestCount, recordsFromSecondBatch.size(),
        "Expected 46 records to be replicated in the second sync.");
  }

}
