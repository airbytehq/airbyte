/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static io.airbyte.integrations.source.mssql.MssqlSource.IS_COMPRESSED;
import static io.airbyte.integrations.source.mssql.MssqlSource.MSSQL_CDC_OFFSET;
import static io.airbyte.integrations.source.mssql.MssqlSource.MSSQL_DB_HISTORY;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Iterables;
import com.google.common.collect.Lists;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateGeneratorUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.stream.Collectors;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CdcStateCompressionTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(CdcStateCompressionTest.class);

  static private final String CDC_ROLE_NAME = "cdc_selector";

  static private final String TEST_USER_NAME_PREFIX = "cdc_test_user";

  static private final String TEST_SCHEMA = "test_schema";

  static private final int TEST_TABLES = 4;

  // SQLServer tables can't have more than 1024 columns.
  static private final int ADDED_COLUMNS = 1000;

  private MsSQLTestDatabase testdb;
  private final ExecutorService executor = Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors());
  private static final String ALTER_TABLE_ADD_COLUMN_SQL;
  static {
    StringBuilder sb = new StringBuilder();
    sb.append("ALTER TABLE ").append(TEST_SCHEMA).append(".%s ADD");
    for (int j = 0; j < ADDED_COLUMNS; j++) {
      sb.append((j > 0) ? ", " : " ")
          // Sqlserver column names can't be longer than 128 characters
          .append("rather_long_column_name_________________________________________________________________________________________").append(j)
          .append(" INT NULL");
    }
    ALTER_TABLE_ADD_COLUMN_SQL = sb.toString();
  }

  @BeforeEach
  public void setup() throws Exception {
    testdb = MsSQLTestDatabase.in(MsSQLTestDatabase.BaseImage.MSSQL_2022, MsSQLTestDatabase.ContainerModifier.AGENT)
        .withWaitUntilAgentRunning()
        .withCdc();

    // Create a test schema and a bunch of test tables with CDC enabled.
    // Insert one row in each table so that they're not empty.
    testdb.with("CREATE SCHEMA %s;", TEST_SCHEMA);
    List<Callable<MsSQLTestDatabase>> createAndPopulateTableTasks = new ArrayList<>();
    List<Callable<MsSQLTestDatabase>> waitForCdcRecordTasks = new ArrayList<>();
    List<Callable<MsSQLTestDatabase>> alterTabletasks = new ArrayList<>();
    List<Callable<MsSQLTestDatabase>> enableTableCdctasks = new ArrayList<>();
    List<Callable<MsSQLTestDatabase>> disableTableCdctasks = new ArrayList<>();

    for (int i = 0; i < TEST_TABLES; i++) {
      String tableName = "test_table_%d".formatted(i);
      String initialCdcInstanceName = "capture_instance_%d_%d".formatted(i, 1);
      String finalCdcInstanceName = "capture_instance_%d_%d".formatted(i, 2);
      createAndPopulateTableTasks.add(() -> testdb
          .with("CREATE TABLE %s.%s (id INT IDENTITY(1,1) PRIMARY KEY);", TEST_SCHEMA, tableName)
          .withCdcForTable(TEST_SCHEMA, tableName, CDC_ROLE_NAME, initialCdcInstanceName)
          .with("INSERT INTO %s.%s DEFAULT VALUES", TEST_SCHEMA, tableName));
      waitForCdcRecordTasks.add(() -> testdb.waitForCdcRecords(TEST_SCHEMA, tableName, initialCdcInstanceName, 1));

      // Increase schema history size to trigger state compression.
      // We do this by adding lots of columns with long names,
      // then migrating to a new CDC capture instance for each table.
      // This is admittedly somewhat awkward and perhaps could be improved.
      alterTabletasks.add(() -> testdb.with(ALTER_TABLE_ADD_COLUMN_SQL.formatted(tableName)));
      enableTableCdctasks.add(() -> testdb.withCdcForTable(TEST_SCHEMA, tableName, CDC_ROLE_NAME, finalCdcInstanceName));
      disableTableCdctasks.add(() -> testdb.withCdcDisabledForTable(TEST_SCHEMA, tableName, initialCdcInstanceName));
    }
    executor.invokeAll(createAndPopulateTableTasks);
    executor.invokeAll(waitForCdcRecordTasks);

    // Create a test user to be used by the source, with proper permissions.
    testdb
        .with("CREATE LOGIN %s WITH PASSWORD = '%s', DEFAULT_DATABASE = %s", testUserName(), testdb.getPassword(), testdb.getDatabaseName())
        .with("CREATE USER %s FOR LOGIN %s WITH DEFAULT_SCHEMA = [dbo]", testUserName(), testUserName())
        .with("REVOKE ALL FROM %s CASCADE;", testUserName())
        .with("EXEC sp_msforeachtable \"REVOKE ALL ON '?' TO %s;\"", testUserName())
        .with("GRANT SELECT ON SCHEMA :: [%s] TO %s", TEST_SCHEMA, testUserName())
        .with("GRANT SELECT ON SCHEMA :: [cdc] TO %s", testUserName())
        .with("USE [master]")
        .with("GRANT VIEW SERVER STATE TO %s", testUserName())
        .with("USE [%s]", testdb.getDatabaseName())
        .with("EXEC sp_addrolemember N'%s', N'%s';", CDC_ROLE_NAME, testUserName());
    executor.invokeAll(alterTabletasks);
    executor.invokeAll(enableTableCdctasks);
    executor.invokeAll(disableTableCdctasks);
  }

  private AirbyteCatalog getCatalog() {
    final var streams = new ArrayList<AirbyteStream>();
    for (int i = 0; i < TEST_TABLES; i++) {
      streams.add(CatalogHelpers.createAirbyteStream(
          "test_table_%d".formatted(i),
          TEST_SCHEMA,
          Field.of("id", JsonSchemaType.INTEGER))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
          .withSourceDefinedPrimaryKey(List.of(List.of("id"))));
    }
    return new AirbyteCatalog().withStreams(streams);
  }

  private ConfiguredAirbyteCatalog getConfiguredCatalog() {
    final var configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(getCatalog());
    configuredCatalog.getStreams().forEach(s -> s.setSyncMode(SyncMode.INCREMENTAL));
    return configuredCatalog;
  }

  private MssqlSource source() {
    return new MssqlSource();
  }

  private JsonNode config() {
    return testdb.configBuilder()
        .withHostAndPort()
        .withDatabase()
        .with(JdbcUtils.USERNAME_KEY, testUserName())
        .with(JdbcUtils.PASSWORD_KEY, testdb.getPassword())
        .withSchemas(TEST_SCHEMA)
        .withoutSsl()
        // Configure for CDC replication but with a higher timeout than usual.
        // This is because Debezium requires more time than usual to build the initial snapshot.
        .with("is_test", true)
        .with("replication_method", Map.of(
            "method", "CDC",
            "initial_waiting_seconds", 20))
        .build();
  }

  private String testUserName() {
    return testdb.withNamespace(TEST_USER_NAME_PREFIX);
  }

  /**
   * This test is similar in principle to CdcMysqlSourceTest.testCompressedSchemaHistory.
   */
  @Test
  public void testCompressedSchemaHistory() throws Exception {
    // First sync.
    final var firstBatchIterator = source().read(config(), getConfiguredCatalog(), null);
    final var dataFromFirstBatch = AutoCloseableIterators.toListAndClose(firstBatchIterator);
    final AirbyteStateMessage lastStateMessageFromFirstBatch =
        StateGeneratorUtils.convertLegacyStateToGlobalState(Iterables.getLast(extractStateMessages(dataFromFirstBatch)));
    assertNotNull(lastStateMessageFromFirstBatch.getGlobal().getSharedState());
    final var lastSharedStateFromFirstBatch = lastStateMessageFromFirstBatch.getGlobal().getSharedState().get("state");
    assertNotNull(lastSharedStateFromFirstBatch);
    assertNotNull(lastSharedStateFromFirstBatch.get(MSSQL_DB_HISTORY));
    assertNotNull(lastSharedStateFromFirstBatch.get(MSSQL_CDC_OFFSET));
    assertNotNull(lastSharedStateFromFirstBatch.get(IS_COMPRESSED));
    assertTrue(lastSharedStateFromFirstBatch.get(IS_COMPRESSED).asBoolean());
    final var recordsFromFirstBatch = extractRecordMessages(dataFromFirstBatch);
    assertEquals(TEST_TABLES, recordsFromFirstBatch.size());
    for (final var record : recordsFromFirstBatch) {
      assertEquals("1", record.getData().get("id").toString());
    }

    LOGGER.info("inserting new data into test tables");
    List<Callable<MsSQLTestDatabase>> waitForCdcTasks = new ArrayList<>();
    // Insert a bunch of records (1 per table, again).
    for (int i = 0; i < TEST_TABLES; i++) {
      String tableName = "test_table_%d".formatted(i);
      String cdcInstanceName = "capture_instance_%d_%d".formatted(i, 2);
      testdb.with("INSERT %s.%s DEFAULT VALUES;", TEST_SCHEMA, tableName);
      waitForCdcTasks.add(() -> testdb.waitForCdcRecords(TEST_SCHEMA, tableName, cdcInstanceName, 1));
    }
    LOGGER.info("waiting for CDC records");
    executor.invokeAll(waitForCdcTasks);

    LOGGER.info("starting second sync");
    // Second sync.
    final var secondBatchStateForRead = Jsons.jsonNode(Collections.singletonList(Iterables.getLast(extractStateMessages(dataFromFirstBatch))));
    final var secondBatchIterator = source().read(config(), getConfiguredCatalog(), secondBatchStateForRead);
    final var dataFromSecondBatch = AutoCloseableIterators.toListAndClose(secondBatchIterator);
    final AirbyteStateMessage lastStateMessageFromSecondBatch =
        StateGeneratorUtils.convertLegacyStateToGlobalState(Iterables.getLast(extractStateMessages(dataFromSecondBatch)));
    assertNotNull(lastStateMessageFromSecondBatch.getGlobal().getSharedState());
    final var lastSharedStateFromSecondBatch = lastStateMessageFromSecondBatch.getGlobal().getSharedState().get("state");
    assertNotNull(lastSharedStateFromSecondBatch);
    assertNotNull(lastSharedStateFromSecondBatch.get(MSSQL_DB_HISTORY));
    assertEquals(lastSharedStateFromFirstBatch.get(MSSQL_DB_HISTORY), lastSharedStateFromSecondBatch.get(MSSQL_DB_HISTORY));
    assertNotNull(lastSharedStateFromSecondBatch.get(MSSQL_CDC_OFFSET));
    assertNotNull(lastSharedStateFromSecondBatch.get(IS_COMPRESSED));
    assertTrue(lastSharedStateFromSecondBatch.get(IS_COMPRESSED).asBoolean());
    final var recordsFromSecondBatch = extractRecordMessages(dataFromSecondBatch);
    assertEquals(TEST_TABLES, recordsFromSecondBatch.size());
    for (final var record : recordsFromSecondBatch) {
      assertEquals("2", record.getData().get("id").toString());
    }
  }

  @AfterEach
  public void tearDown() {
    testdb.close();
  }

  private Set<AirbyteRecordMessage> extractRecordMessages(final List<AirbyteMessage> messages) {
    final var recordsPerStream = extractRecordMessagesStreamWise(messages);
    return recordsPerStream.values().stream().flatMap(Set::stream).collect(Collectors.toSet());
  }

  private Map<String, Set<AirbyteRecordMessage>> extractRecordMessagesStreamWise(final List<AirbyteMessage> messages) {
    final var recordsPerStream = messages.stream()
        .filter(m -> m.getType() == Type.RECORD)
        .map(AirbyteMessage::getRecord)
        .collect(Collectors.groupingBy(AirbyteRecordMessage::getStream));

    final Map<String, Set<AirbyteRecordMessage>> recordsPerStreamWithNoDuplicates = new HashMap<>();
    for (final var entry : recordsPerStream.entrySet()) {
      final var set = new HashSet<>(entry.getValue());
      recordsPerStreamWithNoDuplicates.put(entry.getKey(), set);
      assertEquals(entry.getValue().size(), set.size(), "duplicate records in sync for " + entry.getKey());
    }

    return recordsPerStreamWithNoDuplicates;
  }

  private List<AirbyteStateMessage> extractStateMessages(final List<AirbyteMessage> messages) {
    return messages.stream()
        .filter(r -> r.getType() == Type.STATE)
        .map(AirbyteMessage::getState)
        .toList();
  }

}
