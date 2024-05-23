/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_DURATION_PROPERTY;
import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS_PROPERTY;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_DELETED_AT;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_LSN;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_UPDATED_AT;
import static io.airbyte.integrations.source.postgres.PostgresSpecConstants.FAIL_SYNC_OPTION;
import static io.airbyte.integrations.source.postgres.PostgresSpecConstants.RESYNC_DATA_OPTION;
import static io.airbyte.integrations.source.postgres.ctid.CtidStateManager.STATE_TYPE_KEY;
import static io.airbyte.integrations.source.postgres.ctid.InitialSyncCtidIteratorConstants.USE_TEST_CHUNK_SIZE;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Streams;
import io.airbyte.cdk.db.PgLsn;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.debezium.CdcSourceTest;
import io.airbyte.cdk.integrations.debezium.CdcTargetPosition;
import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.BaseImage;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.ContainerModifier;
import io.airbyte.integrations.source.postgres.cdc.PostgresCdcTargetPosition;
import io.airbyte.integrations.source.postgres.cdc.PostgresReplicationConnection;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteGlobalState;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;
import javax.sql.DataSource;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;

@Order(1)
@edu.umd.cs.findbugs.annotations.SuppressWarnings(value = "NP_NULL_ON_SOME_PATH")
public class CdcPostgresSourceTest extends CdcSourceTest<PostgresSource, PostgresTestDatabase> {

  protected BaseImage postgresImage;

  protected void setBaseImage() {
    this.postgresImage = getServerImage();
  }

  @Override
  protected void assertExpectedStateMessageCountMatches(final List<? extends AirbyteStateMessage> stateMessages, long totalCount) {
    AtomicLong count = new AtomicLong(0L);
    stateMessages.stream().forEach(stateMessage -> count.addAndGet(stateMessage.getSourceStats().getRecordCount().longValue()));
    assertEquals(totalCount, count.get());
  }

  @Override
  protected PostgresTestDatabase createTestDatabase() {
    setBaseImage();
    return PostgresTestDatabase.in(this.postgresImage, ContainerModifier.CONF).withReplicationSlot();
  }

  @Override
  protected PostgresSource source() {
    return new PostgresSource();
  }

  @Override
  protected boolean supportResumableFullRefresh() {
    return true;
  }

  @Override
  protected JsonNode config() {
    return testdb.testConfigBuilder()
        .withSchemas(modelsSchema(), modelsSchema() + "_random")
        .withoutSsl()
        .withCdcReplication("After loading Data in the destination", RESYNC_DATA_OPTION)
        .with(SYNC_CHECKPOINT_RECORDS_PROPERTY, 1)
        .with("heartbeat_action_query", "")
        .build();
  }

  @Override
  @BeforeEach
  protected void setup() {
    super.setup();
    testdb.withPublicationForAllTables();
  }

  // For legacy Postgres we will call advanceLsn() after we retrieved target LSN, so that debezium
  // would not drop any record.
  // However, that might cause unexpected state and cause failure in the test. Thus we need to bypass
  // some check if they are on legacy postgres
  // versions.
  private boolean isOnLegacyPostgres() {
    return postgresImage.majorVersion < 15;
  }

  @Test
  void testDebugMode() {
    final JsonNode invalidDebugConfig = testdb.testConfigBuilder()
        .withSchemas(modelsSchema(), modelsSchema() + "_random")
        .withoutSsl()
        .withCdcReplication("While reading Data", RESYNC_DATA_OPTION)
        .with(SYNC_CHECKPOINT_RECORDS_PROPERTY, 1)
        .with("debug_mode", true)
        .build();
    final ConfiguredAirbyteCatalog configuredCatalog = Jsons.clone(getConfiguredCatalog());
    assertThrows(ConfigErrorException.class, () -> source().read(invalidDebugConfig, configuredCatalog, null));
  }

  @Test
  void testCheckReplicationAccessSuperUserPrivilege() throws Exception {
    final var cleanUserSuperName = testdb.withNamespace("super_user");
    testdb
        .with("CREATE USER %s PASSWORD '%s';", cleanUserSuperName, testdb.getPassword())
        .with("ALTER USER %s SUPERUSER;", cleanUserSuperName)
        .onClose("DROP OWNED BY %s;", cleanUserSuperName)
        .onClose("DROP USER %s;", cleanUserSuperName);
    final JsonNode testConfig = config();
    ((ObjectNode) testConfig).put(JdbcUtils.USERNAME_KEY, cleanUserSuperName);
    final AirbyteConnectionStatus status = source().check(testConfig);
    assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, status.getStatus());
  }

  @Test
  void testCheckReplicationAccessReplicationPrivilege() throws Exception {
    final var cleanUserReplicationName = testdb.withNamespace("replication_user");
    testdb
        .with("CREATE USER %s PASSWORD '%s';", cleanUserReplicationName, testdb.getPassword())
        .with("ALTER USER %s REPLICATION;", cleanUserReplicationName)
        .onClose("DROP OWNED BY %s;", cleanUserReplicationName)
        .onClose("DROP USER %s;", cleanUserReplicationName);
    final JsonNode testConfig = config();
    ((ObjectNode) testConfig).put(JdbcUtils.USERNAME_KEY, cleanUserReplicationName);
    final AirbyteConnectionStatus status = source().check(testConfig);
    assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, status.getStatus());
  }

  @Test
  void testCheckWithoutReplicationPermission() throws Exception {
    final var cleanUserVanillaName = testdb.withNamespace("vanilla_user");
    testdb
        .with("CREATE USER %s PASSWORD '%s';", cleanUserVanillaName, testdb.getPassword())
        .onClose("DROP OWNED BY %s;", cleanUserVanillaName)
        .onClose("DROP USER %s;", cleanUserVanillaName);
    final JsonNode testConfig = config();
    ((ObjectNode) testConfig).put(JdbcUtils.USERNAME_KEY, cleanUserVanillaName);
    final AirbyteConnectionStatus status = source().check(testConfig);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertEquals(String.format(ConnectorExceptionUtil.COMMON_EXCEPTION_MESSAGE_TEMPLATE,
        String.format(PostgresReplicationConnection.REPLICATION_PRIVILEGE_ERROR_MESSAGE, testConfig.get("username").asText())),
        status.getMessage());
  }

  @Test
  void testCheckWithoutPublication() throws Exception {
    testdb.query(ctx -> ctx.execute("DROP PUBLICATION " + testdb.getPublicationName() + ";"));
    final AirbyteConnectionStatus status = source().check(config());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
    testdb.query(ctx -> ctx.execute("CREATE PUBLICATION " + testdb.getPublicationName() + " FOR ALL TABLES;"));
  }

  @Test
  void testCheckWithoutReplicationSlot() throws Exception {
    testdb.query(ctx -> ctx.execute("SELECT pg_drop_replication_slot('" + testdb.getReplicationSlotName() + "');"));
    final AirbyteConnectionStatus status = source().check(config());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
    testdb.query(ctx -> ctx.execute("SELECT pg_create_logical_replication_slot('" + testdb.getReplicationSlotName() + "', 'pgoutput');"));
  }

  @Override
  protected void assertExpectedStateMessages(final List<? extends AirbyteStateMessage> stateMessages) {
    assertEquals(7, stateMessages.size());
    assertStateTypes(stateMessages, 4);
  }

  @Override
  protected void assertExpectedStateMessagesForRecordsProducedDuringAndAfterSync(final List<? extends AirbyteStateMessage> stateAfterFirstBatch) {
    assertEquals(27, stateAfterFirstBatch.size());
    assertStateTypes(stateAfterFirstBatch, 24);
  }

  private void assertStateTypes(final List<? extends AirbyteStateMessage> stateMessages, final int indexTillWhichExpectCtidState) {
    JsonNode sharedState = null;
    for (int i = 0; i < stateMessages.size(); i++) {
      final AirbyteStateMessage stateMessage = stateMessages.get(i);
      assertEquals(AirbyteStateType.GLOBAL, stateMessage.getType());
      final AirbyteGlobalState global = stateMessage.getGlobal();
      assertNotNull(global.getSharedState());
      if (Objects.isNull(sharedState)) {
        sharedState = global.getSharedState();
      } else {
        // This validation is only true for versions on or after postgres 15. We execute
        // EPHEMERAL_HEARTBEAT_CREATE_STATEMENTS for earlier versions of
        // Postgres. See https://github.com/airbytehq/airbyte/pull/33605 for details.
        if (!isOnLegacyPostgres()) {
          assertEquals(sharedState, global.getSharedState());
        }
      }
      assertEquals(1, global.getStreamStates().size());
      final AirbyteStreamState streamState = global.getStreamStates().get(0);
      if (i <= indexTillWhichExpectCtidState) {
        assertTrue(streamState.getStreamState().has(STATE_TYPE_KEY));
        assertEquals("ctid", streamState.getStreamState().get(STATE_TYPE_KEY).asText());
      } else {
        assertFalse(streamState.getStreamState().has(STATE_TYPE_KEY));
      }
    }
  }

  @Override
  protected void validateStreamStateInResumableFullRefresh(final JsonNode streamStateToBeTested) {
    assertEquals("ctid", streamStateToBeTested.get("state_type").asText());
  }

  @Override
  @Test
  protected void testCdcAndNonResumableFullRefreshInSameSync() throws Exception {}

  @Override
  protected void assertStateMessagesForNewTableSnapshotTest(final List<? extends AirbyteStateMessage> stateMessages,
                                                            final AirbyteStateMessage stateMessageEmittedAfterFirstSyncCompletion) {
    assertEquals(7, stateMessages.size(), stateMessages.toString());
    for (int i = 0; i <= 4; i++) {
      final AirbyteStateMessage stateMessage = stateMessages.get(i);
      assertEquals(AirbyteStateMessage.AirbyteStateType.GLOBAL, stateMessage.getType());
      assertEquals(stateMessageEmittedAfterFirstSyncCompletion.getGlobal().getSharedState(),
          stateMessage.getGlobal().getSharedState());
      final Set<StreamDescriptor> streamsInSnapshotState = stateMessage.getGlobal().getStreamStates()
          .stream()
          .map(AirbyteStreamState::getStreamDescriptor)
          .collect(Collectors.toSet());
      assertEquals(2, streamsInSnapshotState.size());
      assertTrue(
          streamsInSnapshotState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME + "_random").withNamespace(randomSchema())));
      assertTrue(streamsInSnapshotState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(modelsSchema())));

      stateMessage.getGlobal().getStreamStates().forEach(s -> {
        final JsonNode streamState = s.getStreamState();
        if (s.getStreamDescriptor().equals(new StreamDescriptor().withName(MODELS_STREAM_NAME + "_random").withNamespace(randomSchema()))) {
          assertEquals("ctid", streamState.get(STATE_TYPE_KEY).asText());
        } else if (s.getStreamDescriptor().equals(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(modelsSchema()))) {
          assertFalse(streamState.has(STATE_TYPE_KEY));
        } else {
          throw new RuntimeException("Unknown stream");
        }
      });
    }

    final AirbyteStateMessage secondLastSateMessage = stateMessages.get(5);
    assertEquals(AirbyteStateMessage.AirbyteStateType.GLOBAL, secondLastSateMessage.getType());
    assertEquals(stateMessageEmittedAfterFirstSyncCompletion.getGlobal().getSharedState(),
        secondLastSateMessage.getGlobal().getSharedState());
    final Set<StreamDescriptor> streamsInSnapshotState = secondLastSateMessage.getGlobal().getStreamStates()
        .stream()
        .map(AirbyteStreamState::getStreamDescriptor)
        .collect(Collectors.toSet());
    assertEquals(2, streamsInSnapshotState.size());
    assertTrue(
        streamsInSnapshotState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME + "_random").withNamespace(randomSchema())));
    assertTrue(streamsInSnapshotState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(modelsSchema())));
    secondLastSateMessage.getGlobal().getStreamStates().forEach(s -> {
      final JsonNode streamState = s.getStreamState();
      assertFalse(streamState.has(STATE_TYPE_KEY));
    });

    final AirbyteStateMessage stateMessageEmittedAfterSecondSyncCompletion = stateMessages.get(6);
    assertEquals(AirbyteStateMessage.AirbyteStateType.GLOBAL, stateMessageEmittedAfterSecondSyncCompletion.getType());
    assertNotEquals(stateMessageEmittedAfterFirstSyncCompletion.getGlobal().getSharedState(),
        stateMessageEmittedAfterSecondSyncCompletion.getGlobal().getSharedState());
    final Set<StreamDescriptor> streamsInSyncCompletionState = stateMessageEmittedAfterSecondSyncCompletion.getGlobal().getStreamStates()
        .stream()
        .map(AirbyteStreamState::getStreamDescriptor)
        .collect(Collectors.toSet());
    assertEquals(2, streamsInSnapshotState.size());
    assertTrue(
        streamsInSyncCompletionState.contains(
            new StreamDescriptor().withName(MODELS_STREAM_NAME + "_random").withNamespace(randomSchema())));
    assertTrue(streamsInSyncCompletionState.contains(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(modelsSchema())));
    assertNotNull(stateMessageEmittedAfterSecondSyncCompletion.getData());
  }

  @Test
  public void testTwoStreamSync() throws Exception {
    final ConfiguredAirbyteCatalog configuredCatalog = Jsons.clone(getConfiguredCatalog());

    final List<JsonNode> MODEL_RECORDS_2 = ImmutableList.of(
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 110, COL_MAKE_ID, 1, COL_MODEL, "Fiesta-2")),
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 120, COL_MAKE_ID, 1, COL_MODEL, "Focus-2")),
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 130, COL_MAKE_ID, 1, COL_MODEL, "Ranger-2")),
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 140, COL_MAKE_ID, 2, COL_MODEL, "GLA-2")),
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 150, COL_MAKE_ID, 2, COL_MODEL, "A 220-2")),
        Jsons.jsonNode(ImmutableMap.of(COL_ID, 160, COL_MAKE_ID, 2, COL_MODEL, "E 350-2")));

    testdb.with(createTableSqlFmt(), modelsSchema(), MODELS_STREAM_NAME + "_2",
        columnClause(ImmutableMap.of(COL_ID, "INTEGER", COL_MAKE_ID, "INTEGER", COL_MODEL, "VARCHAR(200)"), Optional.of(COL_ID)));

    for (final JsonNode recordJson : MODEL_RECORDS_2) {
      writeRecords(recordJson, modelsSchema(), MODELS_STREAM_NAME + "_2", COL_ID,
          COL_MAKE_ID, COL_MODEL);
    }

    final ConfiguredAirbyteStream airbyteStream = new ConfiguredAirbyteStream()
        .withStream(CatalogHelpers.createAirbyteStream(
            MODELS_STREAM_NAME + "_2",
            modelsSchema(),
            Field.of(COL_ID, JsonSchemaType.INTEGER),
            Field.of(COL_MAKE_ID, JsonSchemaType.INTEGER),
            Field.of(COL_MODEL, JsonSchemaType.STRING))
            .withSupportedSyncModes(
                Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID))));
    airbyteStream.setSyncMode(SyncMode.INCREMENTAL);

    final List<ConfiguredAirbyteStream> streams = configuredCatalog.getStreams();
    streams.add(airbyteStream);
    configuredCatalog.withStreams(streams);

    final AutoCloseableIterator<AirbyteMessage> read1 = source().read(config(), configuredCatalog, null);
    final List<AirbyteMessage> actualRecords1 = AutoCloseableIterators.toListAndClose(read1);

    final Set<AirbyteRecordMessage> recordMessages1 = extractRecordMessages(actualRecords1);
    final List<AirbyteStateMessage> stateMessages1 = extractStateMessages(actualRecords1);
    assertEquals(13, stateMessages1.size());
    JsonNode sharedState = null;
    StreamDescriptor firstStreamInState = null;
    for (int i = 0; i < stateMessages1.size(); i++) {
      final AirbyteStateMessage stateMessage = stateMessages1.get(i);
      assertEquals(AirbyteStateType.GLOBAL, stateMessage.getType());
      final AirbyteGlobalState global = stateMessage.getGlobal();
      assertNotNull(global.getSharedState());
      if (Objects.isNull(sharedState)) {
        sharedState = global.getSharedState();
      } else {
        // LSN will be advanced for postgres version before 15. See
        // https://github.com/airbytehq/airbyte/pull/33605
        if (!isOnLegacyPostgres()) {
          assertEquals(sharedState, global.getSharedState());
        }
      }

      if (Objects.isNull(firstStreamInState)) {
        assertEquals(1, global.getStreamStates().size());
        firstStreamInState = global.getStreamStates().get(0).getStreamDescriptor();
      }

      if (i <= 4) {
        // First 4 state messages are ctid state
        assertEquals(1, global.getStreamStates().size());
        final AirbyteStreamState streamState = global.getStreamStates().get(0);
        assertTrue(streamState.getStreamState().has(STATE_TYPE_KEY));
        assertEquals("ctid", streamState.getStreamState().get(STATE_TYPE_KEY).asText());
      } else if (i == 5) {
        // 5th state message is the final state message emitted for the stream
        assertEquals(1, global.getStreamStates().size());
        final AirbyteStreamState streamState = global.getStreamStates().get(0);
        assertFalse(streamState.getStreamState().has(STATE_TYPE_KEY));
      } else if (i <= 10) {
        // 6th to 10th is the ctid state message for the 2nd stream but final state message for 1st stream
        assertEquals(2, global.getStreamStates().size());
        final StreamDescriptor finalFirstStreamInState = firstStreamInState;
        global.getStreamStates().forEach(c -> {
          if (c.getStreamDescriptor().equals(finalFirstStreamInState)) {
            assertFalse(c.getStreamState().has(STATE_TYPE_KEY));
          } else {
            assertTrue(c.getStreamState().has(STATE_TYPE_KEY));
            assertEquals("ctid", c.getStreamState().get(STATE_TYPE_KEY).asText());
          }
        });
      } else {
        // last 2 state messages don't contain ctid info cause ctid sync should be complete
        assertEquals(2, global.getStreamStates().size());
        global.getStreamStates().forEach(c -> assertFalse(c.getStreamState().has(STATE_TYPE_KEY)));
      }
    }

    final Set<String> names = new HashSet<>(STREAM_NAMES);
    names.add(MODELS_STREAM_NAME + "_2");
    assertExpectedRecords(Streams.concat(MODEL_RECORDS_2.stream(), MODEL_RECORDS.stream())
        .collect(Collectors.toSet()),
        recordMessages1,
        names,
        names,
        modelsSchema());

    assertEquals(new StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(modelsSchema()), firstStreamInState);

    // Triggering a sync with a ctid state for 1 stream and complete state for other stream
    final AutoCloseableIterator<AirbyteMessage> read2 = source()
        .read(config(), configuredCatalog, Jsons.jsonNode(Collections.singletonList(stateMessages1.get(6))));
    final List<AirbyteMessage> actualRecords2 = AutoCloseableIterators.toListAndClose(read2);

    final List<AirbyteStateMessage> stateMessages2 = extractStateMessages(actualRecords2);

    assertEquals(6, stateMessages2.size());
    for (int i = 0; i < stateMessages2.size(); i++) {
      final AirbyteStateMessage stateMessage = stateMessages2.get(i);
      assertEquals(AirbyteStateType.GLOBAL, stateMessage.getType());
      final AirbyteGlobalState global = stateMessage.getGlobal();
      assertNotNull(global.getSharedState());
      assertEquals(2, global.getStreamStates().size());

      if (i <= 3) {
        final StreamDescriptor finalFirstStreamInState = firstStreamInState;
        global.getStreamStates().forEach(c -> {
          // First 4 state messages are ctid state for the stream that didn't complete ctid sync the first
          // time
          if (c.getStreamDescriptor().equals(finalFirstStreamInState)) {
            assertFalse(c.getStreamState().has(STATE_TYPE_KEY));
          } else {
            assertTrue(c.getStreamState().has(STATE_TYPE_KEY));
            assertEquals("ctid", c.getStreamState().get(STATE_TYPE_KEY).asText());
          }
        });
      } else {
        // last 2 state messages don't contain ctid info cause ctid sync should be complete
        global.getStreamStates().forEach(c -> assertFalse(c.getStreamState().has(STATE_TYPE_KEY)));
      }
    }

    final Set<AirbyteRecordMessage> recordMessages2 = extractRecordMessages(actualRecords2);
    assertEquals(5, recordMessages2.size());
    assertExpectedRecords(new HashSet<>(MODEL_RECORDS_2.subList(1, MODEL_RECORDS_2.size())),
        recordMessages2,
        names,
        names,
        modelsSchema());
  }

  @Override
  protected void assertExpectedStateMessagesForNoData(final List<? extends AirbyteStateMessage> stateMessages) {
    assertEquals(2, stateMessages.size());
  }

  @Override
  protected void assertExpectedStateMessagesFromIncrementalSync(final List<? extends AirbyteStateMessage> stateMessages) {
    assertEquals(1, stateMessages.size());
    assertNotNull(stateMessages.get(0).getData());
  }

  @Override
  protected PostgresCdcTargetPosition cdcLatestTargetPosition() {
    final JdbcDatabase database = new DefaultJdbcDatabase(
        DataSourceFactory.create(
            config().get(JdbcUtils.USERNAME_KEY).asText(),
            config().get(JdbcUtils.PASSWORD_KEY).asText(),
            DatabaseDriver.POSTGRESQL.getDriverClassName(),
            String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
                config().get(JdbcUtils.HOST_KEY).asText(),
                config().get(JdbcUtils.PORT_KEY).asInt(),
                config().get(JdbcUtils.DATABASE_KEY).asText())));

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

  @Test
  void testDiscoverFiltersNonPublication() throws Exception {
    // Drop the default publication (which is created for all tables). Create a publication for the
    // models table. By default,
    // the tests create a modelsSchema().models table and modelsSchema()_random.models_random
    // table. We
    // will create a publication
    // for one of the tests and assert that both streams end up in the catalog. However, the stream that
    // is not associated with
    // a publication should only have SyncMode.FULL_REFRESH as a supported sync mode.
    testdb.query(ctx -> ctx.execute("DROP PUBLICATION " + testdb.getPublicationName() + ";"));
    testdb
        .query(ctx -> ctx.execute(String.format("CREATE PUBLICATION " + testdb.getPublicationName() + " FOR TABLE %s.%s", modelsSchema(), "models")));

    final AirbyteCatalog catalog = source().discover(config());
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
    assertFalse(streamNotInPublication.getSourceDefinedPrimaryKey().isEmpty());
    assertTrue(streamNotInPublication.getSourceDefinedCursor());
    testdb.query(ctx -> ctx.execute("DROP PUBLICATION " + testdb.getPublicationName() + ";"));
    testdb.query(ctx -> ctx.execute("CREATE PUBLICATION " + testdb.getPublicationName() + " FOR ALL TABLES"));
  }

  @Test
  public void testTableWithTimestampColDefault() throws Exception {
    createAndPopulateTimestampTable();
    final AirbyteCatalog catalog = new AirbyteCatalog().withStreams(List.of(
        CatalogHelpers.createAirbyteStream("time_stamp_table", modelsSchema(),
            Field.of("id", JsonSchemaType.NUMBER),
            Field.of("name", JsonSchemaType.STRING),
            Field.of("created_at", JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of("id")))));
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers
        .toDefaultConfiguredCatalog(catalog);

    // set all streams to incremental.
    configuredCatalog.getStreams().forEach(s -> s.setSyncMode(SyncMode.INCREMENTAL));
    final AutoCloseableIterator<AirbyteMessage> firstBatchIterator = source()
        .read(config(), configuredCatalog, null);
    final List<AirbyteMessage> dataFromFirstBatch = AutoCloseableIterators
        .toListAndClose(firstBatchIterator);
    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessages(dataFromFirstBatch);
    assertExpectedStateMessages(stateAfterFirstBatch);
    final Set<AirbyteRecordMessage> recordsFromFirstBatch = extractRecordMessages(
        dataFromFirstBatch);

    assertEquals(6, recordsFromFirstBatch.size());
  }

  private void createAndPopulateTimestampTable() {
    testdb.with(createTableSqlFmt(), modelsSchema(), "time_stamp_table",
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
      testdb.with("INSERT INTO %s.%s (%s, %s) VALUES (%s, '%s');", modelsSchema(), "time_stamp_table",
          "id", "name",
          recordJson.get("id").asInt(), recordJson.get("name").asText());
    }
  }

  @Test
  void testSyncShouldFailPurgedLogs() throws Exception {
    final int recordsToCreate = 20;

    final JsonNode config = testdb.testConfigBuilder()
        .withSchemas(modelsSchema(), modelsSchema() + "_random")
        .withoutSsl()
        .withCdcReplication("While reading Data", FAIL_SYNC_OPTION)
        .with(SYNC_CHECKPOINT_RECORDS_PROPERTY, 1)
        .build();
    final AutoCloseableIterator<AirbyteMessage> firstBatchIterator = source()
        .read(config, getConfiguredCatalog(), null);
    final List<AirbyteMessage> dataFromFirstBatch = AutoCloseableIterators
        .toListAndClose(firstBatchIterator);
    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessages(dataFromFirstBatch);
    assertExpectedStateMessages(stateAfterFirstBatch);
    // second batch of records again 20 being created
    bulkInsertRecords(recordsToCreate);

    // Extract the last state message
    final JsonNode state = Jsons.jsonNode(Collections.singletonList(stateAfterFirstBatch.get(stateAfterFirstBatch.size() - 1)));
    final AutoCloseableIterator<AirbyteMessage> secondBatchIterator = source()
        .read(config, getConfiguredCatalog(), state);
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
    assertThrows(ConfigErrorException.class, () -> source().read(config, getConfiguredCatalog(), state));
  }

  @Test
  protected void syncShouldHandlePurgedLogsGracefully() throws Exception {

    final int recordsToCreate = 20;

    final JsonNode config = testdb.testConfigBuilder()
        .withSchemas(modelsSchema(), modelsSchema() + "_random")
        .withoutSsl()
        .withCdcReplication()
        .with(SYNC_CHECKPOINT_RECORDS_PROPERTY, 1)
        .build();
    final AutoCloseableIterator<AirbyteMessage> firstBatchIterator = source()
        .read(config, getConfiguredCatalog(), null);
    final List<AirbyteMessage> dataFromFirstBatch = AutoCloseableIterators
        .toListAndClose(firstBatchIterator);
    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessages(dataFromFirstBatch);
    assertExpectedStateMessages(stateAfterFirstBatch);
    // second batch of records again 20 being created
    bulkInsertRecords(recordsToCreate);

    // Extract the last state message
    final JsonNode state = Jsons.jsonNode(Collections.singletonList(stateAfterFirstBatch.get(stateAfterFirstBatch.size() - 1)));
    final AutoCloseableIterator<AirbyteMessage> secondBatchIterator = source()
        .read(config, getConfiguredCatalog(), state);
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
    final AutoCloseableIterator<AirbyteMessage> thirdBatchIterator = source()
        .read(config, getConfiguredCatalog(), state);

    final List<AirbyteMessage> dataFromThirdBatch = AutoCloseableIterators
        .toListAndClose(thirdBatchIterator);

    final List<AirbyteStateMessage> stateAfterThirdBatch = extractStateMessages(dataFromThirdBatch);
    assertStateForSyncShouldHandlePurgedLogsGracefully(stateAfterThirdBatch);
    final Set<AirbyteRecordMessage> recordsFromThirdBatch = extractRecordMessages(
        dataFromThirdBatch);

    assertEquals(MODEL_RECORDS.size() + recordsToCreate + 1, recordsFromThirdBatch.size());
  }

  protected void assertStateForSyncShouldHandlePurgedLogsGracefully(final List<AirbyteStateMessage> stateMessages) {
    assertEquals(28, stateMessages.size());
    assertStateTypes(stateMessages, 25);
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
    final var postgresSource = source();

    final DataSource dataSource = DataSourceFactory.create(
        config().get(JdbcUtils.USERNAME_KEY).asText(),
        config().get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
            config().get(JdbcUtils.HOST_KEY).asText(),
            config().get(JdbcUtils.PORT_KEY).asInt(),
            config().get(JdbcUtils.DATABASE_KEY).asText()));

    final JdbcDatabase defaultJdbcDatabase = new DefaultJdbcDatabase(dataSource);

    final Long replicationSlotAtTheBeginning = PgLsn.fromPgString(
        postgresSource.getReplicationSlot(defaultJdbcDatabase, config()).get(0).get("confirmed_flush_lsn").asText()).asLong();

    final AutoCloseableIterator<AirbyteMessage> firstBatchIterator = postgresSource
        .read(config(), getConfiguredCatalog(), null);
    final List<AirbyteMessage> dataFromFirstBatch = AutoCloseableIterators
        .toListAndClose(firstBatchIterator);
    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessages(dataFromFirstBatch);

    final Long replicationSlotAfterFirstSync = PgLsn.fromPgString(
        postgresSource.getReplicationSlot(defaultJdbcDatabase, config()).get(0).get("confirmed_flush_lsn").asText()).asLong();

    // First sync should not make any change to the replication slot status
    assertLsnPositionForSyncShouldIncrementLSN(replicationSlotAtTheBeginning, replicationSlotAfterFirstSync, 1);

    // second batch of records again 20 being created
    bulkInsertRecords(recordsToCreate);

    final JsonNode stateAfterFirstSync = Jsons.jsonNode(Collections.singletonList(stateAfterFirstBatch.get(stateAfterFirstBatch.size() - 1)));
    final AutoCloseableIterator<AirbyteMessage> secondBatchIterator = postgresSource
        .read(config(), getConfiguredCatalog(), stateAfterFirstSync);
    final List<AirbyteMessage> dataFromSecondBatch = AutoCloseableIterators
        .toListAndClose(secondBatchIterator);
    final List<AirbyteStateMessage> stateAfterSecondBatch = extractStateMessages(dataFromSecondBatch);
    assertExpectedStateMessagesFromIncrementalSync(stateAfterSecondBatch);

    final Long replicationSlotAfterSecondSync = PgLsn.fromPgString(
        postgresSource.getReplicationSlot(defaultJdbcDatabase, config()).get(0).get("confirmed_flush_lsn").asText()).asLong();

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
    final AutoCloseableIterator<AirbyteMessage> thirdBatchIterator = postgresSource
        .read(config(), getConfiguredCatalog(), stateAfterFirstSync);
    final List<AirbyteMessage> dataFromThirdBatch = AutoCloseableIterators
        .toListAndClose(thirdBatchIterator);

    final List<AirbyteStateMessage> stateAfterThirdBatch = extractStateMessages(dataFromThirdBatch);
    assertExpectedStateMessagesFromIncrementalSync(stateAfterThirdBatch);
    final Set<AirbyteRecordMessage> recordsFromThirdBatch = extractRecordMessages(
        dataFromThirdBatch);

    final Long replicationSlotAfterThirdSync = PgLsn.fromPgString(
        postgresSource.getReplicationSlot(defaultJdbcDatabase, config()).get(0).get("confirmed_flush_lsn").asText()).asLong();

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

    final AutoCloseableIterator<AirbyteMessage> fourthBatchIterator = postgresSource
        .read(config(), getConfiguredCatalog(),
            Jsons.jsonNode(Collections.singletonList(stateAfterThirdBatch.get(stateAfterThirdBatch.size() - 1))));
    final List<AirbyteMessage> dataFromFourthBatch = AutoCloseableIterators
        .toListAndClose(fourthBatchIterator);

    final List<AirbyteStateMessage> stateAfterFourthBatch = extractStateMessages(dataFromFourthBatch);
    assertExpectedStateMessagesFromIncrementalSync(stateAfterFourthBatch);
    final Set<AirbyteRecordMessage> recordsFromFourthBatch = extractRecordMessages(
        dataFromFourthBatch);

    final Long replicationSlotAfterFourthSync = PgLsn.fromPgString(
        postgresSource.getReplicationSlot(defaultJdbcDatabase, config()).get(0).get("confirmed_flush_lsn").asText()).asLong();

    // Fourth sync should again move the replication slot ahead
    assertEquals(1, replicationSlotAfterFourthSync.compareTo(replicationSlotAfterThirdSync));
    assertEquals(1, recordsFromFourthBatch.size());
  }

  protected void assertLsnPositionForSyncShouldIncrementLSN(final Long lsnPosition1,
                                                            final Long lsnPosition2,
                                                            final int syncNumber) {
    if (syncNumber == 1) {
      assertEquals(1, lsnPosition2.compareTo(lsnPosition1));
    } else if (syncNumber == 2) {
      // Earlier Postgres version will advance lsn even if there is no sync records. See
      // https://github.com/airbytehq/airbyte/pull/33605.
      if (!isOnLegacyPostgres()) {
        assertEquals(0, lsnPosition2.compareTo(lsnPosition1));
      }
    } else {
      throw new RuntimeException("Unknown sync number " + syncNumber);
    }
  }

  /**
   * This test verifies that multiple states are sent during the CDC process based on number of
   * records. We can ensure that more than one `STATE` type of message is sent, but we are not able to
   * assert the exact number of messages sent as depends on Debezium.
   *
   * @throws Exception Exception happening in the test.
   */
  @Test
  protected void verifyCheckpointStatesByRecords() throws Exception {
    // We require a huge amount of records, otherwise Debezium will notify directly the last offset.
    final int recordsToCreate = 20000;

    final AutoCloseableIterator<AirbyteMessage> firstBatchIterator = source()
        .read(config(), getConfiguredCatalog(), null);
    final List<AirbyteMessage> dataFromFirstBatch = AutoCloseableIterators
        .toListAndClose(firstBatchIterator);
    final List<AirbyteStateMessage> stateMessages = extractStateMessages(dataFromFirstBatch);

    // As first `read` operation is from snapshot, it would generate only one state message at the end
    // of the process.
    assertExpectedStateMessages(stateMessages);
    bulkInsertRecords(recordsToCreate);

    final JsonNode stateAfterFirstSync = Jsons.jsonNode(Collections.singletonList(stateMessages.get(stateMessages.size() - 1)));
    final AutoCloseableIterator<AirbyteMessage> secondBatchIterator = source()
        .read(config(), getConfiguredCatalog(), stateAfterFirstSync);
    final List<AirbyteMessage> dataFromSecondBatch = AutoCloseableIterators
        .toListAndClose(secondBatchIterator);
    assertEquals(recordsToCreate, extractRecordMessages(dataFromSecondBatch).size());
    final List<AirbyteStateMessage> stateMessagesCDC = extractStateMessages(dataFromSecondBatch);
    // We expect only one cdc state message, as all the records are inserted in a single transaction.
    // Since
    // lsn_commit only increases with a new transaction, we expect only one state message.
    assertTrue(stateMessagesCDC.size() == 1, "Generated only the final state.");
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
    final int recordsToCreate = 40000;

    final AutoCloseableIterator<AirbyteMessage> firstBatchIterator = source()
        .read(config(), getConfiguredCatalog(), null);
    final List<AirbyteMessage> dataFromFirstBatch = AutoCloseableIterators
        .toListAndClose(firstBatchIterator);
    final List<AirbyteStateMessage> stateMessages = extractStateMessages(dataFromFirstBatch);

    // As first `read` operation is from snapshot, it would generate only one state message at the end
    // of the process.
    assertExpectedStateMessages(stateMessages);
    bulkInsertRecords(recordsToCreate);

    final JsonNode config = config();
    ((ObjectNode) config).put(SYNC_CHECKPOINT_DURATION_PROPERTY, 1);
    ((ObjectNode) config).put(SYNC_CHECKPOINT_RECORDS_PROPERTY, 100_000);

    final JsonNode stateAfterFirstSync = Jsons.jsonNode(Collections.singletonList(stateMessages.get(stateMessages.size() - 1)));
    final AutoCloseableIterator<AirbyteMessage> secondBatchIterator = source()
        .read(config, getConfiguredCatalog(), stateAfterFirstSync);
    final List<AirbyteMessage> dataFromSecondBatch = AutoCloseableIterators
        .toListAndClose(secondBatchIterator);

    assertEquals(recordsToCreate, extractRecordMessages(dataFromSecondBatch).size());
    final List<AirbyteStateMessage> stateMessagesCDC = extractStateMessages(dataFromSecondBatch);
    // We expect only one cdc state message, as all the records are inserted in a single transaction.
    // Since
    // lsn_commit only increases with a new transaction, we expect only one state message.
    assertTrue(stateMessagesCDC.size() == 1, "Generated only the final state.");
    assertEquals(stateMessagesCDC.size(), stateMessagesCDC.stream().distinct().count(), "There are duplicated states.");
  }

  /**
   * This test is setup to force
   * {@link io.airbyte.integrations.source.postgres.ctid.InitialSyncCtidIterator} create multiple
   * pages
   */
  @Test
  protected void ctidIteratorPageSizeTest() throws Exception {
    final int recordsToCreate = 25_000;
    final Set<Integer> expectedIds = new HashSet<>();
    MODEL_RECORDS.forEach(c -> expectedIds.add(c.get(COL_ID).asInt()));

    bulkInsertRecords(recordsToCreate);
    for (int recordsCreated = 0; recordsCreated < recordsToCreate; recordsCreated++) {
      final int id = 200 + recordsCreated;
      expectedIds.add(id);
    }

    /**
     * Setting the property to make the
     * {@link io.airbyte.integrations.source.postgres.ctid.InitialSyncCtidIterator} use smaller page
     * size of 8KB instead of default 1GB This allows us to make sure that the iterator logic works with
     * multiple pages (sub queries)
     */
    final JsonNode config = config();
    ((ObjectNode) config).put(USE_TEST_CHUNK_SIZE, true);
    final AutoCloseableIterator<AirbyteMessage> firstBatchIterator = source()
        .read(config, getConfiguredCatalog(), null);
    final List<AirbyteMessage> dataFromFirstBatch = AutoCloseableIterators
        .toListAndClose(firstBatchIterator);

    final Set<AirbyteRecordMessage> airbyteRecordMessages = extractRecordMessages(dataFromFirstBatch);
    assertEquals(recordsToCreate + MODEL_RECORDS.size(), airbyteRecordMessages.size());

    airbyteRecordMessages.forEach(c -> {
      assertTrue(expectedIds.contains(c.getData().get(COL_ID).asInt()));
      expectedIds.remove(c.getData().get(COL_ID).asInt());
    });
  }

  private void bulkInsertRecords(final int recordsToCreate) {
    testdb.with("""
                INSERT INTO %s.%s (%s, %s, %s)
                SELECT
                  200 + generate_series AS id,
                  1 AS make_id,
                  'F-' || generate_series AS model
                FROM generate_series(0, %d - 1);
                """,
        modelsSchema(), MODELS_STREAM_NAME,
        COL_ID, COL_MAKE_ID, COL_MODEL,
        recordsToCreate);
  }

  @Override
  protected void compareTargetPositionFromTheRecordsWithTargetPostionGeneratedBeforeSync(final CdcTargetPosition targetPosition,
                                                                                         final AirbyteRecordMessage record) {
    // The LSN from records should be either equal or grater than the position value before the sync
    // started.
    // The current Write-Ahead Log (WAL) position can move ahead even without any data modifications
    // (INSERT, UPDATE, DELETE)
    // The start and end of transactions, even read-only ones, are recorded in the WAL. So, simply
    // starting and committing a transaction can cause the WAL location to move forward.
    // Periodic checkpoints, which write dirty pages from memory to disk to ensure database consistency,
    // generate WAL records. Checkpoints happen even if there are no active data modifications
    assert targetPosition instanceof PostgresCdcTargetPosition;
    assertTrue(extractPosition(record.getData()).targetLsn.compareTo(((PostgresCdcTargetPosition) targetPosition).targetLsn) >= 0);
  }

  protected static BaseImage getServerImage() {
    return BaseImage.POSTGRES_16;
  }

}
