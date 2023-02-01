/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.acceptance;

import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.COLUMN_ID;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.COLUMN_NAME;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.waitForSuccessfulJob;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.generated.WebBackendApi;
import io.airbyte.api.client.invoker.generated.ApiClient;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.AirbyteCatalog;
import io.airbyte.api.client.model.generated.AirbyteStream;
import io.airbyte.api.client.model.generated.AirbyteStreamAndConfiguration;
import io.airbyte.api.client.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.client.model.generated.ConnectionRead;
import io.airbyte.api.client.model.generated.ConnectionScheduleType;
import io.airbyte.api.client.model.generated.ConnectionState;
import io.airbyte.api.client.model.generated.ConnectionStateType;
import io.airbyte.api.client.model.generated.DestinationDefinitionIdRequestBody;
import io.airbyte.api.client.model.generated.DestinationDefinitionRead;
import io.airbyte.api.client.model.generated.DestinationSyncMode;
import io.airbyte.api.client.model.generated.JobInfoRead;
import io.airbyte.api.client.model.generated.JobRead;
import io.airbyte.api.client.model.generated.OperationRead;
import io.airbyte.api.client.model.generated.SourceDefinitionIdRequestBody;
import io.airbyte.api.client.model.generated.SourceDefinitionRead;
import io.airbyte.api.client.model.generated.SourceRead;
import io.airbyte.api.client.model.generated.StreamDescriptor;
import io.airbyte.api.client.model.generated.StreamState;
import io.airbyte.api.client.model.generated.SyncMode;
import io.airbyte.api.client.model.generated.WebBackendConnectionUpdate;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.test.utils.AirbyteAcceptanceTestHarness;
import io.airbyte.test.utils.SchemaTableNamePair;
import java.io.IOException;
import java.net.URISyntaxException;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import org.jooq.Record;
import org.jooq.Result;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;
import org.junit.jupiter.api.condition.DisabledIfEnvironmentVariable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * These tests test the CDC source behavior in Airbyte, ensuring that the behavior of syncs when in
 * CDC mode is as expected
 * <p>
 * Some of the tests in this class are specifically testing partial reset behavior when in CDC mode,
 * support for which was recently added to the postgres connector.
 * <p>
 * These tests are disabled in Kube, similar to the BasicAcceptanceTests, because they aren't
 * testing any behavior that is specific to or dependent on this being run on kube vs docker.
 * Therefore, since operations tend to take longer to perform on kube, there is little value in
 * re-running these tests on kube when we already run them on docker.
 */
@DisabledIfEnvironmentVariable(named = "KUBE",
                               matches = "true")
@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class CdcAcceptanceTests {

  record DestinationCdcRecordMatcher(JsonNode sourceRecord, Instant minUpdatedAt, Optional<Instant> minDeletedAt) {}

  private static final Logger LOGGER = LoggerFactory.getLogger(BasicAcceptanceTests.class);

  private static final String POSTGRES_INIT_SQL_FILE = "postgres_init_cdc.sql";
  private static final String CDC_METHOD = "CDC";
  // must match replication slot name used in the above POSTGRES_INIT_SQL_FILE
  private static final String REPLICATION_SLOT = "airbyte_slot";
  // must match publication name used in the above POSTGRES_INIT_SQL_FILE
  private static final String PUBLICATION = "airbyte_publication";
  private static final Integer INITIAL_WAITING_SECONDS = 5;

  private static final String SOURCE_NAME = "CDC Source";
  private static final String CONNECTION_NAME = "test-connection";
  private static final String SCHEMA_NAME = "public";
  private static final String CDC_UPDATED_AT_COLUMN = "_ab_cdc_updated_at";
  private static final String CDC_DELETED_AT_COLUMN = "_ab_cdc_deleted_at";
  private static final String ID_AND_NAME_TABLE = "id_and_name";
  private static final String COLOR_PALETTE_TABLE = "color_palette";
  private static final String COLUMN_COLOR = "color";
  private static final String STARTING = "Starting {}";
  private static final String STARTING_SYNC_ONE = "Starting {} sync 1";

  // version of the postgres destination connector that was built with the
  // old Airbyte protocol that does not contain any per-stream logic/fields
  private static final String POSTGRES_DESTINATION_LEGACY_CONNECTOR_VERSION = "0.3.19";

  private static AirbyteApiClient apiClient;
  private static WebBackendApi webBackendApi;
  private static UUID workspaceId;
  private static OperationRead operationRead;

  private AirbyteAcceptanceTestHarness testHarness;

  @BeforeAll
  static void init() throws URISyntaxException, IOException, InterruptedException, ApiException {
    apiClient = new AirbyteApiClient(
        new ApiClient().setScheme("http")
            .setHost("localhost")
            .setPort(8001)
            .setBasePath("/api"));
    webBackendApi = new WebBackendApi(
        new ApiClient().setScheme("http")
            .setHost("localhost")
            .setPort(8001)
            .setBasePath("/api"));
    // work in whatever default workspace is present.
    workspaceId = apiClient.getWorkspaceApi().listWorkspaces().getWorkspaces().get(0).getWorkspaceId();
    LOGGER.info("workspaceId = " + workspaceId);

    // log which connectors are being used.
    final SourceDefinitionRead sourceDef = apiClient.getSourceDefinitionApi()
        .getSourceDefinition(new SourceDefinitionIdRequestBody()
            .sourceDefinitionId(UUID.fromString("decd338e-5647-4c0b-adf4-da0e75f5a750")));
    final DestinationDefinitionRead destinationDef = apiClient.getDestinationDefinitionApi()
        .getDestinationDefinition(new DestinationDefinitionIdRequestBody()
            .destinationDefinitionId(UUID.fromString("25c5221d-dce2-4163-ade9-739ef790f503")));
    LOGGER.info("pg source definition: {}", sourceDef.getDockerImageTag());
    LOGGER.info("pg destination definition: {}", destinationDef.getDockerImageTag());
  }

  @BeforeEach
  void setup() throws URISyntaxException, IOException, InterruptedException, ApiException, SQLException {
    testHarness = new AirbyteAcceptanceTestHarness(apiClient, workspaceId, POSTGRES_INIT_SQL_FILE);
    testHarness.setup();
  }

  @AfterEach
  void end() {
    testHarness.cleanup();
    testHarness.stopDbAndContainers();
  }

  @Test
  void testIncrementalCdcSync(final TestInfo testInfo) throws Exception {
    LOGGER.info(STARTING, testInfo.getDisplayName());

    final UUID connectionId = createCdcConnection();
    LOGGER.info(STARTING_SYNC_ONE, testInfo.getDisplayName());

    final JobInfoRead connectionSyncRead1 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead1.getJob());
    LOGGER.info("state after sync 1: {}", apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    final Database source = testHarness.getSourceDatabase();

    List<DestinationCdcRecordMatcher> expectedIdAndNameRecords = getCdcRecordMatchersFromSource(source, ID_AND_NAME_TABLE);
    assertDestinationMatches(ID_AND_NAME_TABLE, expectedIdAndNameRecords);

    List<DestinationCdcRecordMatcher> expectedColorPaletteRecords = getCdcRecordMatchersFromSource(source, COLOR_PALETTE_TABLE);
    assertDestinationMatches(COLOR_PALETTE_TABLE, expectedColorPaletteRecords);

    final List<StreamDescriptor> expectedStreams = List.of(
        new StreamDescriptor().namespace(SCHEMA_NAME).name(ID_AND_NAME_TABLE),
        new StreamDescriptor().namespace(SCHEMA_NAME).name(COLOR_PALETTE_TABLE));
    assertGlobalStateContainsStreams(connectionId, expectedStreams);

    final Instant beforeFirstUpdate = Instant.now();

    LOGGER.info("Inserting and updating source db records");
    // add new records and run again.
    // add a new record
    source.query(ctx -> ctx.execute("INSERT INTO id_and_name(id, name) VALUES(6, 'geralt')"));
    // mutate a record that was already synced with out updating its cursor value.
    // since this is a CDC connection, the destination should contain a record with this
    // new value and an updated_at time corresponding to this update query
    source.query(ctx -> ctx.execute("UPDATE id_and_name SET name='yennefer' WHERE id=2"));
    expectedIdAndNameRecords.add(new DestinationCdcRecordMatcher(
        Jsons.jsonNode(ImmutableMap.builder().put(COLUMN_ID, "6").put(COLUMN_NAME, "geralt").build()),
        beforeFirstUpdate,
        Optional.empty()));
    expectedIdAndNameRecords.add(new DestinationCdcRecordMatcher(
        Jsons.jsonNode(ImmutableMap.builder().put(COLUMN_ID, "2").put(COLUMN_NAME, "yennefer").build()),
        beforeFirstUpdate,
        Optional.empty()));

    // do the same for the other table
    source.query(ctx -> ctx.execute("INSERT INTO color_palette(id, color) VALUES(4, 'yellow')"));
    source.query(ctx -> ctx.execute("UPDATE color_palette SET color='purple' WHERE id=2"));
    expectedColorPaletteRecords.add(new DestinationCdcRecordMatcher(
        Jsons.jsonNode(ImmutableMap.builder().put(COLUMN_ID, "4").put(COLUMN_COLOR, "yellow").build()),
        beforeFirstUpdate,
        Optional.empty()));
    expectedColorPaletteRecords.add(new DestinationCdcRecordMatcher(
        Jsons.jsonNode(ImmutableMap.builder().put(COLUMN_ID, "2").put(COLUMN_COLOR, "purple").build()),
        beforeFirstUpdate,
        Optional.empty()));

    LOGGER.info("Starting {} sync 2", testInfo.getDisplayName());
    final JobInfoRead connectionSyncRead2 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead2.getJob());
    LOGGER.info("state after sync 2: {}", apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    assertDestinationMatches(ID_AND_NAME_TABLE, expectedIdAndNameRecords);
    assertDestinationMatches(COLOR_PALETTE_TABLE, expectedColorPaletteRecords);
    assertGlobalStateContainsStreams(connectionId, expectedStreams);

    // reset back to no data.

    LOGGER.info("Starting {} reset", testInfo.getDisplayName());
    final JobInfoRead jobInfoRead = apiClient.getConnectionApi().resetConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), jobInfoRead.getJob());

    LOGGER.info("state after reset: {}", apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    assertDestinationMatches(ID_AND_NAME_TABLE, Collections.emptyList());
    assertDestinationMatches(COLOR_PALETTE_TABLE, Collections.emptyList());
    assertNoState(connectionId);

    // sync one more time. verify it is the equivalent of a full refresh.
    LOGGER.info("Starting {} sync 3", testInfo.getDisplayName());
    final JobInfoRead connectionSyncRead3 =
        apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead3.getJob());
    LOGGER.info("state after sync 3: {}", apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    expectedIdAndNameRecords = getCdcRecordMatchersFromSource(source, ID_AND_NAME_TABLE);
    assertDestinationMatches(ID_AND_NAME_TABLE, expectedIdAndNameRecords);

    expectedColorPaletteRecords = getCdcRecordMatchersFromSource(source, COLOR_PALETTE_TABLE);
    assertDestinationMatches(COLOR_PALETTE_TABLE, expectedColorPaletteRecords);

    assertGlobalStateContainsStreams(connectionId, expectedStreams);
  }

  // tests that incremental syncs still work properly even when using a destination connector that was
  // built on the old protocol that did not have any per-stream state fields
  @Test
  void testIncrementalCdcSyncWithLegacyDestinationConnector(final TestInfo testInfo) throws Exception {
    LOGGER.info(STARTING, testInfo.getDisplayName());
    final UUID postgresDestDefId = testHarness.getPostgresDestinationDefinitionId();
    // Fetch the current/most recent source definition version
    final DestinationDefinitionRead destinationDefinitionRead = apiClient.getDestinationDefinitionApi().getDestinationDefinition(
        new DestinationDefinitionIdRequestBody().destinationDefinitionId(postgresDestDefId));
    LOGGER.info("Current postgres destination definition version: {}", destinationDefinitionRead.getDockerImageTag());

    try {
      LOGGER.info("Setting postgres destination definition to version {}", POSTGRES_DESTINATION_LEGACY_CONNECTOR_VERSION);
      testHarness.updateDestinationDefinitionVersion(postgresDestDefId, POSTGRES_DESTINATION_LEGACY_CONNECTOR_VERSION);

      testIncrementalCdcSync(testInfo);
    } finally {
      // set postgres destination definition back to latest version for other tests
      LOGGER.info("Setting postgres destination definition back to version {}", destinationDefinitionRead.getDockerImageTag());
      testHarness.updateDestinationDefinitionVersion(postgresDestDefId, destinationDefinitionRead.getDockerImageTag());
    }
  }

  @Test
  void testDeleteRecordCdcSync(final TestInfo testInfo) throws Exception {
    LOGGER.info(STARTING, testInfo.getDisplayName());

    final UUID connectionId = createCdcConnection();
    LOGGER.info(STARTING_SYNC_ONE, testInfo.getDisplayName());

    final JobInfoRead connectionSyncRead1 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead1.getJob());
    LOGGER.info("state after sync 1: {}", apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    final Database source = testHarness.getSourceDatabase();
    final List<DestinationCdcRecordMatcher> expectedIdAndNameRecords = getCdcRecordMatchersFromSource(source, ID_AND_NAME_TABLE);
    assertDestinationMatches(ID_AND_NAME_TABLE, expectedIdAndNameRecords);

    final Instant beforeDelete = Instant.now();

    LOGGER.info("Deleting record");
    // delete a record
    source.query(ctx -> ctx.execute("DELETE FROM id_and_name WHERE id=1"));

    final Map<String, Object> deletedRecordMap = new HashMap<>();
    deletedRecordMap.put(COLUMN_ID, "1");
    deletedRecordMap.put(COLUMN_NAME, null);
    expectedIdAndNameRecords.add(new DestinationCdcRecordMatcher(
        Jsons.jsonNode(deletedRecordMap),
        beforeDelete,
        Optional.of(beforeDelete)));

    LOGGER.info("Starting {} sync 2", testInfo.getDisplayName());
    final JobInfoRead connectionSyncRead2 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead2.getJob());
    LOGGER.info("state after sync 2: {}", apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    assertDestinationMatches(ID_AND_NAME_TABLE, expectedIdAndNameRecords);
  }

  @Test
  void testPartialResetFromSchemaUpdate(final TestInfo testInfo) throws Exception {
    LOGGER.info(STARTING, testInfo.getDisplayName());

    final UUID connectionId = createCdcConnection();
    LOGGER.info(STARTING_SYNC_ONE, testInfo.getDisplayName());

    final JobInfoRead connectionSyncRead1 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead1.getJob());

    final Database source = testHarness.getSourceDatabase();

    final List<DestinationCdcRecordMatcher> expectedIdAndNameRecords = getCdcRecordMatchersFromSource(source, ID_AND_NAME_TABLE);
    assertDestinationMatches(ID_AND_NAME_TABLE, expectedIdAndNameRecords);

    final List<DestinationCdcRecordMatcher> expectedColorPaletteRecords = getCdcRecordMatchersFromSource(source, COLOR_PALETTE_TABLE);
    assertDestinationMatches(COLOR_PALETTE_TABLE, expectedColorPaletteRecords);

    final StreamDescriptor idAndNameStreamDescriptor = new StreamDescriptor().namespace(SCHEMA_NAME).name(ID_AND_NAME_TABLE);
    final StreamDescriptor colorPaletteStreamDescriptor = new StreamDescriptor().namespace(SCHEMA_NAME).name(COLOR_PALETTE_TABLE);
    assertGlobalStateContainsStreams(connectionId, List.of(idAndNameStreamDescriptor, colorPaletteStreamDescriptor));

    LOGGER.info("Removing color palette table");
    source.query(ctx -> ctx.dropTable(COLOR_PALETTE_TABLE).execute());

    LOGGER.info("Refreshing schema and updating connection");
    final ConnectionRead connectionRead = apiClient.getConnectionApi().getConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    final UUID sourceId = createCdcSource().getSourceId();
    final AirbyteCatalog refreshedCatalog = testHarness.discoverSourceSchema(sourceId);
    LOGGER.info("Refreshed catalog: {}", refreshedCatalog);
    final WebBackendConnectionUpdate update = testHarness.getUpdateInput(connectionRead, refreshedCatalog, operationRead);
    webBackendApi.webBackendUpdateConnection(update);

    LOGGER.info("Waiting for sync job after update to complete");
    final JobRead syncFromTheUpdate = testHarness.waitUntilTheNextJobIsStarted(connectionId);
    waitForSuccessfulJob(apiClient.getJobsApi(), syncFromTheUpdate);

    // We do not check that the source and the dest are in sync here because removing a stream doesn't
    // delete its data in the destination
    assertGlobalStateContainsStreams(connectionId, List.of(idAndNameStreamDescriptor));
  }

  @Test
  void testPartialResetFromStreamSelection(final TestInfo testInfo) throws Exception {
    LOGGER.info(STARTING, testInfo.getDisplayName());

    final UUID connectionId = createCdcConnection();
    LOGGER.info(STARTING_SYNC_ONE, testInfo.getDisplayName());

    final JobInfoRead connectionSyncRead1 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead1.getJob());

    final Database source = testHarness.getSourceDatabase();

    final List<DestinationCdcRecordMatcher> expectedIdAndNameRecords = getCdcRecordMatchersFromSource(source, ID_AND_NAME_TABLE);
    assertDestinationMatches(ID_AND_NAME_TABLE, expectedIdAndNameRecords);

    final List<DestinationCdcRecordMatcher> expectedColorPaletteRecords = getCdcRecordMatchersFromSource(source, COLOR_PALETTE_TABLE);
    assertDestinationMatches(COLOR_PALETTE_TABLE, expectedColorPaletteRecords);

    final StreamDescriptor idAndNameStreamDescriptor = new StreamDescriptor().namespace(SCHEMA_NAME).name(ID_AND_NAME_TABLE);
    final StreamDescriptor colorPaletteStreamDescriptor = new StreamDescriptor().namespace(SCHEMA_NAME).name(COLOR_PALETTE_TABLE);
    assertGlobalStateContainsStreams(connectionId, List.of(idAndNameStreamDescriptor, colorPaletteStreamDescriptor));

    LOGGER.info("Removing color palette stream from configured catalog");
    final ConnectionRead connectionRead = apiClient.getConnectionApi().getConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    final UUID sourceId = connectionRead.getSourceId();
    AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    final List<AirbyteStreamAndConfiguration> streams = catalog.getStreams();
    // filter out color_palette stream
    final List<AirbyteStreamAndConfiguration> updatedStreams = streams
        .stream()
        .filter(stream -> !COLOR_PALETTE_TABLE.equals(stream.getStream().getName()))
        .toList();
    catalog.setStreams(updatedStreams);
    LOGGER.info("Updated catalog: {}", catalog);
    WebBackendConnectionUpdate update = testHarness.getUpdateInput(connectionRead, catalog, operationRead);
    webBackendApi.webBackendUpdateConnection(update);

    LOGGER.info("Waiting for sync job after update to start");
    JobRead syncFromTheUpdate = testHarness.waitUntilTheNextJobIsStarted(connectionId);
    LOGGER.info("Waiting for sync job after update to complete");
    waitForSuccessfulJob(apiClient.getJobsApi(), syncFromTheUpdate);

    // We do not check that the source and the dest are in sync here because removing a stream doesn't
    // delete its data in the destination
    assertGlobalStateContainsStreams(connectionId, List.of(idAndNameStreamDescriptor));

    LOGGER.info("Adding color palette stream back to configured catalog");
    catalog = testHarness.discoverSourceSchema(sourceId);
    LOGGER.info("Updated catalog: {}", catalog);
    update = testHarness.getUpdateInput(connectionRead, catalog, operationRead);
    webBackendApi.webBackendUpdateConnection(update);

    LOGGER.info("Waiting for sync job after update to start");
    syncFromTheUpdate = testHarness.waitUntilTheNextJobIsStarted(connectionId);
    LOGGER.info("Checking that id_and_name table is unaffected by the partial reset");
    assertDestinationMatches(ID_AND_NAME_TABLE, expectedIdAndNameRecords);
    LOGGER.info("Checking that color_palette table was cleared in the destination due to the reset triggered by the update");
    assertDestinationMatches(COLOR_PALETTE_TABLE, List.of());
    LOGGER.info("Waiting for sync job after update to complete");
    waitForSuccessfulJob(apiClient.getJobsApi(), syncFromTheUpdate);

    // Verify that color palette table records exist in destination again after sync.
    // If we see 0 records for this table in the destination, that means the CDC partial reset logic is
    // not working properly, and it continued from the replication log cursor for this stream despite
    // this stream's state being reset
    assertDestinationMatches(COLOR_PALETTE_TABLE, expectedColorPaletteRecords);
    assertGlobalStateContainsStreams(connectionId, List.of(idAndNameStreamDescriptor, colorPaletteStreamDescriptor));

    // Verify that incremental still works properly after partial reset
    LOGGER.info("Adding new records to tables");
    final Instant beforeInsert = Instant.now();
    source.query(ctx -> ctx.execute("INSERT INTO id_and_name(id, name) VALUES(6, 'geralt')"));
    expectedIdAndNameRecords.add(new DestinationCdcRecordMatcher(
        Jsons.jsonNode(ImmutableMap.builder().put(COLUMN_ID, "6").put(COLUMN_NAME, "geralt").build()),
        beforeInsert,
        Optional.empty()));

    source.query(ctx -> ctx.execute("INSERT INTO color_palette(id, color) VALUES(4, 'yellow')"));
    expectedColorPaletteRecords.add(new DestinationCdcRecordMatcher(
        Jsons.jsonNode(ImmutableMap.builder().put(COLUMN_ID, "4").put(COLUMN_COLOR, "yellow").build()),
        beforeInsert,
        Optional.empty()));

    LOGGER.info("Starting {} sync after insert", testInfo.getDisplayName());
    final JobInfoRead connectionSyncRead2 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead2.getJob());

    assertDestinationMatches(ID_AND_NAME_TABLE, expectedIdAndNameRecords);
    assertDestinationMatches(COLOR_PALETTE_TABLE, expectedColorPaletteRecords);
    assertGlobalStateContainsStreams(connectionId, List.of(idAndNameStreamDescriptor, colorPaletteStreamDescriptor));
  }

  private List<DestinationCdcRecordMatcher> getCdcRecordMatchersFromSource(final Database source, final String tableName) throws SQLException {
    final List<JsonNode> sourceRecords = testHarness.retrieveSourceRecords(source, tableName);
    return new ArrayList<>(sourceRecords
        .stream()
        .map(sourceRecord -> new DestinationCdcRecordMatcher(sourceRecord, Instant.EPOCH, Optional.empty()))
        .toList());
  }

  private UUID createCdcConnection() throws ApiException {
    final SourceRead sourceRead = createCdcSource();
    final UUID sourceId = sourceRead.getSourceId();
    final UUID destinationId = testHarness.createPostgresDestination().getDestinationId();

    operationRead = testHarness.createOperation();
    final UUID operationId = operationRead.getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    final AirbyteStream stream = catalog.getStreams().get(0).getStream();
    LOGGER.info("stream: {}", stream);

    assertEquals(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL), stream.getSupportedSyncModes());
    assertTrue(stream.getSourceDefinedCursor());
    assertTrue(stream.getDefaultCursorField().isEmpty());
    assertEquals(List.of(List.of("id")), stream.getSourceDefinedPrimaryKey());

    final SyncMode syncMode = SyncMode.INCREMENTAL;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.APPEND;
    catalog.getStreams().forEach(s -> s.getConfig()
        .syncMode(syncMode)
        .cursorField(List.of(COLUMN_ID))
        .destinationSyncMode(destinationSyncMode));
    final UUID connectionId =
        testHarness.createConnection(CONNECTION_NAME, sourceId, destinationId, List.of(operationId), catalog, ConnectionScheduleType.MANUAL, null)
            .getConnectionId();
    return connectionId;
  }

  private SourceRead createCdcSource() throws ApiException {
    final UUID postgresSourceDefinitionId = testHarness.getPostgresSourceDefinitionId();
    final JsonNode sourceDbConfig = testHarness.getSourceDbConfig();
    final Map<Object, Object> sourceDbConfigMap = Jsons.object(sourceDbConfig, Map.class);
    sourceDbConfigMap.put("is_test", true);
    sourceDbConfigMap.put("replication_method", ImmutableMap.builder()
        .put("method", CDC_METHOD)
        .put("replication_slot", REPLICATION_SLOT)
        .put("publication", PUBLICATION)
        .put("initial_waiting_seconds", INITIAL_WAITING_SECONDS)
        .build());
    LOGGER.info("final sourceDbConfigMap: {}", sourceDbConfigMap);

    return testHarness.createSource(
        SOURCE_NAME,
        workspaceId,
        postgresSourceDefinitionId,
        Jsons.jsonNode(sourceDbConfigMap));
  }

  @SuppressWarnings("PMD.AvoidLiteralsInIfCondition")
  private void assertDestinationMatches(final String streamName, final List<DestinationCdcRecordMatcher> expectedDestRecordMatchers)
      throws Exception {
    final List<JsonNode> destRecords = testHarness.retrieveRawDestinationRecords(new SchemaTableNamePair(SCHEMA_NAME, streamName));
    if (destRecords.size() != expectedDestRecordMatchers.size()) {
      final String errorMessage = String.format(
          "The number of destination records %d does not match the expected number %d",
          destRecords.size(),
          expectedDestRecordMatchers.size());
      LOGGER.error(errorMessage);
      LOGGER.error("Expected dest record matchers: {}\nActual destination records: {}", expectedDestRecordMatchers, destRecords);
      throw new IllegalStateException(errorMessage);
    }

    for (final DestinationCdcRecordMatcher recordMatcher : expectedDestRecordMatchers) {
      final List<JsonNode> matchingDestRecords = destRecords.stream().filter(destRecord -> {
        final Map<String, Object> sourceRecordMap = Jsons.object(recordMatcher.sourceRecord, Map.class);
        final Map<String, Object> destRecordMap = Jsons.object(destRecord, Map.class);

        final boolean sourceRecordValuesMatch = sourceRecordMap.keySet()
            .stream()
            .allMatch(column -> Objects.equals(sourceRecordMap.get(column), destRecordMap.get(column)));

        final Object cdcUpdatedAtValue = destRecordMap.get(CDC_UPDATED_AT_COLUMN);
        // use epoch millis to guarantee the two values are at the same precision
        final boolean cdcUpdatedAtMatches = cdcUpdatedAtValue != null
            && Instant.parse(String.valueOf(cdcUpdatedAtValue)).toEpochMilli() >= recordMatcher.minUpdatedAt.toEpochMilli();

        final Object cdcDeletedAtValue = destRecordMap.get(CDC_DELETED_AT_COLUMN);
        final boolean cdcDeletedAtMatches;
        if (recordMatcher.minDeletedAt.isPresent()) {
          cdcDeletedAtMatches = cdcDeletedAtValue != null
              && Instant.parse(String.valueOf(cdcDeletedAtValue)).toEpochMilli() >= recordMatcher.minDeletedAt.get().toEpochMilli();
        } else {
          cdcDeletedAtMatches = cdcDeletedAtValue == null;
        }

        return sourceRecordValuesMatch && cdcUpdatedAtMatches && cdcDeletedAtMatches;
      }).toList();

      if (matchingDestRecords.isEmpty()) {
        throw new IllegalStateException(String.format(
            "Could not find a matching CDC destination record for record matcher %s. Destination records: %s", recordMatcher, destRecords));
      }
      if (matchingDestRecords.size() > 1) {
        throw new IllegalStateException(String.format(
            "Expected only one matching CDC destination record for record matcher %s, but found multiple: %s", recordMatcher, matchingDestRecords));
      }
    }
  }

  private void assertGlobalStateContainsStreams(final UUID connectionId, final List<StreamDescriptor> expectedStreams) throws ApiException {
    final ConnectionState state = apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId));
    LOGGER.info("state: {}", state);
    assertEquals(ConnectionStateType.GLOBAL, state.getStateType());
    final List<StreamDescriptor> stateStreams = state.getGlobalState().getStreamStates().stream().map(StreamState::getStreamDescriptor).toList();

    Assertions.assertTrue(stateStreams.containsAll(expectedStreams) && expectedStreams.containsAll(stateStreams),
        String.format("Expected state to have streams %s, but it actually had streams %s", expectedStreams, stateStreams));
  }

  private void assertNoState(final UUID connectionId) throws ApiException {
    final ConnectionState state = apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId));
    assertEquals(ConnectionStateType.NOT_SET, state.getStateType());
    assertNull(state.getState());
    assertNull(state.getStreamState());
    assertNull(state.getGlobalState());
  }

  // can be helpful for debugging
  @SuppressWarnings("PMD.UnusedPrivateMethod")
  private void printDbs() throws SQLException {
    final Database sourceDb = testHarness.getSourceDatabase();
    Set<SchemaTableNamePair> pairs = testHarness.listAllTables(sourceDb);
    LOGGER.info("Printing source tables");
    for (final SchemaTableNamePair pair : pairs) {
      final Result<Record> result = sourceDb.query(context -> context.fetch(String.format("SELECT * FROM %s.%s", pair.schemaName, pair.tableName)));
      LOGGER.info("{}.{} contents:\n{}", pair.schemaName, pair.tableName, result);
    }

    final Database destDb = testHarness.getDestinationDatabase();
    pairs = testHarness.listAllTables(destDb);
    LOGGER.info("Printing destination tables");
    for (final SchemaTableNamePair pair : pairs) {
      final Result<Record> result = destDb.query(context -> context.fetch(String.format("SELECT * FROM %s.%s", pair.schemaName, pair.tableName)));
      LOGGER.info("{}.{} contents:\n{}", pair.schemaName, pair.tableName, result);
    }
  }

}
