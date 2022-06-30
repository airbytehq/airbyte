/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.acceptance;

import static io.airbyte.api.client.model.generated.ConnectionSchedule.TimeUnitEnum.MINUTES;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.COLUMN_ID;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.COLUMN_NAME;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.STREAM_NAME;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.waitForSuccessfulJob;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.waitWhileJobHasStatus;
import static java.lang.Thread.sleep;
import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.invoker.generated.ApiClient;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.*;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.test.utils.AirbyteAcceptanceTestHarness;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import io.airbyte.test.utils.SchemaTableNamePair;
import io.airbyte.workers.temporal.scheduling.state.WorkflowState;
import java.io.IOException;
import java.net.URISyntaxException;
import java.sql.SQLException;
import java.time.Duration;
import java.util.*;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.condition.DisabledIfEnvironmentVariable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

/**
 * This class tests for api functionality and basic sync functionality.
 * <p>
 * Due to the number of tests here, this set runs only on the docker deployment for speed. The tests
 * here are disabled for Kubernetes as operations take much longer due to Kubernetes pod spin up
 * times and there is little value in re-running these tests since this part of the system does not
 * vary between deployments.
 * <p>
 * We order tests such that earlier tests test more basic behavior relied upon in later tests. e.g.
 * We test that we can create a destination before we test whether we can sync data to it.
 */
@DisabledIfEnvironmentVariable(named = "KUBE",
                               matches = "true")
public class BasicAcceptanceTests {

  private static final Logger LOGGER = LoggerFactory.getLogger(BasicAcceptanceTests.class);

  private static final Boolean WITH_SCD_TABLE = true;

  private static final Boolean WITHOUT_SCD_TABLE = false;

  private static AirbyteAcceptanceTestHarness testHarness;
  private static AirbyteApiClient apiClient;
  private static UUID workspaceId;
  private static PostgreSQLContainer sourcePsql;

  @BeforeAll
  public static void init() throws URISyntaxException, IOException, InterruptedException, ApiException {
    apiClient = new AirbyteApiClient(
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

    testHarness = new AirbyteAcceptanceTestHarness(apiClient, workspaceId);
    sourcePsql = testHarness.getSourcePsql();
  }

  @AfterAll
  public static void end() {
    testHarness.stopDbAndContainers();
  }

  @BeforeEach
  public void setup() throws SQLException, URISyntaxException, IOException {
    testHarness.setup();
  }

  @AfterEach
  public void tearDown() {
    testHarness.cleanup();
  }

  @Test
  @Order(-2)
  public void testGetDestinationSpec() throws ApiException {
    final UUID destinationDefinitionId = testHarness.getDestinationDefId();
    final DestinationDefinitionSpecificationRead spec = apiClient.getDestinationDefinitionSpecificationApi()
        .getDestinationDefinitionSpecification(
            new DestinationDefinitionIdWithWorkspaceId().destinationDefinitionId(destinationDefinitionId).workspaceId(UUID.randomUUID()));
    assertEquals(destinationDefinitionId, spec.getDestinationDefinitionId());
    assertNotNull(spec.getConnectionSpecification());
  }

  @Test
  @Order(-1)
  public void testFailedGet404() {
    final var e = assertThrows(ApiException.class, () -> apiClient.getDestinationDefinitionSpecificationApi()
        .getDestinationDefinitionSpecification(
            new DestinationDefinitionIdWithWorkspaceId().destinationDefinitionId(UUID.randomUUID()).workspaceId(UUID.randomUUID())));
    assertEquals(404, e.getCode());
  }

  @Test
  @Order(0)
  public void testGetSourceSpec() throws ApiException {
    final UUID sourceDefId = testHarness.getPostgresSourceDefinitionId();
    final SourceDefinitionSpecificationRead spec = apiClient.getSourceDefinitionSpecificationApi()
        .getSourceDefinitionSpecification(new SourceDefinitionIdWithWorkspaceId().sourceDefinitionId(sourceDefId).workspaceId(UUID.randomUUID()));
    assertEquals(sourceDefId, spec.getSourceDefinitionId());
    assertNotNull(spec.getConnectionSpecification());
  }

  @Test
  @Order(1)
  public void testCreateDestination() throws ApiException {
    final UUID destinationDefId = testHarness.getDestinationDefId();
    final JsonNode destinationConfig = testHarness.getDestinationDbConfig();
    final String name = "AccTestDestinationDb-" + UUID.randomUUID();

    final DestinationRead createdDestination = testHarness.createDestination(
        name,
        workspaceId,
        destinationDefId,
        destinationConfig);

    assertEquals(name, createdDestination.getName());
    assertEquals(destinationDefId, createdDestination.getDestinationDefinitionId());
    assertEquals(workspaceId, createdDestination.getWorkspaceId());
    assertEquals(testHarness.getDestinationDbConfigWithHiddenPassword(), createdDestination.getConnectionConfiguration());
  }

  @Test
  @Order(2)
  public void testDestinationCheckConnection() throws ApiException {
    final UUID destinationId = testHarness.createDestination().getDestinationId();

    final CheckConnectionRead.StatusEnum checkOperationStatus = apiClient.getDestinationApi()
        .checkConnectionToDestination(new DestinationIdRequestBody().destinationId(destinationId))
        .getStatus();

    assertEquals(CheckConnectionRead.StatusEnum.SUCCEEDED, checkOperationStatus);
  }

  @Test
  @Order(3)
  public void testCreateSource() throws ApiException {
    final String dbName = "acc-test-db";
    final UUID postgresSourceDefinitionId = testHarness.getPostgresSourceDefinitionId();
    final JsonNode sourceDbConfig = testHarness.getSourceDbConfig();

    final SourceRead response = testHarness.createSource(
        dbName,
        workspaceId,
        postgresSourceDefinitionId,
        sourceDbConfig);

    final JsonNode expectedConfig = Jsons.jsonNode(sourceDbConfig);
    // expect replacement of secret with magic string.
    ((ObjectNode) expectedConfig).put("password", "**********");
    assertEquals(dbName, response.getName());
    assertEquals(workspaceId, response.getWorkspaceId());
    assertEquals(postgresSourceDefinitionId, response.getSourceDefinitionId());
    assertEquals(expectedConfig, response.getConnectionConfiguration());
  }

  @Test
  @Order(4)
  public void testSourceCheckConnection() throws ApiException {
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();

    final CheckConnectionRead checkConnectionRead = apiClient.getSourceApi().checkConnectionToSource(new SourceIdRequestBody().sourceId(sourceId));

    assertEquals(
        CheckConnectionRead.StatusEnum.SUCCEEDED,
        checkConnectionRead.getStatus(),
        checkConnectionRead.getMessage());
  }

  @Test
  @Order(5)
  public void testDiscoverSourceSchema() throws ApiException {
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();

    final AirbyteCatalog actual = testHarness.discoverSourceSchema(sourceId);

    final Map<String, Map<String, DataType>> fields = ImmutableMap.of(
        COLUMN_ID, ImmutableMap.of("type", DataType.NUMBER),
        COLUMN_NAME, ImmutableMap.of("type", DataType.STRING));
    final JsonNode jsonSchema = Jsons.jsonNode(ImmutableMap.builder()
        .put("type", "object")
        .put("properties", fields)
        .build());
    final AirbyteStream stream = new AirbyteStream()
        .name(STREAM_NAME)
        .namespace("public")
        .jsonSchema(jsonSchema)
        .sourceDefinedCursor(null)
        .defaultCursorField(Collections.emptyList())
        .sourceDefinedPrimaryKey(Collections.emptyList())
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
    final AirbyteStreamConfiguration streamConfig = new AirbyteStreamConfiguration()
        .syncMode(SyncMode.FULL_REFRESH)
        .cursorField(Collections.emptyList())
        .destinationSyncMode(DestinationSyncMode.APPEND)
        .primaryKey(Collections.emptyList())
        .aliasName(STREAM_NAME.replace(".", "_"))
        .selected(true);
    final AirbyteCatalog expected = new AirbyteCatalog()
        .streams(Lists.newArrayList(new AirbyteStreamAndConfiguration()
            .stream(stream)
            .config(streamConfig)));

    assertEquals(expected, actual);
  }

  @Test
  @Order(6)
  public void testCreateConnection() throws ApiException {
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    final UUID destinationId = testHarness.createDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final String name = "test-connection-" + UUID.randomUUID();
    final ConnectionSchedule schedule = new ConnectionSchedule().timeUnit(MINUTES).units(100L);
    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));
    final ConnectionRead createdConnection =
        testHarness.createConnection(name, sourceId, destinationId, List.of(operationId), catalog, schedule);

    assertEquals(sourceId, createdConnection.getSourceId());
    assertEquals(destinationId, createdConnection.getDestinationId());
    assertEquals(1, createdConnection.getOperationIds().size());
    assertEquals(operationId, createdConnection.getOperationIds().get(0));
    assertEquals(catalog, createdConnection.getSyncCatalog());
    assertEquals(schedule, createdConnection.getSchedule());
    assertEquals(name, createdConnection.getName());
  }

  @Test
  @Order(7)
  public void testCancelSync() throws Exception {
    final SourceDefinitionRead sourceDefinition = testHarness.createE2eSourceDefinition();

    final SourceRead source = testHarness.createSource(
        "E2E Test Source -" + UUID.randomUUID(),
        workspaceId,
        sourceDefinition.getSourceDefinitionId(),
        Jsons.jsonNode(ImmutableMap.builder()
            .put("type", "INFINITE_FEED")
            .put("message_interval", 1000)
            .put("max_records", Duration.ofMinutes(5).toSeconds())
            .build()));

    final String connectionName = "test-connection";
    final UUID sourceId = source.getSourceId();
    final UUID destinationId = testHarness.createDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));
    final UUID connectionId =
        testHarness.createConnection(connectionName, sourceId, destinationId, List.of(operationId), catalog, null).getConnectionId();
    final JobInfoRead connectionSyncRead = apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));

    // wait to get out of PENDING
    final JobRead jobRead = waitWhileJobHasStatus(apiClient.getJobsApi(), connectionSyncRead.getJob(), Set.of(JobStatus.PENDING));
    assertEquals(JobStatus.RUNNING, jobRead.getStatus());

    final var resp = apiClient.getJobsApi().cancelJob(new JobIdRequestBody().id(connectionSyncRead.getJob().getId()));
    assertEquals(JobStatus.CANCELLED, resp.getJob().getStatus());
  }

  @Test
  @Order(8)
  public void testScheduledSync() throws Exception {
    final String connectionName = "test-connection";
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);

    final ConnectionSchedule connectionSchedule = new ConnectionSchedule().units(1L).timeUnit(MINUTES);
    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));

    final var conn =
        testHarness.createConnection(connectionName, sourceId, destinationId, List.of(operationId), catalog, connectionSchedule);

    // When a new connection is created, Airbyte might sync it immediately (before the sync interval).
    // Then it will wait the sync interval.
    // if the wait isn't long enough, failures say "Connection refused" because the assert kills the
    // syncs in progress
    List<io.airbyte.api.client.model.generated.JobWithAttemptsRead> jobs = new ArrayList<>();
    while (jobs.size() < 2) {
      final var listSyncJobsRequest = new io.airbyte.api.client.model.generated.JobListRequestBody().configTypes(List.of(JobConfigType.SYNC))
          .configId(conn.getConnectionId().toString());
      final var resp = apiClient.getJobsApi().listJobsFor(listSyncJobsRequest);
      jobs = resp.getJobs();
      sleep(Duration.ofSeconds(30).toMillis());
    }

    testHarness.assertSourceAndDestinationDbInSync(WITHOUT_SCD_TABLE);
  }

  @Test
  @Order(9)
  public void testMultipleSchemasAndTablesSync() throws Exception {
    // create tables in another schema
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forClasspathResource("postgres_second_schema_multiple_tables.sql"), sourcePsql);

    final String connectionName = "test-connection";
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);

    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));
    final UUID connectionId =
        testHarness.createConnection(connectionName, sourceId, destinationId, List.of(operationId), catalog, null).getConnectionId();
    final JobInfoRead connectionSyncRead = apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead.getJob());
    testHarness.assertSourceAndDestinationDbInSync(false);
  }

  @Test
  @Order(10)
  public void testMultipleSchemasSameTablesSync() throws Exception {
    // create tables in another schema
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forClasspathResource("postgres_separate_schema_same_table.sql"), sourcePsql);

    final String connectionName = "test-connection";
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);

    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));
    final UUID connectionId =
        testHarness.createConnection(connectionName, sourceId, destinationId, List.of(operationId), catalog, null).getConnectionId();

    final JobInfoRead connectionSyncRead = apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead.getJob());
    testHarness.assertSourceAndDestinationDbInSync(WITHOUT_SCD_TABLE);
  }

  @Test
  @Order(11)
  public void testIncrementalDedupeSync() throws Exception {
    final String connectionName = "test-connection";
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    final SyncMode syncMode = SyncMode.INCREMENTAL;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.APPEND_DEDUP;
    catalog.getStreams().forEach(s -> s.getConfig()
        .syncMode(syncMode)
        .cursorField(List.of(COLUMN_ID))
        .destinationSyncMode(destinationSyncMode)
        .primaryKey(List.of(List.of(COLUMN_NAME))));
    final UUID connectionId =
        testHarness.createConnection(connectionName, sourceId, destinationId, List.of(operationId), catalog, null).getConnectionId();

    // sync from start
    final JobInfoRead connectionSyncRead1 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead1.getJob());

    testHarness.assertSourceAndDestinationDbInSync(WITH_SCD_TABLE);

    // add new records and run again.
    final Database source = testHarness.getSourceDatabase();
    final List<JsonNode> expectedRawRecords = testHarness.retrieveSourceRecords(source, STREAM_NAME);
    expectedRawRecords.add(Jsons.jsonNode(ImmutableMap.builder().put(COLUMN_ID, 6).put(COLUMN_NAME, "sherif").build()));
    expectedRawRecords.add(Jsons.jsonNode(ImmutableMap.builder().put(COLUMN_ID, 7).put(COLUMN_NAME, "chris").build()));
    source.query(ctx -> ctx.execute("UPDATE id_and_name SET id=6 WHERE name='sherif'"));
    source.query(ctx -> ctx.execute("INSERT INTO id_and_name(id, name) VALUES(7, 'chris')"));
    // retrieve latest snapshot of source records after modifications; the deduplicated table in
    // destination should mirror this latest state of records
    final List<JsonNode> expectedNormalizedRecords = testHarness.retrieveSourceRecords(source, STREAM_NAME);

    final JobInfoRead connectionSyncRead2 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead2.getJob());

    testHarness.assertRawDestinationContains(expectedRawRecords, new SchemaTableNamePair("public", STREAM_NAME));
    testHarness.assertNormalizedDestinationContains(expectedNormalizedRecords);
  }

  @Test
  @Order(12)
  public void testIncrementalSync() throws Exception {
    LOGGER.info("Starting testIncrementalSync()");
    final String connectionName = "test-connection";
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    final AirbyteStream stream = catalog.getStreams().get(0).getStream();

    assertEquals(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL), stream.getSupportedSyncModes());
    // instead of assertFalse to avoid NPE from unboxed.
    assertNull(stream.getSourceDefinedCursor());
    assertTrue(stream.getDefaultCursorField().isEmpty());
    assertTrue(stream.getSourceDefinedPrimaryKey().isEmpty());

    final SyncMode syncMode = SyncMode.INCREMENTAL;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.APPEND;
    catalog.getStreams().forEach(s -> s.getConfig()
        .syncMode(syncMode)
        .cursorField(List.of(COLUMN_ID))
        .destinationSyncMode(destinationSyncMode));
    final UUID connectionId =
        testHarness.createConnection(connectionName, sourceId, destinationId, List.of(operationId), catalog, null).getConnectionId();
    LOGGER.info("Beginning testIncrementalSync() sync 1");

    final JobInfoRead connectionSyncRead1 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead1.getJob());
    LOGGER.info("state after sync 1: {}", apiClient.getConnectionApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    testHarness.assertSourceAndDestinationDbInSync(WITHOUT_SCD_TABLE);

    // add new records and run again.
    final Database source = testHarness.getSourceDatabase();
    // get contents of source before mutating records.
    final List<JsonNode> expectedRecords = testHarness.retrieveSourceRecords(source, STREAM_NAME);
    expectedRecords.add(Jsons.jsonNode(ImmutableMap.builder().put(COLUMN_ID, 6).put(COLUMN_NAME, "geralt").build()));
    // add a new record
    source.query(ctx -> ctx.execute("INSERT INTO id_and_name(id, name) VALUES(6, 'geralt')"));
    // mutate a record that was already synced with out updating its cursor value. if we are actually
    // full refreshing, this record will appear in the output and cause the test to fail. if we are,
    // correctly, doing incremental, we will not find this value in the destination.
    source.query(ctx -> ctx.execute("UPDATE id_and_name SET name='yennefer' WHERE id=2"));

    LOGGER.info("Starting testIncrementalSync() sync 2");
    final JobInfoRead connectionSyncRead2 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead2.getJob());
    LOGGER.info("state after sync 2: {}", apiClient.getConnectionApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    testHarness.assertRawDestinationContains(expectedRecords, new SchemaTableNamePair("public", STREAM_NAME));

    // reset back to no data.

    LOGGER.info("Starting testIncrementalSync() reset");
    final JobInfoRead jobInfoRead = apiClient.getConnectionApi().resetConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitWhileJobHasStatus(apiClient.getJobsApi(), jobInfoRead.getJob(),
        Sets.newHashSet(JobStatus.PENDING, JobStatus.RUNNING, JobStatus.INCOMPLETE, JobStatus.FAILED));

    LOGGER.info("state after reset: {}", apiClient.getConnectionApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    testHarness.assertRawDestinationContains(Collections.emptyList(), new SchemaTableNamePair("public",
        STREAM_NAME));

    // sync one more time. verify it is the equivalent of a full refresh.
    LOGGER.info("Starting testIncrementalSync() sync 3");
    final JobInfoRead connectionSyncRead3 =
        apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead3.getJob());
    LOGGER.info("state after sync 3: {}", apiClient.getConnectionApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    testHarness.assertSourceAndDestinationDbInSync(WITHOUT_SCD_TABLE);

  }

  @Test
  @Order(13)
  public void testDeleteConnection() throws Exception {
    final String connectionName = "test-connection";
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    final SyncMode syncMode = SyncMode.INCREMENTAL;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.APPEND_DEDUP;
    catalog.getStreams().forEach(s -> s.getConfig()
        .syncMode(syncMode)
        .cursorField(List.of(COLUMN_ID))
        .destinationSyncMode(destinationSyncMode)
        .primaryKey(List.of(List.of(COLUMN_NAME))));

    UUID connectionId =
        testHarness.createConnection(connectionName, sourceId, destinationId, List.of(operationId), catalog, null).getConnectionId();

    final JobInfoRead connectionSyncRead = apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitWhileJobHasStatus(apiClient.getJobsApi(), connectionSyncRead.getJob(), Set.of(JobStatus.RUNNING));

    // test normal deletion of connection
    LOGGER.info("Calling delete connection...");
    apiClient.getConnectionApi().deleteConnection(new ConnectionIdRequestBody().connectionId(connectionId));

    // remove connection to avoid exception during tear down
    // connectionIds.remove(connectionId); // todo remove
    testHarness.removeConnection(connectionId);

    LOGGER.info("Waiting for connection to be deleted...");
    Thread.sleep(500);

    ConnectionStatus connectionStatus =
        apiClient.getConnectionApi().getConnection(new ConnectionIdRequestBody().connectionId(connectionId)).getStatus();
    assertEquals(ConnectionStatus.DEPRECATED, connectionStatus);

    // test that repeated deletion call for same connection is successful
    LOGGER.info("Calling delete connection a second time to test repeat call behavior...");
    apiClient.getConnectionApi().deleteConnection(new ConnectionIdRequestBody().connectionId(connectionId));

    // test deletion of connection when temporal workflow is in a bad state
    LOGGER.info("Testing connection deletion when temporal is in a terminal state");
    connectionId =
        testHarness.createConnection(connectionName, sourceId, destinationId, List.of(operationId), catalog, null).getConnectionId();

    testHarness.terminateTemporalWorkflow(connectionId);

    // we should still be able to delete the connection when the temporal workflow is in this state
    apiClient.getConnectionApi().deleteConnection(new ConnectionIdRequestBody().connectionId(connectionId));

    LOGGER.info("Waiting for connection to be deleted...");
    Thread.sleep(500);

    connectionStatus = apiClient.getConnectionApi().getConnection(new ConnectionIdRequestBody().connectionId(connectionId)).getStatus();
    assertEquals(ConnectionStatus.DEPRECATED, connectionStatus);
  }

  @Test
  @Order(14)
  public void testUpdateConnectionWhenWorkflowUnreachable() throws Exception {
    // This test only covers the specific behavior of updating a connection that does not have an
    // underlying temporal workflow.
    // Also, this test doesn't verify correctness of the schedule update applied, as adding the ability
    // to query a workflow for its current
    // schedule is out of scope for the issue (https://github.com/airbytehq/airbyte/issues/11215). This
    // test just ensures that the underlying workflow
    // is running after the update method is called.
    final String connectionName = "test-connection";
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    catalog.getStreams().forEach(s -> s.getConfig()
        .syncMode(SyncMode.INCREMENTAL)
        .cursorField(List.of(COLUMN_ID))
        .destinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
        .primaryKey(List.of(List.of(COLUMN_NAME))));

    LOGGER.info("Testing connection update when temporal is in a terminal state");
    final UUID connectionId =
        testHarness.createConnection(connectionName, sourceId, destinationId, List.of(operationId), catalog, null).getConnectionId();

    testHarness.terminateTemporalWorkflow(connectionId);

    // we should still be able to update the connection when the temporal workflow is in this state
    testHarness.updateConnectionSchedule(connectionId,
        new ConnectionSchedule().timeUnit(ConnectionSchedule.TimeUnitEnum.HOURS).units(1L));

    LOGGER.info("Waiting for workflow to be recreated...");
    Thread.sleep(500);

    final WorkflowState workflowState = testHarness.getWorkflowState(connectionId);
    assertTrue(workflowState.isRunning());
  }

  @Test
  @Order(15)
  public void testManualSyncRepairsWorkflowWhenWorkflowUnreachable() throws Exception {
    // This test only covers the specific behavior of updating a connection that does not have an
    // underlying temporal workflow.
    final String connectionName = "test-connection";
    final SourceDefinitionRead sourceDefinition = testHarness.createE2eSourceDefinition();
    final SourceRead source = testHarness.createSource(
        "E2E Test Source -" + UUID.randomUUID(),
        workspaceId,
        sourceDefinition.getSourceDefinitionId(),
        Jsons.jsonNode(ImmutableMap.builder()
            .put("type", "INFINITE_FEED")
            .put("max_records", 5000)
            .put("message_interval", 100)
            .build()));
    final UUID sourceId = source.getSourceId();
    final UUID destinationId = testHarness.createDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    catalog.getStreams().forEach(s -> s.getConfig()
        .syncMode(SyncMode.INCREMENTAL)
        .cursorField(List.of(COLUMN_ID))
        .destinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
        .primaryKey(List.of(List.of(COLUMN_NAME))));

    LOGGER.info("Testing manual sync when temporal is in a terminal state");
    final UUID connectionId =
        testHarness.createConnection(connectionName, sourceId, destinationId, List.of(operationId), catalog, null).getConnectionId();

    LOGGER.info("Starting first manual sync");
    final JobInfoRead firstJobInfo = apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    LOGGER.info("Terminating workflow during first sync");
    testHarness.terminateTemporalWorkflow(connectionId);

    LOGGER.info("Submitted another manual sync");
    apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));

    LOGGER.info("Waiting for workflow to be recreated...");
    Thread.sleep(500);

    final WorkflowState workflowState = testHarness.getWorkflowState(connectionId);
    assertTrue(workflowState.isRunning());
    assertTrue(workflowState.isSkipScheduling());

    // verify that the first manual sync was marked as failed
    final JobInfoRead terminatedJobInfo = apiClient.getJobsApi().getJobInfo(new JobIdRequestBody().id(firstJobInfo.getJob().getId()));
    assertEquals(JobStatus.FAILED, terminatedJobInfo.getJob().getStatus());
  }

  @Test
  @Order(16)
  public void testResetConnectionRepairsWorkflowWhenWorkflowUnreachable() throws Exception {
    // This test only covers the specific behavior of updating a connection that does not have an
    // underlying temporal workflow.
    final String connectionName = "test-connection";
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    catalog.getStreams().forEach(s -> s.getConfig()
        .syncMode(SyncMode.INCREMENTAL)
        .cursorField(List.of(COLUMN_ID))
        .destinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
        .primaryKey(List.of(List.of(COLUMN_NAME))));

    LOGGER.info("Testing reset connection when temporal is in a terminal state");
    final UUID connectionId =
        testHarness.createConnection(connectionName, sourceId, destinationId, List.of(operationId), catalog, null).getConnectionId();

    testHarness.terminateTemporalWorkflow(connectionId);

    final JobInfoRead jobInfoRead = apiClient.getConnectionApi().resetConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    assertEquals(JobConfigType.RESET_CONNECTION, jobInfoRead.getJob().getConfigType());
  }

  @Test
  @Order(17)
  public void testResetCancelsRunningSync() throws Exception {
    final SourceDefinitionRead sourceDefinition = testHarness.createE2eSourceDefinition();

    final SourceRead source = testHarness.createSource(
        "E2E Test Source -" + UUID.randomUUID(),
        workspaceId,
        sourceDefinition.getSourceDefinitionId(),
        Jsons.jsonNode(ImmutableMap.builder()
            .put("type", "INFINITE_FEED")
            .put("message_interval", 1000)
            .put("max_records", Duration.ofMinutes(5).toSeconds())
            .build()));

    final String connectionName = "test-connection";
    final UUID sourceId = source.getSourceId();
    final UUID destinationId = testHarness.createDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));
    final UUID connectionId =
        testHarness.createConnection(connectionName, sourceId, destinationId, List.of(operationId), catalog, null).getConnectionId();
    final JobInfoRead connectionSyncRead = apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));

    // wait to get out of PENDING
    final JobRead jobRead = waitWhileJobHasStatus(apiClient.getJobsApi(), connectionSyncRead.getJob(), Set.of(JobStatus.PENDING));
    assertEquals(JobStatus.RUNNING, jobRead.getStatus());

    // send reset request while sync is still running
    final JobInfoRead jobInfoRead = apiClient.getConnectionApi().resetConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    assertEquals(JobConfigType.RESET_CONNECTION, jobInfoRead.getJob().getConfigType());

    // verify that sync job was cancelled
    final JobRead connectionSyncReadAfterReset =
        apiClient.getJobsApi().getJobInfo(new JobIdRequestBody().id(connectionSyncRead.getJob().getId())).getJob();
    assertEquals(JobStatus.CANCELLED, connectionSyncReadAfterReset.getStatus());
  }

  @Test
  public void testSyncAfterUpgradeToPerStreamState(final TestInfo testInfo) throws Exception {
    LOGGER.info("Starting {}", testInfo.getDisplayName());
    final String connectionName = "test-connection";
    final SourceRead source = testHarness.createPostgresSource();
    final UUID sourceId = source.getSourceId();
    final UUID sourceDefinitionId = source.getSourceDefinitionId();
    final UUID destinationId = testHarness.createDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);

    // Fetch the current/most recent source definition version
    final SourceDefinitionRead sourceDefinitionRead =
        apiClient.getSourceDefinitionApi().getSourceDefinition(new SourceDefinitionIdRequestBody().sourceDefinitionId(sourceDefinitionId));
    final String currentSourceDefintionVersion = sourceDefinitionRead.getDockerImageTag();

    // Set the source to a version that does not support per-stream state
    LOGGER.info("Setting source connector to pre-per-stream state version {}...",
        AirbyteAcceptanceTestHarness.POSTGRES_SOURCE_LEGACY_CONNECTOR_VERSION);
    testHarness.updateSourceDefinitionVersion(sourceDefinitionId, AirbyteAcceptanceTestHarness.POSTGRES_SOURCE_LEGACY_CONNECTOR_VERSION);

    catalog.getStreams().forEach(s -> s.getConfig()
        .syncMode(SyncMode.INCREMENTAL)
        .cursorField(List.of(COLUMN_ID))
        .destinationSyncMode(DestinationSyncMode.APPEND));
    final UUID connectionId =
        testHarness.createConnection(connectionName, sourceId, destinationId, List.of(operationId), catalog, null).getConnectionId();
    LOGGER.info("Beginning {} sync 1", testInfo.getDisplayName());

    final JobInfoRead connectionSyncRead1 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead1.getJob());
    LOGGER.info("state after sync 1: {}", apiClient.getConnectionApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    testHarness.assertSourceAndDestinationDbInSync(WITHOUT_SCD_TABLE);

    // Set source to a version that supports per-stream state
    testHarness.updateSourceDefinitionVersion(sourceDefinitionId, currentSourceDefintionVersion);
    LOGGER.info("Upgraded source connector per-stream state supported version {}.", currentSourceDefintionVersion);

    // add new records and run again.
    final Database sourceDatabase = testHarness.getSourceDatabase();
    // get contents of source before mutating records.
    final List<JsonNode> expectedRecords = testHarness.retrieveSourceRecords(sourceDatabase, STREAM_NAME);
    expectedRecords.add(Jsons.jsonNode(ImmutableMap.builder().put(COLUMN_ID, 6).put(COLUMN_NAME, "geralt").build()));
    // add a new record
    sourceDatabase.query(ctx -> ctx.execute("INSERT INTO id_and_name(id, name) VALUES(6, 'geralt')"));
    // mutate a record that was already synced with out updating its cursor value. if we are actually
    // full refreshing, this record will appear in the output and cause the test to fail. if we are,
    // correctly, doing incremental, we will not find this value in the destination.
    sourceDatabase.query(ctx -> ctx.execute("UPDATE id_and_name SET name='yennefer' WHERE id=2"));

    LOGGER.info("Starting {} sync 2", testInfo.getDisplayName());
    final JobInfoRead connectionSyncRead2 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead2.getJob());
    LOGGER.info("state after sync 2: {}", apiClient.getConnectionApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    testHarness.assertRawDestinationContains(expectedRecords, new SchemaTableNamePair("public", STREAM_NAME));

    // reset back to no data.
    LOGGER.info("Starting {} reset", testInfo.getDisplayName());
    final JobInfoRead jobInfoRead = apiClient.getConnectionApi().resetConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitWhileJobHasStatus(apiClient.getJobsApi(), jobInfoRead.getJob(),
        Sets.newHashSet(JobStatus.PENDING, JobStatus.RUNNING, JobStatus.INCOMPLETE, JobStatus.FAILED));

    LOGGER.info("state after reset: {}", apiClient.getConnectionApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    testHarness.assertRawDestinationContains(Collections.emptyList(), new SchemaTableNamePair("public",
        STREAM_NAME));

    // sync one more time. verify it is the equivalent of a full refresh.
    final String expectedState =
        "{\"cdc\":false,\"streams\":[{\"cursor\":\"6\",\"stream_name\":\"id_and_name\",\"cursor_field\":[\"id\"],\"stream_namespace\":\"public\"}]}";
    LOGGER.info("Starting {} sync 3", testInfo.getDisplayName());
    final JobInfoRead connectionSyncRead3 =
        apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead3.getJob());
    final ConnectionState state = apiClient.getConnectionApi().getState(new ConnectionIdRequestBody().connectionId(connectionId));
    LOGGER.info("state after sync 3: {}", state);

    testHarness.assertSourceAndDestinationDbInSync(WITHOUT_SCD_TABLE);
    assertEquals(Jsons.deserialize(expectedState), state.getState());
  }

  @Test
  public void testSyncAfterUpgradeToPerStreamStateWithNoNewData(final TestInfo testInfo) throws Exception {
    LOGGER.info("Starting {}", testInfo.getDisplayName());
    final String connectionName = "test-connection";
    final SourceRead source = testHarness.createPostgresSource();
    final UUID sourceId = source.getSourceId();
    final UUID sourceDefinitionId = source.getSourceDefinitionId();
    final UUID destinationId = testHarness.createDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);

    // Fetch the current/most recent source definition version
    final SourceDefinitionRead sourceDefinitionRead =
        apiClient.getSourceDefinitionApi().getSourceDefinition(new SourceDefinitionIdRequestBody().sourceDefinitionId(sourceDefinitionId));
    final String currentSourceDefintionVersion = sourceDefinitionRead.getDockerImageTag();

    // Set the source to a version that does not support per-stream state
    LOGGER.info("Setting source connector to pre-per-stream state version {}...",
        AirbyteAcceptanceTestHarness.POSTGRES_SOURCE_LEGACY_CONNECTOR_VERSION);
    testHarness.updateSourceDefinitionVersion(sourceDefinitionId, AirbyteAcceptanceTestHarness.POSTGRES_SOURCE_LEGACY_CONNECTOR_VERSION);

    catalog.getStreams().forEach(s -> s.getConfig()
        .syncMode(SyncMode.INCREMENTAL)
        .cursorField(List.of(COLUMN_ID))
        .destinationSyncMode(DestinationSyncMode.APPEND));
    final UUID connectionId =
        testHarness.createConnection(connectionName, sourceId, destinationId, List.of(operationId), catalog, null).getConnectionId();
    LOGGER.info("Beginning {} sync 1", testInfo.getDisplayName());

    final JobInfoRead connectionSyncRead1 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead1.getJob());
    LOGGER.info("state after sync 1: {}", apiClient.getConnectionApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    testHarness.assertSourceAndDestinationDbInSync(WITHOUT_SCD_TABLE);

    // Set source to a version that supports per-stream state
    testHarness.updateSourceDefinitionVersion(sourceDefinitionId, currentSourceDefintionVersion);
    LOGGER.info("Upgraded source connector per-stream state supported version {}.", currentSourceDefintionVersion);

    // sync one more time. verify that nothing has been synced
    LOGGER.info("Starting {} sync 2", testInfo.getDisplayName());
    final JobInfoRead connectionSyncRead2 =
        apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead2.getJob());
    LOGGER.info("state after sync 2: {}", apiClient.getConnectionApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    final JobInfoRead syncJob = apiClient.getJobsApi().getJobInfo(new JobIdRequestBody().id(connectionSyncRead2.getJob().getId()));
    final Optional<AttemptInfoRead> result = syncJob.getAttempts().stream()
        .sorted((a, b) -> Long.compare(b.getAttempt().getEndedAt(), a.getAttempt().getEndedAt()))
        .findFirst();

    assertTrue(result.isPresent());
    assertEquals(0, result.get().getAttempt().getRecordsSynced());
    assertEquals(0, result.get().getAttempt().getTotalStats().getRecordsEmitted());
    testHarness.assertSourceAndDestinationDbInSync(WITHOUT_SCD_TABLE);
  }

  // This test is disabled because it takes a couple of minutes to run, as it is testing timeouts.
  // It should be re-enabled when the @SlowIntegrationTest can be applied to it.
  // See relevant issue: https://github.com/airbytehq/airbyte/issues/8397
  @Disabled
  public void testFailureTimeout() throws Exception {
    final SourceDefinitionRead sourceDefinition = testHarness.createE2eSourceDefinition();
    final DestinationDefinitionRead destinationDefinition = testHarness.createE2eDestinationDefinition();

    final SourceRead source = testHarness.createSource(
        "E2E Test Source -" + UUID.randomUUID(),
        workspaceId,
        sourceDefinition.getSourceDefinitionId(),
        Jsons.jsonNode(ImmutableMap.builder()
            .put("type", "INFINITE_FEED")
            .put("max_records", 1000)
            .put("message_interval", 100)
            .build()));

    // Destination fails after processing 5 messages, so the job should fail after the graceful close
    // timeout of 1 minute
    final DestinationRead destination = testHarness.createDestination(
        "E2E Test Destination -" + UUID.randomUUID(),
        workspaceId,
        destinationDefinition.getDestinationDefinitionId(),
        Jsons.jsonNode(ImmutableMap.builder()
            .put("type", "FAILING")
            .put("num_messages", 5)
            .build()));

    final String connectionName = "test-connection";
    final UUID sourceId = source.getSourceId();
    final UUID destinationId = destination.getDestinationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);

    final UUID connectionId =
        testHarness.createConnection(connectionName, sourceId, destinationId, Collections.emptyList(), catalog, null)
            .getConnectionId();

    final JobInfoRead connectionSyncRead1 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));

    // wait to get out of pending.
    final JobRead runningJob =
        waitWhileJobHasStatus(apiClient.getJobsApi(), connectionSyncRead1.getJob(), Sets.newHashSet(JobStatus.PENDING));

    // wait for job for max of 3 minutes, by which time the job attempt should have failed
    waitWhileJobHasStatus(apiClient.getJobsApi(), runningJob, Sets.newHashSet(JobStatus.RUNNING), Duration.ofMinutes(3));

    final JobIdRequestBody jobId = new JobIdRequestBody().id(runningJob.getId());
    final JobInfoRead jobInfo = apiClient.getJobsApi().getJobInfo(jobId);
    final AttemptInfoRead attemptInfoRead = jobInfo.getAttempts().get(jobInfo.getAttempts().size() - 1);

    // assert that the job attempt failed, and cancel the job regardless of status to prevent retries
    try {
      assertEquals(AttemptStatus.FAILED, attemptInfoRead.getAttempt().getStatus());
    } finally {
      apiClient.getJobsApi().cancelJob(jobId);
    }
  }

}
