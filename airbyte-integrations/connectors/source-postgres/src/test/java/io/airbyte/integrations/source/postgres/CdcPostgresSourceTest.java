/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_DELETED_AT;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_LSN;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_UPDATED_AT;
import static io.airbyte.integrations.source.jdbc.test.JdbcSourceAcceptanceTest.setEnv;
import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
import static org.assertj.core.api.AssertionsForClassTypes.catchThrowable;
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
import com.google.common.collect.Lists;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.Database;
import io.airbyte.db.PgLsn;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.debezium.CdcSourceTest;
import io.airbyte.integrations.debezium.CdcTargetPosition;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.SyncMode;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.sql.SQLException;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.DockerImageName;
import org.testcontainers.utility.MountableFile;

abstract class CdcPostgresSourceTest extends CdcSourceTest {

  protected static final String SLOT_NAME_BASE = "debezium_slot";
  protected static final String PUBLICATION = "publication";
  protected static final int INITIAL_WAITING_SECONDS = 5;
  private PostgreSQLContainer<?> container;

  protected String dbName;
  protected Database database;
  private DSLContext dslContext;
  private PostgresSource source;
  private JsonNode config;
  private String fullReplicationSlot;

  protected abstract String getPluginName();

  @AfterEach
  void tearDown() {
    dslContext.close();
    container.close();
  }

  @BeforeEach
  protected void setup() throws SQLException {
    final DockerImageName myImage = DockerImageName.parse("debezium/postgres:13-alpine").asCompatibleSubstituteFor("postgres");
    container = new PostgreSQLContainer<>(myImage)
        .withCopyFileToContainer(MountableFile.forClasspathResource("postgresql.conf"), "/etc/postgresql/postgresql.conf")
        .withCommand("postgres -c config_file=/etc/postgresql/postgresql.conf");
    container.start();
    setEnv(EnvVariableFeatureFlags.USE_STREAM_CAPABLE_STATE, "true");
    source = new PostgresSource();
    dbName = Strings.addRandomSuffix("db", "_", 10).toLowerCase();

    final String initScriptName = "init_" + dbName.concat(".sql");
    final String tmpFilePath = IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE " + dbName + ";");
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), container);

    config = getConfig(dbName);
    fullReplicationSlot = SLOT_NAME_BASE + "_" + dbName;
    dslContext = getDslContext(config);
    database = getDatabase(dslContext);
    super.setup();
    database.query(ctx -> {
      ctx.execute("SELECT pg_create_logical_replication_slot('" + fullReplicationSlot + "', '" + getPluginName() + "');");
      ctx.execute("CREATE PUBLICATION " + PUBLICATION + " FOR ALL TABLES;");

      return null;
    });

  }

  private JsonNode getConfig(final String dbName) {
    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("replication_slot", SLOT_NAME_BASE + "_" + dbName)
        .put("publication", PUBLICATION)
        .put("plugin", getPluginName())
        .put("initial_waiting_seconds", INITIAL_WAITING_SECONDS)
        .build());

    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, container.getHost())
        .put(JdbcUtils.PORT_KEY, container.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, dbName)
        .put(JdbcUtils.SCHEMAS_KEY, List.of(MODELS_SCHEMA, MODELS_SCHEMA + "_random"))
        .put(JdbcUtils.USERNAME_KEY, container.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, container.getPassword())
        .put(JdbcUtils.SSL_KEY, false)
        .put("is_test", true)
        .put("replication_method", replicationMethod)
        .build());
  }

  private static Database getDatabase(final DSLContext dslContext) {
    return new Database(dslContext);
  }

  private static DSLContext getDslContext(final JsonNode config) {
    return DSLContextFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt(),
            config.get(JdbcUtils.DATABASE_KEY).asText()),
        SQLDialect.POSTGRES);
  }

  @Test
  void testCheckWithoutPublication() throws Exception {
    database.query(ctx -> ctx.execute("DROP PUBLICATION " + PUBLICATION + ";"));

    final Throwable throwable = catchThrowable(() -> source.check(config));
    assertThat(throwable.getMessage()
        .contains("Expected exactly one publication slot but found 0. Please read the docs and add a replication slot to your database."));
  }

  @Test
  void testCheckWithoutReplicationSlot() throws Exception {
    final String fullReplicationSlot = SLOT_NAME_BASE + "_" + dbName;
    database.query(ctx -> ctx.execute("SELECT pg_drop_replication_slot('" + fullReplicationSlot + "');"));

    final Throwable throwable = catchThrowable(() -> source.check(config));
    assertThat(throwable.getMessage()
        .contains("Expected exactly one publication slot but found 0. Please read the docs and add a replication slot to your database."));
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
  protected void assertExpectedStateMessages(final List<AirbyteStateMessage> stateMessages) {
    assertEquals(1, stateMessages.size());
    assertNotNull(stateMessages.get(0).getData());
  }

  @Override
  protected CdcTargetPosition cdcLatestTargetPosition() {
    final JdbcDatabase database = new DefaultJdbcDatabase(
        DataSourceFactory.create(
            config.get(JdbcUtils.USERNAME_KEY).asText(),
            config.get(JdbcUtils.PASSWORD_KEY).asText(),
            DatabaseDriver.POSTGRESQL.getDriverClassName(),
            String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
                config.get(JdbcUtils.HOST_KEY).asText(),
                config.get(JdbcUtils.PORT_KEY).asInt(),
                config.get(JdbcUtils.DATABASE_KEY).asText())));

    return PostgresCdcTargetPosition.targetPosition(database);
  }

  @Override
  protected CdcTargetPosition extractPosition(final JsonNode record) {
    return new PostgresCdcTargetPosition(PgLsn.fromLong(record.get(CDC_LSN).asLong()));
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
  protected void removeCDCColumns(final ObjectNode data) {
    data.remove(CDC_LSN);
    data.remove(CDC_UPDATED_AT);
    data.remove(CDC_DELETED_AT);
  }

  @Override
  protected void addCdcMetadataColumns(final AirbyteStream stream) {
    final ObjectNode jsonSchema = (ObjectNode) stream.getJsonSchema();
    final ObjectNode properties = (ObjectNode) jsonSchema.get("properties");

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
  public String createSchemaQuery(final String schemaName) {
    return "CREATE SCHEMA " + schemaName + ";";
  }

  @Override
  protected String randomTableSchema() {
    return MODELS_SCHEMA + "_random";
  }

  @Test
  public void testTableWithTimestampColDefault() throws Exception {
    createAndPopulateTimestampTable();
    final AirbyteCatalog catalog = new AirbyteCatalog().withStreams(List.of(
        CatalogHelpers.createAirbyteStream("time_stamp_table", MODELS_SCHEMA,
            Field.of("id", JsonSchemaType.NUMBER),
            Field.of("name", JsonSchemaType.STRING),
            Field.of("created_at", JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of("id")))));
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers
        .toDefaultConfiguredCatalog(catalog);

    // set all streams to incremental.
    configuredCatalog.getStreams().forEach(s -> s.setSyncMode(SyncMode.INCREMENTAL));
    final AutoCloseableIterator<AirbyteMessage> firstBatchIterator = getSource()
        .read(getConfig(), configuredCatalog, null);
    final List<AirbyteMessage> dataFromFirstBatch = AutoCloseableIterators
        .toListAndClose(firstBatchIterator);
    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessages(dataFromFirstBatch);
    assertEquals(1, stateAfterFirstBatch.size());
    assertNotNull(stateAfterFirstBatch.get(0).getData());
    assertExpectedStateMessages(stateAfterFirstBatch);
    final Set<AirbyteRecordMessage> recordsFromFirstBatch = extractRecordMessages(
        dataFromFirstBatch);

    assertEquals(6, recordsFromFirstBatch.size());
  }

  private void createAndPopulateTimestampTable() {
    createTable(MODELS_SCHEMA, "time_stamp_table",
        columnClause(ImmutableMap.of("id", "INTEGER", "name", "VARCHAR(200)", "created_at", "TIMESTAMPTZ NOT NULL DEFAULT NOW()"),
            Optional.of("id")));
    final List<JsonNode> timestampRecords = ImmutableList.of(
        Jsons
            .jsonNode(ImmutableMap
                .of("id", 11000, "name", "blah1")),
        Jsons.jsonNode(ImmutableMap
            .of("id", 12000, "name", "blah2")),
        Jsons
            .jsonNode(ImmutableMap
                .of("id", 13000, "name", "blah3")),
        Jsons.jsonNode(ImmutableMap
            .of("id", 14000, "name", "blah4")),
        Jsons.jsonNode(ImmutableMap
            .of("id", 15000, "name", "blah5")),
        Jsons
            .jsonNode(ImmutableMap
                .of("id", 16000, "name", "blah6")));
    for (final JsonNode recordJson : timestampRecords) {
      executeQuery(
          String.format("INSERT INTO %s.%s (%s, %s) VALUES (%s, '%s');", MODELS_SCHEMA, "time_stamp_table",
              "id", "name",
              recordJson.get("id").asInt(), recordJson.get("name").asText()));
    }
  }

  @Test
  protected void syncShouldHandlePurgedLogsGracefully() throws Exception {

    final int recordsToCreate = 20;

    final AutoCloseableIterator<AirbyteMessage> firstBatchIterator = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, null);
    final List<AirbyteMessage> dataFromFirstBatch = AutoCloseableIterators
        .toListAndClose(firstBatchIterator);
    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessages(dataFromFirstBatch);

    // second batch of records again 20 being created
    for (int recordsCreated = 0; recordsCreated < recordsToCreate; recordsCreated++) {
      final JsonNode record =
          Jsons.jsonNode(ImmutableMap
              .of(COL_ID, 200 + recordsCreated, COL_MAKE_ID, 1, COL_MODEL,
                  "F-" + recordsCreated));
      writeModelRecord(record);
    }

    final JsonNode state = Jsons.jsonNode(stateAfterFirstBatch);
    final AutoCloseableIterator<AirbyteMessage> secondBatchIterator = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, state);
    final List<AirbyteMessage> dataFromSecondBatch = AutoCloseableIterators
        .toListAndClose(secondBatchIterator);
    final List<AirbyteStateMessage> stateAfterSecondBatch = extractStateMessages(dataFromSecondBatch);
    assertExpectedStateMessages(stateAfterSecondBatch);

    for (int recordsCreated = 0; recordsCreated < 1; recordsCreated++) {
      final JsonNode record =
          Jsons.jsonNode(ImmutableMap
              .of(COL_ID, 400 + recordsCreated, COL_MAKE_ID, 1, COL_MODEL,
                  "H-" + recordsCreated));
      writeModelRecord(record);
    }

    // Triggering sync with the first sync's state only which would mimic a scenario that the second
    // sync failed on destination end and we didn't save state
    final AutoCloseableIterator<AirbyteMessage> thirdBatchIterator = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, state);

    final List<AirbyteMessage> dataFromThirdBatch = AutoCloseableIterators
        .toListAndClose(thirdBatchIterator);

    final List<AirbyteStateMessage> stateAfterThirdBatch = extractStateMessages(dataFromThirdBatch);
    assertExpectedStateMessages(stateAfterThirdBatch);
    final Set<AirbyteRecordMessage> recordsFromThirdBatch = extractRecordMessages(
        dataFromThirdBatch);

    assertEquals(MODEL_RECORDS.size() + recordsToCreate + 1, recordsFromThirdBatch.size());
  }

}
