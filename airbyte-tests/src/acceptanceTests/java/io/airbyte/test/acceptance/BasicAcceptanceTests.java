/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.acceptance;

import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.AWESOME_PEOPLE_TABLE_NAME;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.COLUMN_ID;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.COLUMN_NAME;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.COOL_EMPLOYEES_TABLE_NAME;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.PUBLIC_SCHEMA_NAME;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.STAGING_SCHEMA_NAME;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.STREAM_NAME;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.waitForSuccessfulJob;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.waitWhileJobHasStatus;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.waitWhileJobIsRunning;
import static java.lang.Thread.sleep;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.generated.WebBackendApi;
import io.airbyte.api.client.invoker.generated.ApiClient;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.AirbyteCatalog;
import io.airbyte.api.client.model.generated.AirbyteStream;
import io.airbyte.api.client.model.generated.AirbyteStreamAndConfiguration;
import io.airbyte.api.client.model.generated.AirbyteStreamConfiguration;
import io.airbyte.api.client.model.generated.AttemptInfoRead;
import io.airbyte.api.client.model.generated.AttemptStatus;
import io.airbyte.api.client.model.generated.CheckConnectionRead;
import io.airbyte.api.client.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.client.model.generated.ConnectionRead;
import io.airbyte.api.client.model.generated.ConnectionScheduleData;
import io.airbyte.api.client.model.generated.ConnectionScheduleDataBasicSchedule;
import io.airbyte.api.client.model.generated.ConnectionScheduleDataBasicSchedule.TimeUnitEnum;
import io.airbyte.api.client.model.generated.ConnectionScheduleDataCron;
import io.airbyte.api.client.model.generated.ConnectionScheduleType;
import io.airbyte.api.client.model.generated.ConnectionState;
import io.airbyte.api.client.model.generated.ConnectionStatus;
import io.airbyte.api.client.model.generated.DataType;
import io.airbyte.api.client.model.generated.DestinationDefinitionIdRequestBody;
import io.airbyte.api.client.model.generated.DestinationDefinitionIdWithWorkspaceId;
import io.airbyte.api.client.model.generated.DestinationDefinitionRead;
import io.airbyte.api.client.model.generated.DestinationDefinitionSpecificationRead;
import io.airbyte.api.client.model.generated.DestinationIdRequestBody;
import io.airbyte.api.client.model.generated.DestinationRead;
import io.airbyte.api.client.model.generated.DestinationSyncMode;
import io.airbyte.api.client.model.generated.JobConfigType;
import io.airbyte.api.client.model.generated.JobIdRequestBody;
import io.airbyte.api.client.model.generated.JobInfoRead;
import io.airbyte.api.client.model.generated.JobListRequestBody;
import io.airbyte.api.client.model.generated.JobRead;
import io.airbyte.api.client.model.generated.JobStatus;
import io.airbyte.api.client.model.generated.JobWithAttemptsRead;
import io.airbyte.api.client.model.generated.OperationCreate;
import io.airbyte.api.client.model.generated.OperationRead;
import io.airbyte.api.client.model.generated.OperatorConfiguration;
import io.airbyte.api.client.model.generated.OperatorType;
import io.airbyte.api.client.model.generated.OperatorWebhook;
import io.airbyte.api.client.model.generated.OperatorWebhook.WebhookTypeEnum;
import io.airbyte.api.client.model.generated.OperatorWebhookDbtCloud;
import io.airbyte.api.client.model.generated.SelectedFieldInfo;
import io.airbyte.api.client.model.generated.SourceDefinitionIdRequestBody;
import io.airbyte.api.client.model.generated.SourceDefinitionIdWithWorkspaceId;
import io.airbyte.api.client.model.generated.SourceDefinitionRead;
import io.airbyte.api.client.model.generated.SourceDefinitionSpecificationRead;
import io.airbyte.api.client.model.generated.SourceIdRequestBody;
import io.airbyte.api.client.model.generated.SourceRead;
import io.airbyte.api.client.model.generated.StreamDescriptor;
import io.airbyte.api.client.model.generated.StreamState;
import io.airbyte.api.client.model.generated.SyncMode;
import io.airbyte.api.client.model.generated.WebBackendConnectionUpdate;
import io.airbyte.api.client.model.generated.WebhookConfigWrite;
import io.airbyte.api.client.model.generated.WorkspaceRead;
import io.airbyte.api.client.model.generated.WorkspaceUpdate;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.temporal.scheduling.state.WorkflowState;
import io.airbyte.db.Database;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.test.utils.AirbyteAcceptanceTestHarness;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import io.airbyte.test.utils.SchemaTableNamePair;
import java.io.IOException;
import java.net.URISyntaxException;
import java.sql.SQLException;
import java.time.Duration;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;
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
@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class BasicAcceptanceTests {

  private static final Logger LOGGER = LoggerFactory.getLogger(BasicAcceptanceTests.class);

  private static final Boolean WITH_SCD_TABLE = true;

  private static final Boolean WITHOUT_SCD_TABLE = false;

  private static AirbyteAcceptanceTestHarness testHarness;
  private static AirbyteApiClient apiClient;
  private static WebBackendApi webBackendApi;
  private static UUID workspaceId;
  private static PostgreSQLContainer sourcePsql;

  private static final String TYPE = "type";
  private static final String REF = "$ref";
  private static final String INTEGER_REFERENCE = "WellKnownTypes.json#/definitions/Integer";
  private static final String STRING_REFERENCE = "WellKnownTypes.json#/definitions/String";
  private static final String PUBLIC = "public";
  private static final String E2E_TEST_SOURCE = "E2E Test Source -";
  private static final String INFINITE_FEED = "INFINITE_FEED";
  private static final String MESSAGE_INTERVAL = "message_interval";
  private static final String MAX_RECORDS = "max_records";
  private static final String TEST_CONNECTION = "test-connection";
  private static final String STATE_AFTER_SYNC_ONE = "state after sync 1: {}";
  private static final String STATE_AFTER_SYNC_TWO = "state after sync 2: {}";
  private static final String GERALT = "geralt";
  private static final String NAME = "name";
  private static final String VALUE = "value";
  private static final String LOCATION = "location";
  private static final String FIELD = "field";
  private static final String ID_AND_NAME = "id_and_name";

  private static final int MAX_SCHEDULED_JOB_RETRIES = 10;

  private static final ConnectionScheduleData BASIC_SCHEDULE_DATA = new ConnectionScheduleData().basicSchedule(
      new ConnectionScheduleDataBasicSchedule().units(1L).timeUnit(TimeUnitEnum.HOURS));

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

    testHarness = new AirbyteAcceptanceTestHarness(apiClient, workspaceId);
    sourcePsql = testHarness.getSourcePsql();
  }

  @AfterAll
  static void end() {
    testHarness.stopDbAndContainers();
  }

  @BeforeEach
  void setup() throws SQLException, URISyntaxException, IOException {
    testHarness.setup();
  }

  @AfterEach
  void tearDown() {
    testHarness.cleanup();
  }

  @Test
  @Order(-2)
  void testGetDestinationSpec() throws ApiException {
    final UUID destinationDefinitionId = testHarness.getPostgresDestinationDefinitionId();
    final DestinationDefinitionSpecificationRead spec = apiClient.getDestinationDefinitionSpecificationApi()
        .getDestinationDefinitionSpecification(
            new DestinationDefinitionIdWithWorkspaceId().destinationDefinitionId(destinationDefinitionId).workspaceId(UUID.randomUUID()));
    assertEquals(destinationDefinitionId, spec.getDestinationDefinitionId());
    assertNotNull(spec.getConnectionSpecification());
  }

  @Test
  @Order(-1)
  void testFailedGet404() {
    final var e = assertThrows(ApiException.class, () -> apiClient.getDestinationDefinitionSpecificationApi()
        .getDestinationDefinitionSpecification(
            new DestinationDefinitionIdWithWorkspaceId().destinationDefinitionId(UUID.randomUUID()).workspaceId(UUID.randomUUID())));
    assertEquals(404, e.getCode());
  }

  @Test
  @Order(0)
  void testGetSourceSpec() throws ApiException {
    final UUID sourceDefId = testHarness.getPostgresSourceDefinitionId();
    final SourceDefinitionSpecificationRead spec = apiClient.getSourceDefinitionSpecificationApi()
        .getSourceDefinitionSpecification(new SourceDefinitionIdWithWorkspaceId().sourceDefinitionId(sourceDefId).workspaceId(UUID.randomUUID()));
    assertEquals(sourceDefId, spec.getSourceDefinitionId());
    assertNotNull(spec.getConnectionSpecification());
  }

  @Test
  @Order(1)
  void testCreateDestination() throws ApiException {
    final UUID destinationDefId = testHarness.getPostgresDestinationDefinitionId();
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
  void testDestinationCheckConnection() throws ApiException {
    final UUID destinationId = testHarness.createPostgresDestination().getDestinationId();

    final CheckConnectionRead.StatusEnum checkOperationStatus = apiClient.getDestinationApi()
        .checkConnectionToDestination(new DestinationIdRequestBody().destinationId(destinationId))
        .getStatus();

    assertEquals(CheckConnectionRead.StatusEnum.SUCCEEDED, checkOperationStatus);
  }

  @Test
  @Order(3)
  void wtestCreateSource() throws ApiException {
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
    ((ObjectNode) expectedConfig).put(JdbcUtils.PASSWORD_KEY, "**********");
    assertEquals(dbName, response.getName());
    assertEquals(workspaceId, response.getWorkspaceId());
    assertEquals(postgresSourceDefinitionId, response.getSourceDefinitionId());
    assertEquals(expectedConfig, response.getConnectionConfiguration());
  }

  @Test
  @Order(4)
  void testSourceCheckConnection() throws ApiException {
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();

    final CheckConnectionRead checkConnectionRead = apiClient.getSourceApi().checkConnectionToSource(new SourceIdRequestBody().sourceId(sourceId));

    assertEquals(
        CheckConnectionRead.StatusEnum.SUCCEEDED,
        checkConnectionRead.getStatus(),
        checkConnectionRead.getMessage());
  }

  @Test
  @Order(5)
  void testDiscoverSourceSchema() throws ApiException {
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();

    final AirbyteCatalog actual = testHarness.discoverSourceSchema(sourceId);

    final Map<String, Map<String, String>> fields = ImmutableMap.of(
        COLUMN_ID, ImmutableMap.of(TYPE, DataType.NUMBER.getValue(), "airbyte_type", "integer"),
        COLUMN_NAME, ImmutableMap.of(TYPE, DataType.STRING.getValue()));
    final JsonNode jsonSchema = Jsons.jsonNode(ImmutableMap.builder()
        .put(TYPE, "object")
        .put("properties", fields)
        .build());
    final AirbyteStream stream = new AirbyteStream()
        .name(STREAM_NAME)
        .namespace(PUBLIC)
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
        .selected(true)
        .suggested(true);
    final AirbyteCatalog expected = new AirbyteCatalog()
        .streams(Lists.newArrayList(new AirbyteStreamAndConfiguration()
            .stream(stream)
            .config(streamConfig)));

    assertEquals(expected, actual);
  }

  @Test
  @Order(6)
  void testCreateConnection() throws ApiException {
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    final UUID destinationId = testHarness.createPostgresDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final String name = "test-connection-" + UUID.randomUUID();
    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode).setFieldSelectionEnabled(false));
    final ConnectionRead createdConnection =
        testHarness.createConnection(name, sourceId, destinationId, List.of(operationId), catalog, ConnectionScheduleType.BASIC, BASIC_SCHEDULE_DATA);
    createdConnection.getSyncCatalog().getStreams().forEach(s -> s.getConfig().setSuggested(true));

    assertEquals(sourceId, createdConnection.getSourceId());
    assertEquals(destinationId, createdConnection.getDestinationId());
    assertEquals(1, createdConnection.getOperationIds().size());
    assertEquals(operationId, createdConnection.getOperationIds().get(0));
    assertEquals(catalog, createdConnection.getSyncCatalog());
    assertEquals(ConnectionScheduleType.BASIC, createdConnection.getScheduleType());
    assertEquals(BASIC_SCHEDULE_DATA, createdConnection.getScheduleData());
    assertEquals(name, createdConnection.getName());
  }

  @Test
  @Order(7)
  void testCancelSync() throws Exception {
    final SourceDefinitionRead sourceDefinition = testHarness.createE2eSourceDefinition(workspaceId);

    final SourceRead source = testHarness.createSource(
        E2E_TEST_SOURCE + UUID.randomUUID(),
        workspaceId,
        sourceDefinition.getSourceDefinitionId(),
        Jsons.jsonNode(ImmutableMap.builder()
            .put(TYPE, INFINITE_FEED)
            .put(MESSAGE_INTERVAL, 1000)
            .put(MAX_RECORDS, Duration.ofMinutes(5).toSeconds())
            .build()));

    final UUID sourceId = source.getSourceId();
    final UUID destinationId = testHarness.createPostgresDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));
    final UUID connectionId =
        testHarness.createConnection(TEST_CONNECTION, sourceId, destinationId, List.of(operationId), catalog, ConnectionScheduleType.MANUAL, null)
            .getConnectionId();
    final JobInfoRead connectionSyncRead = apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));

    // wait to get out of PENDING
    final JobRead jobRead = waitWhileJobHasStatus(apiClient.getJobsApi(), connectionSyncRead.getJob(), Set.of(JobStatus.PENDING));
    assertEquals(JobStatus.RUNNING, jobRead.getStatus());

    final var resp = apiClient.getJobsApi().cancelJob(new JobIdRequestBody().id(connectionSyncRead.getJob().getId()));
    assertEquals(JobStatus.CANCELLED, resp.getJob().getStatus());
  }

  @Test
  @Order(8)
  void testScheduledSync() throws Exception {
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createPostgresDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);

    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));

    final UUID connectionId =
        testHarness.createConnection(TEST_CONNECTION, sourceId, destinationId, List.of(operationId), catalog, ConnectionScheduleType.BASIC,
            BASIC_SCHEDULE_DATA).getConnectionId();

    waitForSuccessfulJobWithRetries(connectionId, MAX_SCHEDULED_JOB_RETRIES);

    testHarness.assertSourceAndDestinationDbInSync(WITHOUT_SCD_TABLE);
  }

  @Test
  @Order(9)
  void testCronSync() throws Exception {
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createPostgresDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);

    // NOTE: this cron should run once every two minutes.
    final ConnectionScheduleData connectionScheduleData = new ConnectionScheduleData().cron(
        new ConnectionScheduleDataCron().cronExpression("* */2 * * * ?").cronTimeZone("UTC"));
    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));

    final UUID connectionId =
        testHarness.createConnection(TEST_CONNECTION, sourceId, destinationId, List.of(operationId), catalog, ConnectionScheduleType.CRON,
            connectionScheduleData).getConnectionId();

    waitForSuccessfulJobWithRetries(connectionId, MAX_SCHEDULED_JOB_RETRIES);

    testHarness.assertSourceAndDestinationDbInSync(WITHOUT_SCD_TABLE);
    apiClient.getConnectionApi().deleteConnection(new ConnectionIdRequestBody().connectionId(connectionId));

    // remove connection to avoid exception during tear down
    testHarness.removeConnection(connectionId);
  }

  @Test
  @Order(19)
  void testWebhookOperationExecutesSuccessfully() throws Exception {
    // create workspace webhook config
    final WorkspaceRead workspaceRead = apiClient.getWorkspaceApi().updateWorkspace(
        new WorkspaceUpdate().workspaceId(workspaceId).addWebhookConfigsItem(
            new WebhookConfigWrite().name("reqres test")));
    // create a webhook operation
    final OperationRead operationRead = apiClient.getOperationApi().createOperation(new OperationCreate()
        .workspaceId(workspaceId)
        .name("reqres test")
        .operatorConfiguration(new OperatorConfiguration()
            .operatorType(OperatorType.WEBHOOK)
            .webhook(new OperatorWebhook()
                .webhookConfigId(workspaceRead.getWebhookConfigs().get(0).getId())
                // NOTE: this dbt Cloud config won't actually work, but the sync should still succeed.
                .webhookType(WebhookTypeEnum.DBTCLOUD)
                .dbtCloud(new OperatorWebhookDbtCloud().accountId(123).jobId(456)))));
    // create a connection with the new operation.
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createPostgresDestination().getDestinationId();
    // NOTE: this is a normalization operation.
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));
    final UUID connectionId =
        testHarness.createConnection(
            TEST_CONNECTION, sourceId, destinationId, List.of(operationId, operationRead.getOperationId()), catalog, ConnectionScheduleType.MANUAL,
            null)
            .getConnectionId();
    // run the sync
    apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJobWithRetries(connectionId, MAX_SCHEDULED_JOB_RETRIES);
    testHarness.assertSourceAndDestinationDbInSync(WITHOUT_SCD_TABLE);
    apiClient.getConnectionApi().deleteConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    // remove connection to avoid exception during tear down
    testHarness.removeConnection(connectionId);
    // TODO(mfsiega-airbyte): add webhook info to the jobs api to verify the webhook execution status.
  }

  @Test
  @Order(10)
  void testMultipleSchemasAndTablesSync() throws Exception {
    // create tables in another schema
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forClasspathResource("postgres_second_schema_multiple_tables.sql"), sourcePsql);

    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createPostgresDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);

    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));
    final UUID connectionId =
        testHarness.createConnection(TEST_CONNECTION, sourceId, destinationId, List.of(operationId), catalog, ConnectionScheduleType.MANUAL, null)
            .getConnectionId();
    final JobInfoRead connectionSyncRead = apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead.getJob());
    testHarness.assertSourceAndDestinationDbInSync(false);
  }

  @Test
  @Order(11)
  void testMultipleSchemasSameTablesSync() throws Exception {
    // create tables in another schema
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forClasspathResource("postgres_separate_schema_same_table.sql"), sourcePsql);

    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createPostgresDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);

    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));
    final UUID connectionId =
        testHarness.createConnection(TEST_CONNECTION, sourceId, destinationId, List.of(operationId), catalog, ConnectionScheduleType.MANUAL, null)
            .getConnectionId();

    final JobInfoRead connectionSyncRead = apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead.getJob());
    testHarness.assertSourceAndDestinationDbInSync(WITHOUT_SCD_TABLE);
  }

  @Test
  @Order(12)
  void testIncrementalDedupeSync() throws Exception {
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createPostgresDestination().getDestinationId();
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
        testHarness.createConnection(TEST_CONNECTION, sourceId, destinationId, List.of(operationId), catalog, ConnectionScheduleType.MANUAL, null)
            .getConnectionId();

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

    testHarness.assertRawDestinationContains(expectedRawRecords, new SchemaTableNamePair(PUBLIC, STREAM_NAME));
    testHarness.assertNormalizedDestinationContains(expectedNormalizedRecords);
  }

  @Test
  @Order(13)
  void testIncrementalSync() throws Exception {
    LOGGER.info("Starting testIncrementalSync()");
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createPostgresDestination().getDestinationId();
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
        testHarness.createConnection(TEST_CONNECTION, sourceId, destinationId, List.of(operationId), catalog, ConnectionScheduleType.MANUAL, null)
            .getConnectionId();
    LOGGER.info("Beginning testIncrementalSync() sync 1");

    final JobInfoRead connectionSyncRead1 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead1.getJob());
    LOGGER.info(STATE_AFTER_SYNC_ONE, apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    testHarness.assertSourceAndDestinationDbInSync(WITHOUT_SCD_TABLE);

    // add new records and run again.
    final Database source = testHarness.getSourceDatabase();
    // get contents of source before mutating records.
    final List<JsonNode> expectedRecords = testHarness.retrieveSourceRecords(source, STREAM_NAME);
    expectedRecords.add(Jsons.jsonNode(ImmutableMap.builder().put(COLUMN_ID, 6).put(COLUMN_NAME, GERALT).build()));
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
    LOGGER.info(STATE_AFTER_SYNC_TWO, apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    testHarness.assertRawDestinationContains(expectedRecords, new SchemaTableNamePair(PUBLIC, STREAM_NAME));

    // reset back to no data.

    LOGGER.info("Starting testIncrementalSync() reset");
    final JobInfoRead jobInfoRead = apiClient.getConnectionApi().resetConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitWhileJobHasStatus(apiClient.getJobsApi(), jobInfoRead.getJob(),
        Sets.newHashSet(JobStatus.PENDING, JobStatus.RUNNING, JobStatus.INCOMPLETE, JobStatus.FAILED));
    // This is a band-aid to prevent some race conditions where the job status was updated but we may
    // still be cleaning up some data in the reset table. This would be an argument for reworking the
    // source of truth of the replication workflow state to be in DB rather than in Memory and
    // serialized automagically by temporal
    waitWhileJobIsRunning(apiClient.getJobsApi(), jobInfoRead.getJob(), Duration.ofMinutes(1));

    LOGGER.info("state after reset: {}", apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    testHarness.assertRawDestinationContains(Collections.emptyList(), new SchemaTableNamePair(PUBLIC,
        STREAM_NAME));

    // sync one more time. verify it is the equivalent of a full refresh.
    LOGGER.info("Starting testIncrementalSync() sync 3");
    final JobInfoRead connectionSyncRead3 =
        apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead3.getJob());
    LOGGER.info("state after sync 3: {}", apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    testHarness.assertSourceAndDestinationDbInSync(WITHOUT_SCD_TABLE);

  }

  @Test
  @Order(14)
  void testDeleteConnection() throws Exception {
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createPostgresDestination().getDestinationId();
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
        testHarness.createConnection(TEST_CONNECTION, sourceId, destinationId, List.of(operationId), catalog, ConnectionScheduleType.MANUAL, null)
            .getConnectionId();

    final JobInfoRead connectionSyncRead = apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitWhileJobHasStatus(apiClient.getJobsApi(), connectionSyncRead.getJob(), Set.of(JobStatus.RUNNING));

    // test normal deletion of connection
    LOGGER.info("Calling delete connection...");
    apiClient.getConnectionApi().deleteConnection(new ConnectionIdRequestBody().connectionId(connectionId));

    // remove connection to avoid exception during tear down
    // connectionIds.remove(connectionId); // todo remove
    testHarness.removeConnection(connectionId);

    ConnectionStatus connectionStatus =
        apiClient.getConnectionApi().getConnection(new ConnectionIdRequestBody().connectionId(connectionId)).getStatus();
    assertEquals(ConnectionStatus.DEPRECATED, connectionStatus);

    // test that repeated deletion call for same connection is successful
    LOGGER.info("Calling delete connection a second time to test repeat call behavior...");
    apiClient.getConnectionApi().deleteConnection(new ConnectionIdRequestBody().connectionId(connectionId));

    // test deletion of connection when temporal workflow is in a bad state
    LOGGER.info("Testing connection deletion when temporal is in a terminal state");
    connectionId =
        testHarness.createConnection(TEST_CONNECTION, sourceId, destinationId, List.of(operationId), catalog, ConnectionScheduleType.MANUAL, null)
            .getConnectionId();

    testHarness.terminateTemporalWorkflow(connectionId);

    // we should still be able to delete the connection when the temporal workflow is in this state
    apiClient.getConnectionApi().deleteConnection(new ConnectionIdRequestBody().connectionId(connectionId));

    connectionStatus = apiClient.getConnectionApi().getConnection(new ConnectionIdRequestBody().connectionId(connectionId)).getStatus();
    assertEquals(ConnectionStatus.DEPRECATED, connectionStatus);
  }

  @Test
  @Order(15)
  void testUpdateConnectionWhenWorkflowUnreachable() throws Exception {
    // This test only covers the specific behavior of updating a connection that does not have an
    // underlying temporal workflow.
    // Also, this test doesn't verify correctness of the schedule update applied, as adding the ability
    // to query a workflow for its current
    // schedule is out of scope for the issue (https://github.com/airbytehq/airbyte/issues/11215). This
    // test just ensures that the underlying workflow
    // is running after the update method is called.
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createPostgresDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    catalog.getStreams().forEach(s -> s.getConfig()
        .syncMode(SyncMode.INCREMENTAL)
        .cursorField(List.of(COLUMN_ID))
        .destinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
        .primaryKey(List.of(List.of(COLUMN_NAME))));

    LOGGER.info("Testing connection update when temporal is in a terminal state");
    final UUID connectionId =
        testHarness.createConnection(TEST_CONNECTION, sourceId, destinationId, List.of(operationId), catalog, ConnectionScheduleType.MANUAL, null)
            .getConnectionId();

    testHarness.terminateTemporalWorkflow(connectionId);

    // we should still be able to update the connection when the temporal workflow is in this state
    testHarness.updateConnectionSchedule(
        connectionId,
        ConnectionScheduleType.BASIC,
        new ConnectionScheduleData().basicSchedule(new ConnectionScheduleDataBasicSchedule().timeUnit(TimeUnitEnum.HOURS).units(1L)));

    LOGGER.info("Waiting for workflow to be recreated...");
    Thread.sleep(500);

    final WorkflowState workflowState = testHarness.getWorkflowState(connectionId);
    assertTrue(workflowState.isRunning());
  }

  @Test
  @Order(16)
  void testManualSyncRepairsWorkflowWhenWorkflowUnreachable() throws Exception {
    // This test only covers the specific behavior of updating a connection that does not have an
    // underlying temporal workflow.
    final SourceDefinitionRead sourceDefinition = testHarness.createE2eSourceDefinition(workspaceId);
    final SourceRead source = testHarness.createSource(
        E2E_TEST_SOURCE + UUID.randomUUID(),
        workspaceId,
        sourceDefinition.getSourceDefinitionId(),
        Jsons.jsonNode(ImmutableMap.builder()
            .put(TYPE, INFINITE_FEED)
            .put(MAX_RECORDS, 5000)
            .put(MESSAGE_INTERVAL, 100)
            .build()));
    final UUID sourceId = source.getSourceId();
    final UUID destinationId = testHarness.createPostgresDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    catalog.getStreams().forEach(s -> s.getConfig()
        .syncMode(SyncMode.INCREMENTAL)
        .cursorField(List.of(COLUMN_ID))
        .destinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
        .primaryKey(List.of(List.of(COLUMN_NAME))));

    LOGGER.info("Testing manual sync when temporal is in a terminal state");
    final UUID connectionId =
        testHarness.createConnection(TEST_CONNECTION, sourceId, destinationId, List.of(operationId), catalog, ConnectionScheduleType.MANUAL, null)
            .getConnectionId();

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
  @Order(17)
  void testResetConnectionRepairsWorkflowWhenWorkflowUnreachable() throws Exception {
    // This test only covers the specific behavior of updating a connection that does not have an
    // underlying temporal workflow.
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createPostgresDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    catalog.getStreams().forEach(s -> s.getConfig()
        .syncMode(SyncMode.INCREMENTAL)
        .cursorField(List.of(COLUMN_ID))
        .destinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
        .primaryKey(List.of(List.of(COLUMN_NAME))));

    LOGGER.info("Testing reset connection when temporal is in a terminal state");
    final UUID connectionId =
        testHarness.createConnection(TEST_CONNECTION, sourceId, destinationId, List.of(operationId), catalog, ConnectionScheduleType.MANUAL, null)
            .getConnectionId();

    testHarness.terminateTemporalWorkflow(connectionId);

    final JobInfoRead jobInfoRead = apiClient.getConnectionApi().resetConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    assertEquals(JobConfigType.RESET_CONNECTION, jobInfoRead.getJob().getConfigType());
  }

  @Test
  @Order(18)
  void testResetCancelsRunningSync() throws Exception {
    final SourceDefinitionRead sourceDefinition = testHarness.createE2eSourceDefinition(workspaceId);

    final SourceRead source = testHarness.createSource(
        E2E_TEST_SOURCE + UUID.randomUUID(),
        workspaceId,
        sourceDefinition.getSourceDefinitionId(),
        Jsons.jsonNode(ImmutableMap.builder()
            .put(TYPE, INFINITE_FEED)
            .put(MESSAGE_INTERVAL, 1000)
            .put(MAX_RECORDS, Duration.ofMinutes(5).toSeconds())
            .build()));

    final UUID sourceId = source.getSourceId();
    final UUID destinationId = testHarness.createPostgresDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));
    final UUID connectionId =
        testHarness.createConnection(TEST_CONNECTION, sourceId, destinationId, List.of(operationId), catalog, ConnectionScheduleType.MANUAL, null)
            .getConnectionId();
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
  void testSyncAfterUpgradeToPerStreamState(final TestInfo testInfo) throws Exception {
    LOGGER.info("Starting {}", testInfo.getDisplayName());
    final SourceRead source = testHarness.createPostgresSource(true);
    final UUID sourceId = source.getSourceId();
    final UUID sourceDefinitionId = source.getSourceDefinitionId();
    final UUID destinationId = testHarness.createPostgresDestination(true).getDestinationId();
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
        testHarness.createConnection(TEST_CONNECTION, sourceId, destinationId, List.of(operationId), catalog, ConnectionScheduleType.MANUAL, null)
            .getConnectionId();
    LOGGER.info("Beginning {} sync 1", testInfo.getDisplayName());

    final JobInfoRead connectionSyncRead1 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead1.getJob());
    LOGGER.info(STATE_AFTER_SYNC_ONE, apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    testHarness.assertSourceAndDestinationDbInSync(WITHOUT_SCD_TABLE);

    // Set source to a version that supports per-stream state
    testHarness.updateSourceDefinitionVersion(sourceDefinitionId, currentSourceDefintionVersion);
    LOGGER.info("Upgraded source connector per-stream state supported version {}.", currentSourceDefintionVersion);

    // add new records and run again.
    final Database sourceDatabase = testHarness.getSourceDatabase();
    // get contents of source before mutating records.
    final List<JsonNode> expectedRecords = testHarness.retrieveSourceRecords(sourceDatabase, STREAM_NAME);
    expectedRecords.add(Jsons.jsonNode(ImmutableMap.builder().put(COLUMN_ID, 6).put(COLUMN_NAME, GERALT).build()));
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
    LOGGER.info(STATE_AFTER_SYNC_TWO, apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    testHarness.assertRawDestinationContains(expectedRecords, new SchemaTableNamePair(PUBLIC, STREAM_NAME));

    // reset back to no data.
    LOGGER.info("Starting {} reset", testInfo.getDisplayName());
    final JobInfoRead jobInfoRead = apiClient.getConnectionApi().resetConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitWhileJobHasStatus(apiClient.getJobsApi(), jobInfoRead.getJob(),
        Sets.newHashSet(JobStatus.PENDING, JobStatus.RUNNING, JobStatus.INCOMPLETE, JobStatus.FAILED));
    // This is a band-aid to prevent some race conditions where the job status was updated but we may
    // still be cleaning up some data in the reset table. This would be an argument for reworking the
    // source of truth of the replication workflow state to be in DB rather than in Memory and
    // serialized automagically by temporal
    waitWhileJobIsRunning(apiClient.getJobsApi(), jobInfoRead.getJob(), Duration.ofMinutes(1));

    LOGGER.info("state after reset: {}", apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    testHarness.assertRawDestinationContains(Collections.emptyList(), new SchemaTableNamePair(PUBLIC,
        STREAM_NAME));

    // sync one more time. verify it is the equivalent of a full refresh.
    final String expectedState =
        "{\"cursor\":\"6\",\"stream_name\":\"id_and_name\",\"cursor_field\":[\"id\"],\"stream_namespace\":\"public\",\"cursor_record_count\":1}";
    LOGGER.info("Starting {} sync 3", testInfo.getDisplayName());
    final JobInfoRead connectionSyncRead3 =
        apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead3.getJob());
    final ConnectionState state = apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId));
    LOGGER.info("state after sync 3: {}", state);

    testHarness.assertSourceAndDestinationDbInSync(WITHOUT_SCD_TABLE);
    assertNotNull(state.getStreamState());
    assertEquals(1, state.getStreamState().size());
    final StreamState idAndNameState = state.getStreamState().get(0);
    assertEquals(new StreamDescriptor().namespace(PUBLIC).name(STREAM_NAME), idAndNameState.getStreamDescriptor());
    assertEquals(Jsons.deserialize(expectedState), idAndNameState.getStreamState());
  }

  @Test
  void testSyncAfterUpgradeToPerStreamStateWithNoNewData(final TestInfo testInfo) throws Exception {
    LOGGER.info("Starting {}", testInfo.getDisplayName());
    final SourceRead source = testHarness.createPostgresSource(true);
    final UUID sourceId = source.getSourceId();
    final UUID sourceDefinitionId = source.getSourceDefinitionId();
    final UUID destinationId = testHarness.createPostgresDestination(true).getDestinationId();
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
        testHarness.createConnection(TEST_CONNECTION, sourceId, destinationId, List.of(operationId), catalog, ConnectionScheduleType.MANUAL, null)
            .getConnectionId();
    LOGGER.info("Beginning {} sync 1", testInfo.getDisplayName());

    final JobInfoRead connectionSyncRead1 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead1.getJob());
    LOGGER.info(STATE_AFTER_SYNC_ONE, apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    testHarness.assertSourceAndDestinationDbInSync(WITHOUT_SCD_TABLE);

    // Set source to a version that supports per-stream state
    testHarness.updateSourceDefinitionVersion(sourceDefinitionId, currentSourceDefintionVersion);
    LOGGER.info("Upgraded source connector per-stream state supported version {}.", currentSourceDefintionVersion);

    // sync one more time. verify that nothing has been synced
    LOGGER.info("Starting {} sync 2", testInfo.getDisplayName());
    final JobInfoRead connectionSyncRead2 =
        apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead2.getJob());
    LOGGER.info(STATE_AFTER_SYNC_TWO, apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    final JobInfoRead syncJob = apiClient.getJobsApi().getJobInfo(new JobIdRequestBody().id(connectionSyncRead2.getJob().getId()));
    final Optional<AttemptInfoRead> result = syncJob.getAttempts().stream()
        .sorted((a, b) -> Long.compare(b.getAttempt().getEndedAt(), a.getAttempt().getEndedAt()))
        .findFirst();

    assertTrue(result.isPresent());
    assertEquals(0, result.get().getAttempt().getRecordsSynced());
    assertEquals(0, result.get().getAttempt().getTotalStats().getRecordsEmitted());
    testHarness.assertSourceAndDestinationDbInSync(WITHOUT_SCD_TABLE);
  }

  @Test
  void testResetAllWhenSchemaIsModifiedForLegacySource() throws Exception {
    final String sourceTable1 = "test_table1";
    final String sourceTable2 = "test_table2";
    final String sourceTable3 = "test_table3";
    final String outputPrefix = "output_namespace_public.output_table_";
    final Database sourceDb = testHarness.getSourceDatabase();
    final Database destDb = testHarness.getDestinationDatabase();
    sourceDb.query(ctx -> {
      ctx.createTableIfNotExists(sourceTable1).columns(DSL.field(NAME, SQLDataType.VARCHAR)).execute();
      ctx.truncate(sourceTable1).execute();
      ctx.insertInto(DSL.table(sourceTable1)).columns(DSL.field(NAME)).values("john").execute();
      ctx.insertInto(DSL.table(sourceTable1)).columns(DSL.field(NAME)).values("bob").execute();

      ctx.createTableIfNotExists(sourceTable2).columns(DSL.field(VALUE, SQLDataType.VARCHAR)).execute();
      ctx.truncate(sourceTable2).execute();
      ctx.insertInto(DSL.table(sourceTable2)).columns(DSL.field(VALUE)).values("v1").execute();
      ctx.insertInto(DSL.table(sourceTable2)).columns(DSL.field(VALUE)).values("v2").execute();
      return null;
    });

    final SourceRead source = testHarness.createPostgresSource(true);
    final UUID sourceId = source.getSourceId();
    final UUID sourceDefinitionId = source.getSourceDefinitionId();

    // Fetch the current/most recent source definition version
    final SourceDefinitionRead sourceDefinitionRead =
        apiClient.getSourceDefinitionApi().getSourceDefinition(new SourceDefinitionIdRequestBody().sourceDefinitionId(sourceDefinitionId));
    final String currentSourceDefinitionVersion = sourceDefinitionRead.getDockerImageTag();

    try {
      // Set the source to a version that does not support per-stream state
      LOGGER.info("Setting source connector to pre-per-stream state version {}...",
          AirbyteAcceptanceTestHarness.POSTGRES_SOURCE_LEGACY_CONNECTOR_VERSION);
      testHarness.updateSourceDefinitionVersion(sourceDefinitionId, AirbyteAcceptanceTestHarness.POSTGRES_SOURCE_LEGACY_CONNECTOR_VERSION);

      final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
      final UUID destinationId = testHarness.createPostgresDestination(true).getDestinationId();
      final OperationRead operation = testHarness.createOperation();
      final String name = "test_reset_when_schema_is_modified_" + UUID.randomUUID();

      LOGGER.info("Discovered catalog: {}", catalog);

      final ConnectionRead connection =
          testHarness.createConnection(name, sourceId, destinationId, List.of(operation.getOperationId()), catalog, ConnectionScheduleType.MANUAL,
              null);
      LOGGER.info("Created Connection: {}", connection);

      sourceDb.query(ctx -> {
        prettyPrintTables(ctx, sourceTable1, sourceTable2);
        return null;
      });

      // Run initial sync
      LOGGER.info("Running initial sync");
      final JobInfoRead syncRead =
          apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connection.getConnectionId()));
      waitForSuccessfulJob(apiClient.getJobsApi(), syncRead.getJob());

      // Some inspection for debug
      destDb.query(ctx -> {
        prettyPrintTables(ctx, outputPrefix + sourceTable1, outputPrefix + sourceTable2);
        return null;
      });
      final ConnectionState initSyncState =
          apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connection.getConnectionId()));
      LOGGER.info("ConnectionState after the initial sync: " + initSyncState.toString());

      testHarness.assertSourceAndDestinationDbInSync(false);

      // Patch some data in the source
      LOGGER.info("Modifying source tables");
      sourceDb.query(ctx -> {
        // Adding a new rows to make sure we sync more data.
        ctx.insertInto(DSL.table(sourceTable1)).columns(DSL.field(NAME)).values("alice").execute();
        ctx.insertInto(DSL.table(sourceTable2)).columns(DSL.field(VALUE)).values("v3").execute();

        // The removed rows should no longer be in the destination since we expect a full reset
        ctx.deleteFrom(DSL.table(sourceTable1)).where(DSL.field(NAME).eq("john")).execute();
        ctx.deleteFrom(DSL.table(sourceTable2)).where(DSL.field(VALUE).eq("v2")).execute();

        // Adding a new table to trigger reset from the update connection API
        ctx.createTableIfNotExists(sourceTable3).columns(DSL.field(LOCATION, SQLDataType.VARCHAR)).execute();
        ctx.truncate(sourceTable3).execute();
        ctx.insertInto(DSL.table(sourceTable3)).columns(DSL.field(LOCATION)).values("home").execute();
        ctx.insertInto(DSL.table(sourceTable3)).columns(DSL.field(LOCATION)).values("work").execute();
        ctx.insertInto(DSL.table(sourceTable3)).columns(DSL.field(LOCATION)).values("space").execute();
        return null;
      });

      final AirbyteCatalog updatedCatalog = testHarness.discoverSourceSchemaWithoutCache(sourceId);
      LOGGER.info("Discovered updated catalog: {}", updatedCatalog);

      // Update with refreshed catalog
      LOGGER.info("Submit the update request");
      final WebBackendConnectionUpdate update = new WebBackendConnectionUpdate()
          .connectionId(connection.getConnectionId())
          .syncCatalog(updatedCatalog);
      webBackendApi.webBackendUpdateConnection(update);

      LOGGER.info("Inspecting Destination DB after the update request, tables should be empty");
      destDb.query(ctx -> {
        prettyPrintTables(ctx, outputPrefix + sourceTable1, outputPrefix + sourceTable2);
        return null;
      });
      final ConnectionState postResetState =
          apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connection.getConnectionId()));
      LOGGER.info("ConnectionState after the update request: {}", postResetState.toString());

      // Wait until the sync from the UpdateConnection is finished
      final JobRead syncFromTheUpdate = testHarness.waitUntilTheNextJobIsStarted(connection.getConnectionId());
      LOGGER.info("Generated SyncJob config: {}", syncFromTheUpdate.toString());
      waitForSuccessfulJob(apiClient.getJobsApi(), syncFromTheUpdate);

      final ConnectionState postUpdateState =
          apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connection.getConnectionId()));
      LOGGER.info("ConnectionState after the final sync: {}", postUpdateState.toString());

      LOGGER.info("Inspecting DBs After the final sync");
      sourceDb.query(ctx -> {
        prettyPrintTables(ctx, sourceTable1, sourceTable2, sourceTable3);
        return null;
      });
      destDb.query(ctx -> {
        prettyPrintTables(ctx, outputPrefix + sourceTable1, outputPrefix + sourceTable2, outputPrefix + sourceTable3);
        return null;
      });

      testHarness.assertSourceAndDestinationDbInSync(false);
    } finally {
      // Set source back to version it was set to at beginning of test
      LOGGER.info("Set source connector back to per-stream state supported version {}.", currentSourceDefinitionVersion);
      testHarness.updateSourceDefinitionVersion(sourceDefinitionId, currentSourceDefinitionVersion);
    }
  }

  private void prettyPrintTables(final DSLContext ctx, final String... tables) {
    for (final String table : tables) {
      LOGGER.info("select * from {}", table);
      Arrays.stream(ctx.selectFrom(table)
          .fetch()
          .toString()
          .split("\\n")).forEach(LOGGER::info);
    }
  }

  @Test
  @Disabled
  void testIncrementalSyncMultipleStreams() throws Exception {
    LOGGER.info("Starting testIncrementalSyncMultipleStreams()");

    PostgreSQLContainerHelper.runSqlScript(MountableFile.forClasspathResource("postgres_second_schema_multiple_tables.sql"), sourcePsql);

    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createPostgresDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);

    for (final AirbyteStreamAndConfiguration streamAndConfig : catalog.getStreams()) {
      final AirbyteStream stream = streamAndConfig.getStream();
      assertEquals(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL), stream.getSupportedSyncModes());
      // instead of assertFalse to avoid NPE from unboxed.
      assertNull(stream.getSourceDefinedCursor());
      assertTrue(stream.getDefaultCursorField().isEmpty());
      assertTrue(stream.getSourceDefinedPrimaryKey().isEmpty());
    }

    final SyncMode syncMode = SyncMode.INCREMENTAL;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.APPEND;
    catalog.getStreams().forEach(s -> s.getConfig()
        .syncMode(syncMode)
        .cursorField(List.of(COLUMN_ID))
        .destinationSyncMode(destinationSyncMode));
    final UUID connectionId =
        testHarness.createConnection(TEST_CONNECTION, sourceId, destinationId, List.of(operationId), catalog, ConnectionScheduleType.MANUAL, null)
            .getConnectionId();
    LOGGER.info("Beginning testIncrementalSync() sync 1");

    final JobInfoRead connectionSyncRead1 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead1.getJob());
    LOGGER.info(STATE_AFTER_SYNC_ONE, apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    testHarness.assertSourceAndDestinationDbInSync(WITHOUT_SCD_TABLE);

    // add new records and run again.
    final Database source = testHarness.getSourceDatabase();
    // get contents of source before mutating records.
    final List<JsonNode> expectedRecordsIdAndName = testHarness.retrieveSourceRecords(source, STREAM_NAME);
    final List<JsonNode> expectedRecordsCoolEmployees =
        testHarness.retrieveSourceRecords(source, STAGING_SCHEMA_NAME + "." + COOL_EMPLOYEES_TABLE_NAME);
    final List<JsonNode> expectedRecordsAwesomePeople =
        testHarness.retrieveSourceRecords(source, STAGING_SCHEMA_NAME + "." + AWESOME_PEOPLE_TABLE_NAME);
    expectedRecordsIdAndName.add(Jsons.jsonNode(ImmutableMap.builder().put(COLUMN_ID, 6).put(COLUMN_NAME, GERALT).build()));
    expectedRecordsCoolEmployees.add(Jsons.jsonNode(ImmutableMap.builder().put(COLUMN_ID, 6).put(COLUMN_NAME, GERALT).build()));
    expectedRecordsAwesomePeople.add(Jsons.jsonNode(ImmutableMap.builder().put(COLUMN_ID, 3).put(COLUMN_NAME, GERALT).build()));
    // add a new record to each table
    source.query(ctx -> ctx.execute("INSERT INTO id_and_name(id, name) VALUES(6, 'geralt')"));
    source.query(ctx -> ctx.execute("INSERT INTO staging.cool_employees(id, name) VALUES(6, 'geralt')"));
    source.query(ctx -> ctx.execute("INSERT INTO staging.awesome_people(id, name) VALUES(3, 'geralt')"));
    // mutate a record that was already synced with out updating its cursor value. if we are actually
    // full refreshing, this record will appear in the output and cause the test to fail. if we are,
    // correctly, doing incremental, we will not find this value in the destination.
    source.query(ctx -> ctx.execute("UPDATE id_and_name SET name='yennefer' WHERE id=2"));
    source.query(ctx -> ctx.execute("UPDATE staging.cool_employees SET name='yennefer' WHERE id=2"));
    source.query(ctx -> ctx.execute("UPDATE staging.awesome_people SET name='yennefer' WHERE id=2"));

    LOGGER.info("Starting testIncrementalSync() sync 2");
    final JobInfoRead connectionSyncRead2 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead2.getJob());
    LOGGER.info(STATE_AFTER_SYNC_TWO, apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    testHarness.assertRawDestinationContains(expectedRecordsIdAndName, new SchemaTableNamePair(PUBLIC_SCHEMA_NAME, STREAM_NAME));
    testHarness.assertRawDestinationContains(expectedRecordsCoolEmployees, new SchemaTableNamePair(STAGING_SCHEMA_NAME, COOL_EMPLOYEES_TABLE_NAME));
    testHarness.assertRawDestinationContains(expectedRecordsAwesomePeople, new SchemaTableNamePair(STAGING_SCHEMA_NAME, AWESOME_PEOPLE_TABLE_NAME));

    // reset back to no data.

    LOGGER.info("Starting testIncrementalSync() reset");
    final JobInfoRead jobInfoRead = apiClient.getConnectionApi().resetConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitWhileJobHasStatus(apiClient.getJobsApi(), jobInfoRead.getJob(),
        Sets.newHashSet(JobStatus.PENDING, JobStatus.RUNNING, JobStatus.INCOMPLETE, JobStatus.FAILED));
    // This is a band-aid to prevent some race conditions where the job status was updated but we may
    // still be cleaning up some data in the reset table. This would be an argument for reworking the
    // source of truth of the replication workflow state to be in DB rather than in Memory and
    // serialized automagically by temporal
    waitWhileJobIsRunning(apiClient.getJobsApi(), jobInfoRead.getJob(), Duration.ofMinutes(1));

    LOGGER.info("state after reset: {}", apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    testHarness.assertRawDestinationContains(Collections.emptyList(), new SchemaTableNamePair(PUBLIC,
        STREAM_NAME));

    // sync one more time. verify it is the equivalent of a full refresh.
    LOGGER.info("Starting testIncrementalSync() sync 3");
    final JobInfoRead connectionSyncRead3 =
        apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead3.getJob());
    LOGGER.info("state after sync 3: {}", apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    testHarness.assertSourceAndDestinationDbInSync(WITHOUT_SCD_TABLE);

  }

  @Test
  void testMultipleSchemasAndTablesSyncAndReset() throws Exception {
    // create tables in another schema
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forClasspathResource("postgres_second_schema_multiple_tables.sql"), sourcePsql);

    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createPostgresDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);

    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));
    final UUID connectionId =
        testHarness.createConnection(TEST_CONNECTION, sourceId, destinationId, List.of(operationId), catalog, ConnectionScheduleType.MANUAL, null)
            .getConnectionId();
    final JobInfoRead connectionSyncRead = apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead.getJob());
    testHarness.assertSourceAndDestinationDbInSync(false);
    final JobInfoRead connectionResetRead = apiClient.getConnectionApi().resetConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionResetRead.getJob());
    testHarness.assertDestinationDbEmpty(false);
  }

  @Test
  void testPartialResetResetAllWhenSchemaIsModified(final TestInfo testInfo) throws Exception {
    LOGGER.info("Running: " + testInfo.getDisplayName());

    // Add Table
    final String additionalTable = "additional_table";
    final Database sourceDb = testHarness.getSourceDatabase();
    sourceDb.query(ctx -> {
      ctx.createTableIfNotExists(additionalTable)
          .columns(DSL.field("id", SQLDataType.INTEGER), DSL.field(FIELD, SQLDataType.VARCHAR)).execute();
      ctx.truncate(additionalTable).execute();
      ctx.insertInto(DSL.table(additionalTable)).columns(DSL.field("id"), DSL.field(FIELD)).values(1, "1").execute();
      ctx.insertInto(DSL.table(additionalTable)).columns(DSL.field("id"), DSL.field(FIELD)).values(2, "2").execute();
      return null;
    });
    UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    final UUID destinationId = testHarness.createPostgresDestination().getDestinationId();
    final OperationRead operation = testHarness.createOperation();
    final UUID operationId = operation.getOperationId();
    final String name = "test_reset_when_schema_is_modified_" + UUID.randomUUID();

    testHarness.setIncrementalAppendSyncMode(catalog, List.of(COLUMN_ID));

    final ConnectionRead connection =
        testHarness.createConnection(name, sourceId, destinationId, List.of(operationId), catalog, ConnectionScheduleType.MANUAL, null);

    // Run initial sync
    final JobInfoRead syncRead =
        apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connection.getConnectionId()));
    waitForSuccessfulJob(apiClient.getJobsApi(), syncRead.getJob());

    testHarness.assertSourceAndDestinationDbInSync(WITHOUT_SCD_TABLE);
    assertStreamStateContainsStream(connection.getConnectionId(), List.of(
        new StreamDescriptor().name(ID_AND_NAME).namespace(PUBLIC),
        new StreamDescriptor().name(additionalTable).namespace(PUBLIC)));

    LOGGER.info("Initial sync ran, now running an update with a stream being removed.");

    /**
     * Remove stream
     */
    sourceDb.query(ctx -> ctx.dropTableIfExists(additionalTable).execute());

    // Update with refreshed catalog
    AirbyteCatalog refreshedCatalog = testHarness.discoverSourceSchemaWithoutCache(sourceId);
    WebBackendConnectionUpdate update = testHarness.getUpdateInput(connection, refreshedCatalog, operation);
    webBackendApi.webBackendUpdateConnection(update);

    // Wait until the sync from the UpdateConnection is finished
    JobRead syncFromTheUpdate = waitUntilTheNextJobIsStarted(connection.getConnectionId());
    waitForSuccessfulJob(apiClient.getJobsApi(), syncFromTheUpdate);

    // We do not check that the source and the dest are in sync here because removing a stream doesn't
    // remove that
    assertStreamStateContainsStream(connection.getConnectionId(), List.of(
        new StreamDescriptor().name(ID_AND_NAME).namespace(PUBLIC)));

    LOGGER.info("Remove done, now running an update with a stream being added.");

    /**
     * Add a stream -- the value of in the table are different than the initial import to ensure that it
     * is properly reset.
     */
    sourceDb.query(ctx -> {
      ctx.createTableIfNotExists(additionalTable)
          .columns(DSL.field("id", SQLDataType.INTEGER), DSL.field(FIELD, SQLDataType.VARCHAR)).execute();
      ctx.truncate(additionalTable).execute();
      ctx.insertInto(DSL.table(additionalTable)).columns(DSL.field("id"), DSL.field(FIELD)).values(3, "3").execute();
      ctx.insertInto(DSL.table(additionalTable)).columns(DSL.field("id"), DSL.field(FIELD)).values(4, "4").execute();
      return null;
    });

    sourceId = testHarness.createPostgresSource().getSourceId();
    refreshedCatalog = testHarness.discoverSourceSchema(sourceId);
    update = testHarness.getUpdateInput(connection, refreshedCatalog, operation);
    webBackendApi.webBackendUpdateConnection(update);

    syncFromTheUpdate = waitUntilTheNextJobIsStarted(connection.getConnectionId());
    waitForSuccessfulJob(apiClient.getJobsApi(), syncFromTheUpdate);

    // We do not check that the source and the dest are in sync here because removing a stream doesn't
    // remove that
    testHarness.assertSourceAndDestinationDbInSync(WITHOUT_SCD_TABLE);
    assertStreamStateContainsStream(connection.getConnectionId(), List.of(
        new StreamDescriptor().name(ID_AND_NAME).namespace(PUBLIC),
        new StreamDescriptor().name(additionalTable).namespace(PUBLIC)));

    LOGGER.info("Addition done, now running an update with a stream being updated.");

    // Update
    sourceDb.query(ctx -> {
      ctx.dropTableIfExists(additionalTable).execute();
      ctx.createTableIfNotExists(additionalTable)
          .columns(DSL.field("id", SQLDataType.INTEGER), DSL.field(FIELD, SQLDataType.VARCHAR), DSL.field("another_field", SQLDataType.VARCHAR))
          .execute();
      ctx.truncate(additionalTable).execute();
      ctx.insertInto(DSL.table(additionalTable)).columns(DSL.field("id"), DSL.field(FIELD), DSL.field("another_field")).values(3, "3", "three")
          .execute();
      ctx.insertInto(DSL.table(additionalTable)).columns(DSL.field("id"), DSL.field(FIELD), DSL.field("another_field")).values(4, "4", "four")
          .execute();
      return null;
    });

    sourceId = testHarness.createPostgresSource().getSourceId();
    refreshedCatalog = testHarness.discoverSourceSchema(sourceId);
    update = testHarness.getUpdateInput(connection, refreshedCatalog, operation);
    webBackendApi.webBackendUpdateConnection(update);

    syncFromTheUpdate = waitUntilTheNextJobIsStarted(connection.getConnectionId());
    waitForSuccessfulJob(apiClient.getJobsApi(), syncFromTheUpdate);

    // We do not check that the source and the dest are in sync here because removing a stream doesn't
    // remove that
    testHarness.assertSourceAndDestinationDbInSync(WITHOUT_SCD_TABLE);
    assertStreamStateContainsStream(connection.getConnectionId(), List.of(
        new StreamDescriptor().name(ID_AND_NAME).namespace(PUBLIC),
        new StreamDescriptor().name(additionalTable).namespace(PUBLIC)));

  }

  @Test
  @Order(19)
  void testIncrementalDedupeSyncRemoveOneColumn() throws Exception {
    // !!! NOTE !!! this test relies on a feature flag that currently defaults to false. If you're
    // running these tests locally against an external deployment and this test is failing, make sure
    // the flag is enabled.
    // Specifically:
    // APPLY_FIELD_SELECTION=true
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createPostgresDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    final SyncMode syncMode = SyncMode.INCREMENTAL;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.APPEND_DEDUP;
    catalog.getStreams().forEach(s -> s.getConfig()
        .syncMode(syncMode)
        .cursorField(List.of(COLUMN_ID))
        .destinationSyncMode(destinationSyncMode)
        .primaryKey(List.of(List.of(COLUMN_ID))));
    final UUID connectionId =
        testHarness.createConnection(TEST_CONNECTION, sourceId, destinationId, List.of(operationId), catalog, ConnectionScheduleType.MANUAL, null)
            .getConnectionId();

    // sync from start
    final JobInfoRead connectionSyncRead1 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead1.getJob());

    testHarness.assertSourceAndDestinationDbInSync(WITH_SCD_TABLE);

    // Update the catalog, so we only select the id column.
    catalog.getStreams().get(0).getConfig().fieldSelectionEnabled(true).addSelectedFieldsItem(new SelectedFieldInfo().addFieldPathItem("id"));
    testHarness.updateConnectionCatalog(connectionId, catalog);

    // add new records and run again.
    final Database source = testHarness.getSourceDatabase();
    final List<JsonNode> expectedRawRecords = testHarness.retrieveSourceRecords(source, STREAM_NAME);
    source.query(ctx -> ctx.execute("INSERT INTO id_and_name(id, name) VALUES(6, 'mike')"));
    source.query(ctx -> ctx.execute("INSERT INTO id_and_name(id, name) VALUES(7, 'chris')"));
    // The expected new raw records should only have the ID column.
    expectedRawRecords.add(Jsons.jsonNode(ImmutableMap.builder().put(COLUMN_ID, 6).build()));
    expectedRawRecords.add(Jsons.jsonNode(ImmutableMap.builder().put(COLUMN_ID, 7).build()));
    final JobInfoRead connectionSyncRead2 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead2.getJob());

    // For the normalized records, they should all only have the ID column.
    final List<JsonNode> expectedNormalizedRecords = testHarness.retrieveSourceRecords(source, STREAM_NAME).stream()
        .map((record) -> ((ObjectNode) record).retain(COLUMN_ID)).collect(Collectors.toList());

    testHarness.assertRawDestinationContains(expectedRawRecords, new SchemaTableNamePair(PUBLIC, STREAM_NAME));
    testHarness.assertNormalizedDestinationContainsIdColumn(expectedNormalizedRecords);
  }

  private void assertStreamStateContainsStream(final UUID connectionId, final List<StreamDescriptor> expectedStreamDescriptors) throws ApiException {
    final ConnectionState state = apiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId));
    final List<StreamDescriptor> streamDescriptors = state.getStreamState().stream().map(StreamState::getStreamDescriptor).toList();

    Assertions.assertTrue(streamDescriptors.containsAll(expectedStreamDescriptors) && expectedStreamDescriptors.containsAll(streamDescriptors));
  }

  private JobRead getMostRecentSyncJobId(final UUID connectionId) throws Exception {
    return apiClient.getJobsApi()
        .listJobsFor(new JobListRequestBody().configId(connectionId.toString()).configTypes(List.of(JobConfigType.SYNC)))
        .getJobs()
        .stream().findFirst().map(JobWithAttemptsRead::getJob).orElseThrow();
  }

  private JobRead waitUntilTheNextJobIsStarted(final UUID connectionId) throws Exception {
    final JobRead lastJob = getMostRecentSyncJobId(connectionId);
    if (lastJob.getStatus() != JobStatus.SUCCEEDED) {
      return lastJob;
    }

    JobRead mostRecentSyncJob = getMostRecentSyncJobId(connectionId);
    while (mostRecentSyncJob.getId().equals(lastJob.getId())) {
      Thread.sleep(Duration.ofSeconds(10).toMillis());
      mostRecentSyncJob = getMostRecentSyncJobId(connectionId);
    }
    return mostRecentSyncJob;
  }

  /**
   * Waits for the given connection to finish, waiting at 30s intervals, until maxRetries is reached.
   *
   * @param connectionId the connection to wait for
   * @param maxRetries the number of times to retry
   * @throws InterruptedException
   */
  private void waitForSuccessfulJobWithRetries(final UUID connectionId, final int maxRetries) throws InterruptedException {
    int i;
    for (i = 0; i < maxRetries; i++) {
      try {
        final JobRead jobInfo = testHarness.getMostRecentSyncJobId(connectionId);
        waitForSuccessfulJob(apiClient.getJobsApi(), jobInfo);
        break;
      } catch (final Exception e) {
        LOGGER.info("Something went wrong querying jobs API, retrying...");
      }
      sleep(Duration.ofSeconds(30).toMillis());
    }

    if (i == maxRetries) {
      LOGGER.error("Sync job did not complete within 5 minutes");
    }
  }

  // This test is disabled because it takes a couple of minutes to run, as it is testing timeouts.
  // It should be re-enabled when the @SlowIntegrationTest can be applied to it.
  // See relevant issue: https://github.com/airbytehq/airbyte/issues/8397
  @Test
  @Disabled
  void testFailureTimeout() throws Exception {
    final SourceDefinitionRead sourceDefinition = testHarness.createE2eSourceDefinition(workspaceId);
    final DestinationDefinitionRead destinationDefinition = testHarness.createE2eDestinationDefinition(workspaceId);

    final SourceRead source = testHarness.createSource(
        E2E_TEST_SOURCE + UUID.randomUUID(),
        workspaceId,
        sourceDefinition.getSourceDefinitionId(),
        Jsons.jsonNode(ImmutableMap.builder()
            .put(TYPE, INFINITE_FEED)
            .put(MAX_RECORDS, 1000)
            .put(MESSAGE_INTERVAL, 100)
            .build()));

    // Destination fails after processing 5 messages, so the job should fail after the graceful close
    // timeout of 1 minute
    final DestinationRead destination = testHarness.createDestination(
        "E2E Test Destination -" + UUID.randomUUID(),
        workspaceId,
        destinationDefinition.getDestinationDefinitionId(),
        Jsons.jsonNode(ImmutableMap.builder()
            .put(TYPE, "FAILING")
            .put("num_messages", 5)
            .build()));

    final UUID sourceId = source.getSourceId();
    final UUID destinationId = destination.getDestinationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);

    final UUID connectionId =
        testHarness.createConnection(TEST_CONNECTION, sourceId, destinationId, Collections.emptyList(), catalog, ConnectionScheduleType.MANUAL, null)
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
