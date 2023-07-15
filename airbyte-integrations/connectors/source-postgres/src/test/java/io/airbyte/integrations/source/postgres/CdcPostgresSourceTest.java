/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_DELETED_AT;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_LSN;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_UPDATED_AT;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
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
import io.airbyte.integrations.debezium.internals.postgres.PostgresCdcTargetPosition;
import io.airbyte.integrations.debezium.internals.postgres.PostgresReplicationConnection;
import io.airbyte.integrations.util.ConnectorExceptionUtil;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.SyncMode;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.sql.SQLException;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.DockerImageName;
import org.testcontainers.utility.MountableFile;
import uk.org.webcompere.systemstubs.environment.EnvironmentVariables;
import uk.org.webcompere.systemstubs.jupiter.SystemStub;
import uk.org.webcompere.systemstubs.jupiter.SystemStubsExtension;

@ExtendWith(SystemStubsExtension.class)
public class CdcPostgresSourceTest extends CdcSourceTest {

  @SystemStub
  private EnvironmentVariables environmentVariables;

  protected static final String SLOT_NAME_BASE = "debezium_slot";
  protected static final String PUBLICATION = "publication";
  protected static final int INITIAL_WAITING_SECONDS = 30;
  private PostgreSQLContainer<?> container;

  protected String dbName;
  protected Database database;
  private DSLContext dslContext;
  private PostgresSource source;
  private JsonNode config;
  private String fullReplicationSlot;
  private final String cleanUserName = "airbyte_test";
  private final String cleanUserPassword = "password";

  protected String getPluginName() {
    return "pgoutput";
  }

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
    environmentVariables.set(EnvVariableFeatureFlags.USE_STREAM_CAPABLE_STATE, "true");
    source = new PostgresSource();
    dbName = Strings.addRandomSuffix("db", "_", 10).toLowerCase();

    final String initScriptName = "init_" + dbName.concat(".sql");
    final String tmpFilePath = IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE " + dbName + ";");
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), container);

    config = getConfig(dbName, container.getUsername(), container.getPassword());
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

  private JsonNode getConfig(final String dbName, final String userName, final String userPassword) {
    final JsonNode replicationMethod = getReplicationMethod(dbName);
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, container.getHost())
        .put(JdbcUtils.PORT_KEY, container.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, dbName)
        .put(JdbcUtils.SCHEMAS_KEY, List.of(MODELS_SCHEMA, MODELS_SCHEMA + "_random"))
        .put(JdbcUtils.USERNAME_KEY, userName)
        .put(JdbcUtils.PASSWORD_KEY, userPassword)
        .put(JdbcUtils.SSL_KEY, false)
        .put("is_test", true)
        .put("replication_method", replicationMethod)
        .put("sync_checkpoint_records", 1)
        .build());
  }

  private JsonNode getReplicationMethod(final String dbName) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "CDC")
        .put("replication_slot", SLOT_NAME_BASE + "_" + dbName)
        .put("publication", PUBLICATION)
        .put("plugin", getPluginName())
        .put("initial_waiting_seconds", INITIAL_WAITING_SECONDS)
        .put("lsn_commit_behaviour", "After loading Data in the destination")
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

  /**
   * Creates a new user without privileges for the access tests
   */
  private void createCleanUser() {
    executeQuery("CREATE USER " + cleanUserName + " PASSWORD '" + cleanUserPassword + "';");
  }

  /**
   * Grants privilege to a user (SUPERUSER, REPLICATION, ...)
   */
  private void grantUserPrivilege(final String userName, final String postgresPrivilege) {
    executeQuery("ALTER USER " + userName + " " + postgresPrivilege + ";");
  }

  @Test
  void testCheckReplicationAccessSuperUserPrivilege() throws Exception {
    createCleanUser();
    final JsonNode test_config = getConfig(dbName, cleanUserName, cleanUserPassword);
    grantUserPrivilege(cleanUserName, "SUPERUSER");
    final AirbyteConnectionStatus status = source.check(test_config);
    assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, status.getStatus());
  }

  @Test
  void testCheckReplicationAccessReplicationPrivilege() throws Exception {
    createCleanUser();
    final JsonNode test_config = getConfig(dbName, cleanUserName, cleanUserPassword);
    grantUserPrivilege(cleanUserName, "REPLICATION");
    final AirbyteConnectionStatus status = source.check(test_config);
    assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, status.getStatus());
  }

  @Test
  void testCheckWithoutReplicationPermission() throws Exception {
    createCleanUser();
    final JsonNode test_config = getConfig(dbName, cleanUserName, cleanUserPassword);
    final AirbyteConnectionStatus status = source.check(test_config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertEquals(String.format(ConnectorExceptionUtil.COMMON_EXCEPTION_MESSAGE_TEMPLATE,
        String.format(PostgresReplicationConnection.REPLICATION_PRIVILEGE_ERROR_MESSAGE, test_config.get("username").asText())),
        status.getMessage());
  }

  @Test
  void testCheckWithoutPublication() throws Exception {
    database.query(ctx -> ctx.execute("DROP PUBLICATION " + PUBLICATION + ";"));
    final AirbyteConnectionStatus status = source.check(getConfig());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
  }

  @Test
  void testCheckWithoutReplicationSlot() throws Exception {
    final String fullReplicationSlot = SLOT_NAME_BASE + "_" + dbName;
    database.query(ctx -> ctx.execute("SELECT pg_drop_replication_slot('" + fullReplicationSlot + "');"));

    final AirbyteConnectionStatus status = source.check(getConfig());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
  }

  @Override
  protected void assertExpectedStateMessages(final List<AirbyteStateMessage> stateMessages) {
    assertEquals(1, stateMessages.size());
    assertNotNull(stateMessages.get(0).getData());
  }

  @Override
  protected PostgresCdcTargetPosition cdcLatestTargetPosition() {
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
  protected PostgresCdcTargetPosition extractPosition(final JsonNode record) {
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
  protected void addCdcDefaultCursorField(final AirbyteStream stream) {
    stream.setDefaultCursorField(ImmutableList.of(CDC_LSN));
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
  void testDiscoverFiltersNonPublication() throws Exception {
    // Drop the default publication (which is created for all tables). Create a publication for the
    // models table. By default,
    // the tests create a models_schema.models table and models_schema_random.models_random table. We
    // will create a publication
    // for one of the tests and assert that both streams end up in the catalog. However, the stream that
    // is not associated with
    // a publication should only have SyncMode.FULL_REFRESH as a supported sync mode.
    database.query(ctx -> ctx.execute("DROP PUBLICATION " + PUBLICATION + ";"));
    database.query(ctx -> ctx.execute(String.format("CREATE PUBLICATION " + PUBLICATION + " FOR TABLE %s.%s", MODELS_SCHEMA, "models")));

    final AirbyteCatalog catalog = source.discover(getConfig());
    assertEquals(catalog.getStreams().size(), 2);
    final AirbyteStream streamInPublication =
        catalog.getStreams().stream().filter(stream -> stream.getName().equals("models")).findFirst().get();
    final AirbyteStream streamNotInPublication =
        catalog.getStreams().stream().filter(stream -> !stream.getName().equals("models")).findFirst().get();

    // The stream that has an associated publication should have support for source-defined incremental
    // sync.
    assertEquals(streamInPublication.getSupportedSyncModes(), List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
    assertFalse(streamInPublication.getSourceDefinedPrimaryKey().isEmpty());
    assertTrue(streamInPublication.getSourceDefinedCursor());

    // The stream that does not have an associated publication should not have support for
    // source-defined incremental sync.
    assertEquals(streamNotInPublication.getSupportedSyncModes(), List.of(SyncMode.FULL_REFRESH));
    assertTrue(streamNotInPublication.getSourceDefinedPrimaryKey().isEmpty());
    assertFalse(streamNotInPublication.getSourceDefinedCursor());
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

    final JsonNode config = getConfig();
    final JsonNode replicationMethod = ((ObjectNode) getReplicationMethod(config.get(JdbcUtils.DATABASE_KEY).asText())).put("lsn_commit_behaviour",
        "While reading Data");
    ((ObjectNode) config).put("replication_method", replicationMethod);

    final AutoCloseableIterator<AirbyteMessage> firstBatchIterator = getSource()
        .read(config, CONFIGURED_CATALOG, null);
    final List<AirbyteMessage> dataFromFirstBatch = AutoCloseableIterators
        .toListAndClose(firstBatchIterator);
    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessages(dataFromFirstBatch);
    assertExpectedStateMessages(stateAfterFirstBatch);
    // second batch of records again 20 being created
    for (int recordsCreated = 0; recordsCreated < recordsToCreate; recordsCreated++) {
      final JsonNode record =
          Jsons.jsonNode(ImmutableMap
              .of(COL_ID, 200 + recordsCreated, COL_MAKE_ID, 1, COL_MODEL,
                  "F-" + recordsCreated));
      writeModelRecord(record);
    }

    // Extract the last state message
    final JsonNode state = Jsons.jsonNode(Collections.singletonList(stateAfterFirstBatch.get(stateAfterFirstBatch.size() - 1)));
    final AutoCloseableIterator<AirbyteMessage> secondBatchIterator = getSource()
        .read(config, CONFIGURED_CATALOG, state);
    final List<AirbyteMessage> dataFromSecondBatch = AutoCloseableIterators
        .toListAndClose(secondBatchIterator);
    final List<AirbyteStateMessage> stateAfterSecondBatch = extractStateMessages(dataFromSecondBatch);
    assertExpectedStateMessagesFromIncrementalSync(stateAfterSecondBatch);

    for (int recordsCreated = 0; recordsCreated < 1; recordsCreated++) {
      final JsonNode record =
          Jsons.jsonNode(ImmutableMap
              .of(COL_ID, 400 + recordsCreated, COL_MAKE_ID, 1, COL_MODEL,
                  "H-" + recordsCreated));
      writeModelRecord(record);
    }

    // Triggering sync with the first sync's state only which would mimic a scenario that the second
    // sync failed on destination end, and we didn't save state
    final AutoCloseableIterator<AirbyteMessage> thirdBatchIterator = getSource()
        .read(config, CONFIGURED_CATALOG, state);

    final List<AirbyteMessage> dataFromThirdBatch = AutoCloseableIterators
        .toListAndClose(thirdBatchIterator);

    final List<AirbyteStateMessage> stateAfterThirdBatch = extractStateMessages(dataFromThirdBatch);
    assertStateForSyncShouldHandlePurgedLogsGracefully(stateAfterThirdBatch);
    final Set<AirbyteRecordMessage> recordsFromThirdBatch = extractRecordMessages(
        dataFromThirdBatch);

    assertEquals(MODEL_RECORDS.size() + recordsToCreate + 1, recordsFromThirdBatch.size());
  }

  protected void assertStateForSyncShouldHandlePurgedLogsGracefully(final List<AirbyteStateMessage> stateMessages) {
    assertExpectedStateMessages(stateMessages);
  }

  @Test
  void testReachedTargetPosition() {
    final PostgresCdcTargetPosition ctp = cdcLatestTargetPosition();
    final PgLsn target = ctp.targetLsn;
    assertTrue(ctp.reachedTargetPosition(target.asLong() + 1));
    assertTrue(ctp.reachedTargetPosition(target.asLong()));
    assertFalse(ctp.reachedTargetPosition(target.asLong() - 1));
    assertFalse(ctp.reachedTargetPosition((Long) null));
  }

  @Test
  protected void syncShouldIncrementLSN() throws Exception {
    final int recordsToCreate = 20;

    final DataSource dataSource = DataSourceFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt(),
            config.get(JdbcUtils.DATABASE_KEY).asText()));

    final JdbcDatabase defaultJdbcDatabase = new DefaultJdbcDatabase(dataSource);

    final Long replicationSlotAtTheBeginning = PgLsn.fromPgString(
        source.getReplicationSlot(defaultJdbcDatabase, getConfig()).get(0).get("confirmed_flush_lsn").asText()).asLong();

    final AutoCloseableIterator<AirbyteMessage> firstBatchIterator = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, null);
    final List<AirbyteMessage> dataFromFirstBatch = AutoCloseableIterators
        .toListAndClose(firstBatchIterator);
    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessages(dataFromFirstBatch);

    final Long replicationSlotAfterFirstSync = PgLsn.fromPgString(
        source.getReplicationSlot(defaultJdbcDatabase, getConfig()).get(0).get("confirmed_flush_lsn").asText()).asLong();

    // First sync should not make any change to the replication slot status
    assertLsnPositionForSyncShouldIncrementLSN(replicationSlotAtTheBeginning, replicationSlotAfterFirstSync, 1);

    // second batch of records again 20 being created
    for (int recordsCreated = 0; recordsCreated < recordsToCreate; recordsCreated++) {
      final JsonNode record =
          Jsons.jsonNode(ImmutableMap
              .of(COL_ID, 200 + recordsCreated, COL_MAKE_ID, 1, COL_MODEL,
                  "F-" + recordsCreated));
      writeModelRecord(record);
    }

    final JsonNode stateAfterFirstSync = Jsons.jsonNode(Collections.singletonList(stateAfterFirstBatch.get(stateAfterFirstBatch.size() - 1)));
    final AutoCloseableIterator<AirbyteMessage> secondBatchIterator = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, stateAfterFirstSync);
    final List<AirbyteMessage> dataFromSecondBatch = AutoCloseableIterators
        .toListAndClose(secondBatchIterator);
    final List<AirbyteStateMessage> stateAfterSecondBatch = extractStateMessages(dataFromSecondBatch);
    assertExpectedStateMessagesFromIncrementalSync(stateAfterSecondBatch);

    final Long replicationSlotAfterSecondSync = PgLsn.fromPgString(
        source.getReplicationSlot(defaultJdbcDatabase, getConfig()).get(0).get("confirmed_flush_lsn").asText()).asLong();

    // Second sync should move the replication slot ahead
    assertLsnPositionForSyncShouldIncrementLSN(replicationSlotAfterFirstSync, replicationSlotAfterSecondSync, 2);

    for (int recordsCreated = 0; recordsCreated < 1; recordsCreated++) {
      final JsonNode record =
          Jsons.jsonNode(ImmutableMap
              .of(COL_ID, 400 + recordsCreated, COL_MAKE_ID, 1, COL_MODEL,
                  "H-" + recordsCreated));
      writeModelRecord(record);
    }

    // Triggering sync with the first sync's state only which would mimic a scenario that the second
    // sync failed on destination end, and we didn't save state
    final AutoCloseableIterator<AirbyteMessage> thirdBatchIterator = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, stateAfterFirstSync);
    final List<AirbyteMessage> dataFromThirdBatch = AutoCloseableIterators
        .toListAndClose(thirdBatchIterator);

    final List<AirbyteStateMessage> stateAfterThirdBatch = extractStateMessages(dataFromThirdBatch);
    assertExpectedStateMessagesFromIncrementalSync(stateAfterThirdBatch);
    final Set<AirbyteRecordMessage> recordsFromThirdBatch = extractRecordMessages(
        dataFromThirdBatch);

    final Long replicationSlotAfterThirdSync = PgLsn.fromPgString(
        source.getReplicationSlot(defaultJdbcDatabase, getConfig()).get(0).get("confirmed_flush_lsn").asText()).asLong();

    // Since we used the state, no change should happen to the replication slot
    assertEquals(replicationSlotAfterSecondSync, replicationSlotAfterThirdSync);
    assertEquals(recordsToCreate + 1, recordsFromThirdBatch.size());

    for (int recordsCreated = 0; recordsCreated < 1; recordsCreated++) {
      final JsonNode record =
          Jsons.jsonNode(ImmutableMap
              .of(COL_ID, 500 + recordsCreated, COL_MAKE_ID, 1, COL_MODEL,
                  "H-" + recordsCreated));
      writeModelRecord(record);
    }

    final AutoCloseableIterator<AirbyteMessage> fourthBatchIterator = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, Jsons.jsonNode(Collections.singletonList(stateAfterThirdBatch.get(stateAfterThirdBatch.size() - 1))));
    final List<AirbyteMessage> dataFromFourthBatch = AutoCloseableIterators
        .toListAndClose(fourthBatchIterator);

    final List<AirbyteStateMessage> stateAfterFourthBatch = extractStateMessages(dataFromFourthBatch);
    assertExpectedStateMessagesFromIncrementalSync(stateAfterFourthBatch);
    final Set<AirbyteRecordMessage> recordsFromFourthBatch = extractRecordMessages(
        dataFromFourthBatch);

    final Long replicationSlotAfterFourthSync = PgLsn.fromPgString(
        source.getReplicationSlot(defaultJdbcDatabase, getConfig()).get(0).get("confirmed_flush_lsn").asText()).asLong();

    // Fourth sync should again move the replication slot ahead
    assertEquals(1, replicationSlotAfterFourthSync.compareTo(replicationSlotAfterThirdSync));
    assertEquals(1, recordsFromFourthBatch.size());
  }

  protected void assertLsnPositionForSyncShouldIncrementLSN(final Long lsnPosition1,
      final Long lsnPosition2, final int syncNumber) {
    if (syncNumber == 1) {
      assertEquals(lsnPosition1, lsnPosition2);
    } else if (syncNumber == 2) {
      assertEquals(1, lsnPosition2.compareTo(lsnPosition1));
    } else {
      throw new RuntimeException("unknown sync number " + syncNumber);
    }
  }

  /**
   * This test verifies that multiple states are sent during the CDC process based on number of records.
   * We can ensure that more than one `STATE` type of message is sent, but we are not able to assert
   * the exact number of messages sent as depends on Debezium.
   *
   * @throws Exception Exception happening in the test.
   */
  @Test
  protected void verifyCheckpointStatesByRecords() throws Exception {
    // We require a huge amount of records, otherwise Debezium will notify directly the last offset.
    final int recordsToCreate = 20000;

    final AutoCloseableIterator<AirbyteMessage> firstBatchIterator = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, null);
    final List<AirbyteMessage> dataFromFirstBatch = AutoCloseableIterators
        .toListAndClose(firstBatchIterator);
    final List<AirbyteStateMessage> stateMessages = extractStateMessages(dataFromFirstBatch);

    // As first `read` operation is from snapshot, it would generate only one state message at the end
    // of the process.
    assertExpectedStateMessages(stateMessages);

    for (int recordsCreated = 0; recordsCreated < recordsToCreate; recordsCreated++) {
      final JsonNode record =
          Jsons.jsonNode(ImmutableMap
              .of(COL_ID, 200 + recordsCreated, COL_MAKE_ID, 1, COL_MODEL,
                  "F-" + recordsCreated));
      writeModelRecord(record);
    }

    final JsonNode stateAfterFirstSync = Jsons.jsonNode(Collections.singletonList(stateMessages.get(stateMessages.size() - 1)));
    final AutoCloseableIterator<AirbyteMessage> secondBatchIterator = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, stateAfterFirstSync);
    final List<AirbyteMessage> dataFromSecondBatch = AutoCloseableIterators
        .toListAndClose(secondBatchIterator);
    assertEquals(recordsToCreate, extractRecordMessages(dataFromSecondBatch).size());
    final List<AirbyteStateMessage> stateMessagesCDC = extractStateMessages(dataFromSecondBatch);
    assertTrue(stateMessagesCDC.size() > 1, "Generated only the final state.");
    assertEquals(stateMessagesCDC.size(), stateMessagesCDC.stream().distinct().count(), "There are duplicated states.");
  }

  /**
   * This test verifies that multiple states are sent during the CDC process based on time ranges. We
   * can ensure that more than one `STATE` type of message is sent, but we are not able to assert the
   * exact number of messages sent as depends on Debezium.
   *
   * @throws Exception Exception happening in the test.
   */
  @Test
  protected void verifyCheckpointStatesBySeconds() throws Exception {
    // We require a huge amount of records, otherwise Debezium will notify directly the last offset.
    final int recordsToCreate = 20000;

    final AutoCloseableIterator<AirbyteMessage> firstBatchIterator = getSource()
        .read(getConfig(), CONFIGURED_CATALOG, null);
    final List<AirbyteMessage> dataFromFirstBatch = AutoCloseableIterators
        .toListAndClose(firstBatchIterator);
    final List<AirbyteStateMessage> stateMessages = extractStateMessages(dataFromFirstBatch);

    // As first `read` operation is from snapshot, it would generate only one state message at the end
    // of the process.
    assertExpectedStateMessages(stateMessages);

    for (int recordsCreated = 0; recordsCreated < recordsToCreate; recordsCreated++) {
      final JsonNode record =
          Jsons.jsonNode(ImmutableMap
              .of(COL_ID, 200 + recordsCreated, COL_MAKE_ID, 1, COL_MODEL,
                  "F-" + recordsCreated));
      writeModelRecord(record);
    }
    final JsonNode config = getConfig();
    ((ObjectNode) config).put("sync_checkpoint_seconds", 1);
    ((ObjectNode) config).put("sync_checkpoint_records", 100_000);

    final JsonNode stateAfterFirstSync = Jsons.jsonNode(Collections.singletonList(stateMessages.get(stateMessages.size() - 1)));
    final AutoCloseableIterator<AirbyteMessage> secondBatchIterator = getSource()
        .read(config, CONFIGURED_CATALOG, stateAfterFirstSync);
    final List<AirbyteMessage> dataFromSecondBatch = AutoCloseableIterators
        .toListAndClose(secondBatchIterator);

    assertEquals(recordsToCreate, extractRecordMessages(dataFromSecondBatch).size());
    final List<AirbyteStateMessage> stateMessagesCDC = extractStateMessages(dataFromSecondBatch);
    assertTrue(stateMessagesCDC.size() > 1, "Generated only the final state.");
    assertEquals(stateMessagesCDC.size(), stateMessagesCDC.stream().distinct().count(), "There are duplicated states.");
  }

}
