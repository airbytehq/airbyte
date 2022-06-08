/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.acceptance;

import static java.lang.Thread.sleep;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import com.google.common.io.Resources;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.generated.JobsApi;
import io.airbyte.api.client.invoker.generated.ApiClient;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.AirbyteCatalog;
import io.airbyte.api.client.model.generated.AirbyteStream;
import io.airbyte.api.client.model.generated.AttemptInfoRead;
import io.airbyte.api.client.model.generated.ConnectionCreate;
import io.airbyte.api.client.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.client.model.generated.ConnectionRead;
import io.airbyte.api.client.model.generated.ConnectionSchedule;
import io.airbyte.api.client.model.generated.ConnectionState;
import io.airbyte.api.client.model.generated.ConnectionStatus;
import io.airbyte.api.client.model.generated.ConnectionUpdate;
import io.airbyte.api.client.model.generated.DestinationCreate;
import io.airbyte.api.client.model.generated.DestinationDefinitionCreate;
import io.airbyte.api.client.model.generated.DestinationDefinitionIdRequestBody;
import io.airbyte.api.client.model.generated.DestinationDefinitionRead;
import io.airbyte.api.client.model.generated.DestinationIdRequestBody;
import io.airbyte.api.client.model.generated.DestinationRead;
import io.airbyte.api.client.model.generated.DestinationSyncMode;
import io.airbyte.api.client.model.generated.JobIdRequestBody;
import io.airbyte.api.client.model.generated.JobInfoRead;
import io.airbyte.api.client.model.generated.JobRead;
import io.airbyte.api.client.model.generated.JobStatus;
import io.airbyte.api.client.model.generated.LogType;
import io.airbyte.api.client.model.generated.LogsRequestBody;
import io.airbyte.api.client.model.generated.NamespaceDefinitionType;
import io.airbyte.api.client.model.generated.OperationCreate;
import io.airbyte.api.client.model.generated.OperationIdRequestBody;
import io.airbyte.api.client.model.generated.OperationRead;
import io.airbyte.api.client.model.generated.OperatorConfiguration;
import io.airbyte.api.client.model.generated.OperatorNormalization;
import io.airbyte.api.client.model.generated.OperatorNormalization.OptionEnum;
import io.airbyte.api.client.model.generated.OperatorType;
import io.airbyte.api.client.model.generated.SourceCreate;
import io.airbyte.api.client.model.generated.SourceDefinitionCreate;
import io.airbyte.api.client.model.generated.SourceDefinitionIdRequestBody;
import io.airbyte.api.client.model.generated.SourceDefinitionRead;
import io.airbyte.api.client.model.generated.SourceDiscoverSchemaRequestBody;
import io.airbyte.api.client.model.generated.SourceIdRequestBody;
import io.airbyte.api.client.model.generated.SourceRead;
import io.airbyte.api.client.model.generated.SyncMode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.MoreBooleans;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.MoreProperties;
import io.airbyte.container_orchestrator.ContainerOrchestratorApp;
import io.airbyte.db.Database;
import io.airbyte.test.airbyte_test_container.AirbyteTestContainer;
import io.airbyte.test.utils.DatabaseConnectionHelper;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import java.io.File;
import java.io.IOException;
import java.net.Inet4Address;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.UnknownHostException;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.sql.SQLException;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import org.jooq.JSONB;
import org.jooq.Record;
import org.jooq.Result;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.junit.jupiter.api.Timeout;
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable;
import org.junitpioneer.jupiter.RetryingTest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

/**
 * The class test for advanced platform functionality that can be affected by the networking
 * difference between the Kube and Docker deployments i.e. distributed vs local processes. All tests
 * in this class should pass when ran on either type of deployment.
 * <p>
 * Tests use the {@link RetryingTest} annotation instead of the more common {@link Test} to allow
 * multiple tries for a test to pass. This is because these tests sometimes fail transiently, and we
 * haven't been able to fix that yet.
 * <p>
 * However, in general we should prefer using {@code @Test} instead and only resort to using
 * {@code @RetryingTest} for tests that we can't get to pass reliably. New tests should thus default
 * to using {@code @Test} if possible.
 * <p>
 * We order tests such that earlier tests test more basic behavior that is relied upon in later
 * tests. e.g. We test that we can create a destination before we test whether we can sync data to
 * it.
 */
@SuppressWarnings({"rawtypes", "ConstantConditions"})
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class AdvancedAcceptanceTests {

  private static final Logger LOGGER = LoggerFactory.getLogger(AdvancedAcceptanceTests.class);

  private static final String DOCKER_COMPOSE_FILE_NAME = "docker-compose.yaml";
  // assume env file is one directory level up from airbyte-tests.
  private final static File ENV_FILE = Path.of(System.getProperty("user.dir")).getParent().resolve(".env").toFile();

  private static final String SOURCE_E2E_TEST_CONNECTOR_VERSION = "0.1.1";
  private static final String DESTINATION_E2E_TEST_CONNECTOR_VERSION = "0.1.1";

  private static final Charset UTF8 = StandardCharsets.UTF_8;
  private static final boolean IS_KUBE = System.getenv().containsKey("KUBE");
  private static final boolean IS_MINIKUBE = System.getenv().containsKey("IS_MINIKUBE");
  private static final boolean IS_GKE = System.getenv().containsKey("IS_GKE");
  private static final boolean IS_MAC = System.getProperty("os.name").startsWith("Mac");
  private static final boolean USE_EXTERNAL_DEPLOYMENT =
      System.getenv("USE_EXTERNAL_DEPLOYMENT") != null && System.getenv("USE_EXTERNAL_DEPLOYMENT").equalsIgnoreCase("true");

  private static final String OUTPUT_NAMESPACE_PREFIX = "output_namespace_";
  private static final String OUTPUT_NAMESPACE = OUTPUT_NAMESPACE_PREFIX + "${SOURCE_NAMESPACE}";
  private static final String OUTPUT_STREAM_PREFIX = "output_table_";
  private static final String TABLE_NAME = "id_and_name";
  private static final String STREAM_NAME = TABLE_NAME;
  private static final String COLUMN_ID = "id";
  private static final String COLUMN_NAME = "name";
  private static final String COLUMN_NAME_DATA = "_airbyte_data";
  private static final String SOURCE_USERNAME = "sourceusername";
  private static final String SOURCE_PASSWORD = "hunter2";

  /**
   * When the acceptance tests are run against a local instance of docker-compose or KUBE then these
   * test containers are used. When we run these tests in GKE, we spawn a source and destination
   * postgres database ane use them for testing.
   */
  private static PostgreSQLContainer sourcePsql;
  private static PostgreSQLContainer destinationPsql;
  private static AirbyteTestContainer airbyteTestContainer;
  private static AirbyteApiClient apiClient;
  private static UUID workspaceId;

  private List<UUID> sourceIds;
  private List<UUID> connectionIds;
  private List<UUID> destinationIds;
  private List<UUID> operationIds;

  private static KubernetesClient kubernetesClient = null;

  @SuppressWarnings("UnstableApiUsage")
  @BeforeAll
  public static void init() throws URISyntaxException, IOException, InterruptedException, ApiException, SQLException {
    if (IS_GKE && !IS_KUBE) {
      throw new RuntimeException("KUBE Flag should also be enabled if GKE flag is enabled");
    }
    if (!IS_GKE) {
      sourcePsql = new PostgreSQLContainer("postgres:13-alpine")
          .withUsername(SOURCE_USERNAME)
          .withPassword(SOURCE_PASSWORD);
      sourcePsql.start();
    }

    if (IS_KUBE) {
      kubernetesClient = new DefaultKubernetesClient();
    }

    // by default use airbyte deployment governed by a test container.
    if (!USE_EXTERNAL_DEPLOYMENT) {
      LOGGER.info("Using deployment of airbyte managed by test containers.");
      airbyteTestContainer = new AirbyteTestContainer.Builder(new File(Resources.getResource(DOCKER_COMPOSE_FILE_NAME).toURI()))
          .setEnv(MoreProperties.envFileToProperties(ENV_FILE))
          // override env VERSION to use dev to test current build of airbyte.
          .setEnvVariable("VERSION", "dev")
          // override to use test mounts.
          .setEnvVariable("DATA_DOCKER_MOUNT", "airbyte_data_migration_test")
          .setEnvVariable("DB_DOCKER_MOUNT", "airbyte_db_migration_test")
          .setEnvVariable("WORKSPACE_DOCKER_MOUNT", "airbyte_workspace_migration_test")
          .setEnvVariable("LOCAL_ROOT", "/tmp/airbyte_local_migration_test")
          .setEnvVariable("LOCAL_DOCKER_MOUNT", "/tmp/airbyte_local_migration_test")
          .build();
      airbyteTestContainer.startBlocking();
    } else {
      LOGGER.info("Using external deployment of airbyte.");
    }

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

    if (!IS_GKE) {
      destinationPsql = new PostgreSQLContainer("postgres:13-alpine");
      destinationPsql.start();
    }

  }

  @AfterAll
  public static void end() {
    if (!IS_GKE) {
      sourcePsql.stop();
      destinationPsql.stop();
    }

    if (airbyteTestContainer != null) {
      airbyteTestContainer.stop();
    }
  }

  @BeforeEach
  public void setup() throws URISyntaxException, IOException, SQLException {
    sourceIds = Lists.newArrayList();
    connectionIds = Lists.newArrayList();
    destinationIds = Lists.newArrayList();
    operationIds = Lists.newArrayList();

    if (IS_GKE) {
      // seed database.
      final Database database = getSourceDatabase();
      final Path path = Path.of(MoreResources.readResourceAsFile("postgres_init.sql").toURI());
      final StringBuilder query = new StringBuilder();
      for (final String line : java.nio.file.Files.readAllLines(path, UTF8)) {
        if (line != null && !line.isEmpty()) {
          query.append(line);
        }
      }
      database.query(context -> context.execute(query.toString()));
    } else {
      PostgreSQLContainerHelper.runSqlScript(MountableFile.forClasspathResource("postgres_init.sql"), sourcePsql);
    }
  }

  @AfterEach
  public void tearDown() {
    try {
      clearSourceDbData();
      clearDestinationDbData();

      for (final UUID operationId : operationIds) {
        deleteOperation(operationId);
      }

      for (final UUID connectionId : connectionIds) {
        disableConnection(connectionId);
      }

      for (final UUID sourceId : sourceIds) {
        deleteSource(sourceId);
      }

      for (final UUID destinationId : destinationIds) {
        deleteDestination(destinationId);
      }
    } catch (Exception e) {
      LOGGER.error("Error tearing down test fixtures:", e);
    }
  }

  @RetryingTest(3)
  @Order(1)
  public void testManualSync() throws Exception {
    final String connectionName = "test-connection";
    final UUID sourceId = createPostgresSource().getSourceId();
    final UUID destinationId = createDestination().getDestinationId();
    final UUID operationId = createOperation().getOperationId();
    final AirbyteCatalog catalog = discoverSourceSchema(sourceId);
    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));
    final UUID connectionId =
        createConnection(connectionName, sourceId, destinationId, List.of(operationId), catalog, null).getConnectionId();
    final JobInfoRead connectionSyncRead = apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead.getJob());
    assertSourceAndDestinationDbInSync(false);
  }

  @RetryingTest(3)
  @Order(2)
  public void testCheckpointing() throws Exception {
    final SourceDefinitionRead sourceDefinition = createE2eSourceDefinition();
    final DestinationDefinitionRead destinationDefinition = createE2eDestinationDefinition();

    final SourceRead source = createSource(
        "E2E Test Source -" + UUID.randomUUID(),
        workspaceId,
        sourceDefinition.getSourceDefinitionId(),
        Jsons.jsonNode(ImmutableMap.builder()
            .put("type", "EXCEPTION_AFTER_N")
            .put("throw_after_n_records", 100)
            .build()));

    final DestinationRead destination = createDestination(
        "E2E Test Destination -" + UUID.randomUUID(),
        workspaceId,
        destinationDefinition.getDestinationDefinitionId(),
        Jsons.jsonNode(ImmutableMap.of("type", "SILENT")));

    final String connectionName = "test-connection";
    final UUID sourceId = source.getSourceId();
    final UUID destinationId = destination.getDestinationId();
    final AirbyteCatalog catalog = discoverSourceSchema(sourceId);
    final AirbyteStream stream = catalog.getStreams().get(0).getStream();

    assertEquals(
        Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL),
        stream.getSupportedSyncModes());
    assertTrue(MoreBooleans.isTruthy(stream.getSourceDefinedCursor()));

    final SyncMode syncMode = SyncMode.INCREMENTAL;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.APPEND;
    catalog.getStreams().forEach(s -> s.getConfig()
        .syncMode(syncMode)
        .cursorField(List.of(COLUMN_ID))
        .destinationSyncMode(destinationSyncMode));
    final UUID connectionId =
        createConnection(connectionName, sourceId, destinationId, Collections.emptyList(), catalog, null).getConnectionId();
    final JobInfoRead connectionSyncRead1 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));

    // wait to get out of pending.
    final JobRead runningJob = waitWhileJobHasStatus(apiClient.getJobsApi(), connectionSyncRead1.getJob(), Sets.newHashSet(JobStatus.PENDING));
    // wait to get out of running.
    waitWhileJobHasStatus(apiClient.getJobsApi(), runningJob, Sets.newHashSet(JobStatus.RUNNING));
    // now cancel it so that we freeze state!
    try {
      apiClient.getJobsApi().cancelJob(new JobIdRequestBody().id(connectionSyncRead1.getJob().getId()));
    } catch (final Exception e) {}

    final ConnectionState connectionState = waitForConnectionState(apiClient, connectionId);

    // the source is set to emit a state message every 5th message. because of the multi threaded
    // nature, we can't guarantee exactly what checkpoint will be registered. what we can do is send
    // enough messages to make sure that we checkpoint at least once.
    assertNotNull(connectionState.getState());
    assertTrue(connectionState.getState().get("column1").isInt());
    LOGGER.info("state value: {}", connectionState.getState().get("column1").asInt());
    assertTrue(connectionState.getState().get("column1").asInt() > 0);
    assertEquals(0, connectionState.getState().get("column1").asInt() % 5);
  }

  @RetryingTest(3)
  @Order(3)
  public void testRedactionOfSensitiveRequestBodies() throws Exception {
    // check that the source password is not present in the logs
    final List<String> serverLogLines = java.nio.file.Files.readAllLines(
        apiClient.getLogsApi().getLogs(new LogsRequestBody().logType(LogType.SERVER)).toPath(),
        Charset.defaultCharset());

    assertTrue(serverLogLines.size() > 0);

    boolean hasRedacted = false;

    for (final String line : serverLogLines) {
      assertFalse(line.contains(SOURCE_PASSWORD));

      if (line.contains("REDACTED")) {
        hasRedacted = true;
      }
    }

    assertTrue(hasRedacted);
  }

  // verify that when the worker uses backpressure from pipes that no records are lost.
  @RetryingTest(3)
  @Order(4)
  public void testBackpressure() throws Exception {
    final SourceDefinitionRead sourceDefinition = createE2eSourceDefinition();
    final DestinationDefinitionRead destinationDefinition = createE2eDestinationDefinition();

    final SourceRead source = createSource(
        "E2E Test Source -" + UUID.randomUUID(),
        workspaceId,
        sourceDefinition.getSourceDefinitionId(),
        Jsons.jsonNode(ImmutableMap.builder()
            .put("type", "INFINITE_FEED")
            .put("max_records", 5000)
            .build()));

    final DestinationRead destination = createDestination(
        "E2E Test Destination -" + UUID.randomUUID(),
        workspaceId,
        destinationDefinition.getDestinationDefinitionId(),
        Jsons.jsonNode(ImmutableMap.builder()
            .put("type", "THROTTLED")
            .put("millis_per_record", 1)
            .build()));

    final String connectionName = "test-connection";
    final UUID sourceId = source.getSourceId();
    final UUID destinationId = destination.getDestinationId();
    final AirbyteCatalog catalog = discoverSourceSchema(sourceId);

    final UUID connectionId =
        createConnection(connectionName, sourceId, destinationId, Collections.emptyList(), catalog, null)
            .getConnectionId();
    final JobInfoRead connectionSyncRead1 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));

    // wait to get out of pending.
    final JobRead runningJob = waitWhileJobHasStatus(apiClient.getJobsApi(), connectionSyncRead1.getJob(), Sets.newHashSet(JobStatus.PENDING));
    // wait to get out of running.
    waitWhileJobHasStatus(apiClient.getJobsApi(), runningJob, Sets.newHashSet(JobStatus.RUNNING));

    final JobInfoRead jobInfo = apiClient.getJobsApi().getJobInfo(new JobIdRequestBody().id(runningJob.getId()));
    final AttemptInfoRead attemptInfoRead = jobInfo.getAttempts().get(jobInfo.getAttempts().size() - 1);
    assertNotNull(attemptInfoRead);

    int expectedMessageNumber = 0;
    final int max = 10_000;
    for (final String logLine : attemptInfoRead.getLogs().getLogLines()) {
      if (expectedMessageNumber > max) {
        break;
      }

      if (logLine.contains("received record: ") && logLine.contains("\"type\": \"RECORD\"")) {
        assertTrue(
            logLine.contains(String.format("\"column1\": \"%s\"", expectedMessageNumber)),
            String.format("Expected %s but got: %s", expectedMessageNumber, logLine));
        expectedMessageNumber++;
      }
    }
  }

  @RetryingTest(3)
  @Order(5)
  @EnabledIfEnvironmentVariable(named = "CONTAINER_ORCHESTRATOR",
                                matches = "true")
  public void testDowntimeDuringSync() throws Exception {
    final String connectionName = "test-connection";
    final UUID sourceId = createPostgresSource().getSourceId();
    final UUID destinationId = createDestination().getDestinationId();
    final AirbyteCatalog catalog = discoverSourceSchema(sourceId);
    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));

    for (final var input : List.of("KILL_BOTH_NON_SYNC_SLIGHTLY_FIRST", "KILL_ONLY_SYNC", "KILL_ONLY_NON_SYNC")) {
      LOGGER.info("Checking " + input);

      final UUID connectionId =
          createConnection(connectionName, sourceId, destinationId, List.of(), catalog, null).getConnectionId();

      JobInfoRead connectionSyncRead = null;

      while (connectionSyncRead == null) {

        try {
          connectionSyncRead = apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
        } catch (final Exception e) {
          LOGGER.error("retrying after error", e);
        }
      }

      Thread.sleep(10000);

      switch (input) {
        case "KILL_BOTH_NON_SYNC_SLIGHTLY_FIRST" -> {
          LOGGER.info("Scaling down both workers at roughly the same time...");
          kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-worker").scale(0);
          kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-sync-worker").scale(0, true);

          LOGGER.info("Scaling up both workers...");
          kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-worker").scale(1);
          kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-sync-worker").scale(1);
        }
        case "KILL_ONLY_SYNC" -> {
          LOGGER.info("Scaling down only sync worker...");
          kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-sync-worker").scale(0, true);

          LOGGER.info("Scaling up sync worker...");
          kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-sync-worker").scale(1);
        }
        case "KILL_ONLY_NON_SYNC" -> {
          LOGGER.info("Scaling down only non-sync worker...");
          kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-worker").scale(0, true);

          LOGGER.info("Scaling up non-sync worker...");
          kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-worker").scale(1);
        }
      }

      waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead.getJob());

      final long numAttempts = apiClient.getJobsApi()
          .getJobInfo(new JobIdRequestBody().id(connectionSyncRead.getJob().getId()))
          .getAttempts()
          .size();

      // it should be able to accomplish the resume without an additional attempt!
      assertEquals(1, numAttempts);
    }
  }

  @RetryingTest(3)
  @Order(6)
  @EnabledIfEnvironmentVariable(named = "CONTAINER_ORCHESTRATOR",
                                matches = "true")
  public void testCancelSyncWithInterruption() throws Exception {
    final String connectionName = "test-connection";
    final UUID sourceId = createPostgresSource().getSourceId();
    final UUID destinationId = createDestination().getDestinationId();
    final UUID operationId = createOperation().getOperationId();
    final AirbyteCatalog catalog = discoverSourceSchema(sourceId);
    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));
    final UUID connectionId =
        createConnection(connectionName, sourceId, destinationId, List.of(operationId), catalog, null).getConnectionId();

    final JobInfoRead connectionSyncRead = apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitWhileJobHasStatus(apiClient.getJobsApi(), connectionSyncRead.getJob(), Set.of(JobStatus.RUNNING));

    Thread.sleep(5000);

    kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-worker").scale(0);
    Thread.sleep(1000);
    kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-worker").scale(1);

    final var resp = apiClient.getJobsApi().cancelJob(new JobIdRequestBody().id(connectionSyncRead.getJob().getId()));
    assertEquals(JobStatus.CANCELLED, resp.getJob().getStatus());
  }

  @RetryingTest(3)
  @Order(7)
  @Timeout(value = 5,
           unit = TimeUnit.MINUTES)
  @EnabledIfEnvironmentVariable(named = "CONTAINER_ORCHESTRATOR",
                                matches = "true")
  public void testCuttingOffPodBeforeFilesTransfer() throws Exception {
    final String connectionName = "test-connection";
    final UUID sourceId = createPostgresSource().getSourceId();
    final UUID destinationId = createDestination().getDestinationId();
    final UUID operationId = createOperation().getOperationId();
    final AirbyteCatalog catalog = discoverSourceSchema(sourceId);
    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));

    LOGGER.info("Creating connection...");
    final UUID connectionId =
        createConnection(connectionName, sourceId, destinationId, List.of(operationId), catalog, null).getConnectionId();

    LOGGER.info("Waiting for connection to be available in Temporal...");

    LOGGER.info("Run manual sync...");
    final JobInfoRead connectionSyncRead = apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));

    LOGGER.info("Waiting for job to run...");
    waitWhileJobHasStatus(apiClient.getJobsApi(), connectionSyncRead.getJob(), Set.of(JobStatus.RUNNING));

    LOGGER.info("Scale down workers...");
    kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-worker").scale(0);

    LOGGER.info("Wait for worker scale down...");
    Thread.sleep(1000);

    LOGGER.info("Scale up workers...");
    kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-worker").scale(1);

    LOGGER.info("Waiting for worker timeout...");
    Thread.sleep(ContainerOrchestratorApp.MAX_SECONDS_TO_WAIT_FOR_FILE_COPY * 1000 + 1000);

    LOGGER.info("Waiting for job to retry and succeed...");
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead.getJob());
  }

  @RetryingTest(3)
  @Order(8)
  @Timeout(value = 5,
           unit = TimeUnit.MINUTES)
  @EnabledIfEnvironmentVariable(named = "CONTAINER_ORCHESTRATOR",
                                matches = "true")
  public void testCancelSyncWhenCancelledWhenWorkerIsNotRunning() throws Exception {
    final String connectionName = "test-connection";
    final UUID sourceId = createPostgresSource().getSourceId();
    final UUID destinationId = createDestination().getDestinationId();
    final UUID operationId = createOperation().getOperationId();
    final AirbyteCatalog catalog = discoverSourceSchema(sourceId);
    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));

    LOGGER.info("Creating connection...");
    final UUID connectionId =
        createConnection(connectionName, sourceId, destinationId, List.of(operationId), catalog, null).getConnectionId();

    LOGGER.info("Waiting for connection to be available in Temporal...");

    LOGGER.info("Run manual sync...");
    final JobInfoRead connectionSyncRead = apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));

    LOGGER.info("Waiting for job to run...");
    waitWhileJobHasStatus(apiClient.getJobsApi(), connectionSyncRead.getJob(), Set.of(JobStatus.RUNNING));

    LOGGER.info("Waiting for job to run a little...");
    Thread.sleep(5000);

    LOGGER.info("Scale down workers...");
    kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-worker").scale(0);

    LOGGER.info("Waiting for worker shutdown...");
    Thread.sleep(2000);

    LOGGER.info("Starting background cancellation request...");
    final var pool = Executors.newSingleThreadExecutor();
    final var mdc = MDC.getCopyOfContextMap();
    final Future<JobInfoRead> resp =
        pool.submit(() -> {
          MDC.setContextMap(mdc);
          try {
            final JobInfoRead jobInfoRead = apiClient.getJobsApi().cancelJob(new JobIdRequestBody().id(connectionSyncRead.getJob().getId()));
            LOGGER.info("jobInfoRead = " + jobInfoRead);
            return jobInfoRead;
          } catch (final ApiException e) {
            LOGGER.error("Failed to read from api", e);
            throw e;
          }
        });
    Thread.sleep(2000);

    LOGGER.info("Scaling up workers...");
    kubernetesClient.apps().deployments().inNamespace("default").withName("airbyte-worker").scale(1);

    LOGGER.info("Waiting for cancellation to go into effect...");
    assertEquals(JobStatus.CANCELLED, resp.get().getJob().getStatus());
  }

  private AirbyteCatalog discoverSourceSchema(final UUID sourceId) throws ApiException {
    return apiClient.getSourceApi().discoverSchemaForSource(new SourceDiscoverSchemaRequestBody().sourceId(sourceId)).getCatalog();
  }

  private void assertSourceAndDestinationDbInSync(final boolean withScdTable) throws Exception {
    final Database source = getSourceDatabase();

    final Set<SchemaTableNamePair> sourceTables = listAllTables(source);
    final Set<SchemaTableNamePair> sourceTablesWithRawTablesAdded = addAirbyteGeneratedTables(withScdTable, sourceTables);
    final Database destination = getDestinationDatabase();
    final Set<SchemaTableNamePair> destinationTables = listAllTables(destination);
    assertEquals(sourceTablesWithRawTablesAdded, destinationTables,
        String.format("streams did not match.\n source stream names: %s\n destination stream names: %s\n", sourceTables, destinationTables));

    for (final SchemaTableNamePair pair : sourceTables) {
      final List<JsonNode> sourceRecords = retrieveSourceRecords(source, pair.getFullyQualifiedTableName());
      assertRawDestinationContains(sourceRecords, pair);
    }
  }

  private static Database getSourceDatabase() {
    if (IS_KUBE && IS_GKE) {
      return GKEPostgresConfig.getSourceDatabase();
    }
    return getDatabase(sourcePsql);
  }

  private static Database getDatabase(final PostgreSQLContainer db) {
    return new Database(DatabaseConnectionHelper.createDslContext(db, SQLDialect.POSTGRES));
  }

  private Database getDestinationDatabase() {
    if (IS_KUBE && IS_GKE) {
      return GKEPostgresConfig.getDestinationDatabase();
    }
    return getDatabase(destinationPsql);
  }

  private Set<SchemaTableNamePair> listAllTables(final Database database) throws SQLException {
    return database.query(
        context -> {
          final Result<Record> fetch =
              context.fetch(
                  "SELECT tablename, schemaname FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'");
          return fetch.stream()
              .map(record -> {
                final var schemaName = (String) record.get("schemaname");
                final var tableName = (String) record.get("tablename");
                return new SchemaTableNamePair(schemaName, tableName);
              })
              .collect(Collectors.toSet());
        });
  }

  private Set<SchemaTableNamePair> addAirbyteGeneratedTables(final boolean withScdTable, final Set<SchemaTableNamePair> sourceTables) {
    return sourceTables.stream().flatMap(x -> {
      final String cleanedNameStream = x.tableName.replace(".", "_");
      final List<SchemaTableNamePair> explodedStreamNames = new ArrayList<>(List.of(
          new SchemaTableNamePair(OUTPUT_NAMESPACE_PREFIX + x.schemaName,
              String.format("_airbyte_raw_%s%s", OUTPUT_STREAM_PREFIX, cleanedNameStream)),
          new SchemaTableNamePair(OUTPUT_NAMESPACE_PREFIX + x.schemaName, String.format("%s%s", OUTPUT_STREAM_PREFIX, cleanedNameStream))));
      if (withScdTable) {
        explodedStreamNames
            .add(new SchemaTableNamePair("_airbyte_" + OUTPUT_NAMESPACE_PREFIX + x.schemaName,
                String.format("%s%s_stg", OUTPUT_STREAM_PREFIX, cleanedNameStream)));
        explodedStreamNames
            .add(new SchemaTableNamePair(OUTPUT_NAMESPACE_PREFIX + x.schemaName, String.format("%s%s_scd", OUTPUT_STREAM_PREFIX, cleanedNameStream)));
      }
      return explodedStreamNames.stream();
    }).collect(Collectors.toSet());
  }

  private void assertRawDestinationContains(final List<JsonNode> sourceRecords, final SchemaTableNamePair pair) throws Exception {
    final Set<JsonNode> destinationRecords = new HashSet<>(retrieveRawDestinationRecords(pair));

    assertEquals(sourceRecords.size(), destinationRecords.size(),
        String.format("destination contains: %s record. source contains: %s, \nsource records %s \ndestination records: %s",
            destinationRecords.size(), sourceRecords.size(), sourceRecords, destinationRecords));

    for (final JsonNode sourceStreamRecord : sourceRecords) {
      assertTrue(destinationRecords.contains(sourceStreamRecord),
          String.format("destination does not contain record:\n %s \n destination contains:\n %s\n",
              sourceStreamRecord, destinationRecords));
    }
  }

  private ConnectionRead createConnection(final String name,
                                          final UUID sourceId,
                                          final UUID destinationId,
                                          final List<UUID> operationIds,
                                          final AirbyteCatalog catalog,
                                          final ConnectionSchedule schedule)
      throws ApiException {
    final ConnectionRead connection = apiClient.getConnectionApi().createConnection(
        new ConnectionCreate()
            .status(ConnectionStatus.ACTIVE)
            .sourceId(sourceId)
            .destinationId(destinationId)
            .syncCatalog(catalog)
            .schedule(schedule)
            .operationIds(operationIds)
            .name(name)
            .namespaceDefinition(NamespaceDefinitionType.CUSTOMFORMAT)
            .namespaceFormat(OUTPUT_NAMESPACE)
            .prefix(OUTPUT_STREAM_PREFIX));
    connectionIds.add(connection.getConnectionId());
    return connection;
  }

  private DestinationRead createDestination() throws ApiException {
    return createDestination(
        "AccTestDestination-" + UUID.randomUUID(),
        workspaceId,
        getDestinationDefId(),
        getDestinationDbConfig());
  }

  private DestinationRead createDestination(final String name, final UUID workspaceId, final UUID destinationDefId, final JsonNode destinationConfig)
      throws ApiException {
    final DestinationRead destination =
        apiClient.getDestinationApi().createDestination(new DestinationCreate()
            .name(name)
            .connectionConfiguration(Jsons.jsonNode(destinationConfig))
            .workspaceId(workspaceId)
            .destinationDefinitionId(destinationDefId));
    destinationIds.add(destination.getDestinationId());
    return destination;
  }

  private OperationRead createOperation() throws ApiException {
    final OperatorConfiguration normalizationConfig = new OperatorConfiguration()
        .operatorType(OperatorType.NORMALIZATION).normalization(new OperatorNormalization().option(
            OptionEnum.BASIC));

    final OperationCreate operationCreate = new OperationCreate()
        .workspaceId(workspaceId)
        .name("AccTestDestination-" + UUID.randomUUID()).operatorConfiguration(normalizationConfig);

    final OperationRead operation = apiClient.getOperationApi().createOperation(operationCreate);
    operationIds.add(operation.getOperationId());
    return operation;
  }

  private UUID getDestinationDefId() throws ApiException {
    return apiClient.getDestinationDefinitionApi().listDestinationDefinitions().getDestinationDefinitions()
        .stream()
        .filter(dr -> dr.getName().toLowerCase().contains("postgres"))
        .findFirst()
        .orElseThrow()
        .getDestinationDefinitionId();
  }

  private List<JsonNode> retrieveSourceRecords(final Database database, final String table) throws SQLException {
    return database.query(context -> context.fetch(String.format("SELECT * FROM %s;", table)))
        .stream()
        .map(Record::intoMap)
        .map(Jsons::jsonNode)
        .collect(Collectors.toList());
  }

  private List<JsonNode> retrieveDestinationRecords(final Database database, final String table) throws SQLException {
    return database.query(context -> context.fetch(String.format("SELECT * FROM %s;", table)))
        .stream()
        .map(Record::intoMap)
        .map(r -> r.get(COLUMN_NAME_DATA))
        .map(f -> (JSONB) f)
        .map(JSONB::data)
        .map(Jsons::deserialize)
        .map(Jsons::jsonNode)
        .collect(Collectors.toList());
  }

  private List<JsonNode> retrieveRawDestinationRecords(final SchemaTableNamePair pair) throws Exception {
    final Database destination = getDestinationDatabase();
    final Set<SchemaTableNamePair> namePairs = listAllTables(destination);

    final String rawStreamName = String.format("_airbyte_raw_%s%s", OUTPUT_STREAM_PREFIX, pair.tableName.replace(".", "_"));
    final SchemaTableNamePair rawTablePair = new SchemaTableNamePair(OUTPUT_NAMESPACE_PREFIX + pair.schemaName, rawStreamName);
    assertTrue(namePairs.contains(rawTablePair), "can't find a non-normalized version (raw) of " + rawTablePair.getFullyQualifiedTableName());

    return retrieveDestinationRecords(destination, rawTablePair.getFullyQualifiedTableName());
  }

  private JsonNode getSourceDbConfig() {
    return getDbConfig(sourcePsql, false, false, Type.SOURCE);
  }

  private JsonNode getDestinationDbConfig() {
    return getDbConfig(destinationPsql, false, true, Type.DESTINATION);
  }

  private JsonNode getDestinationDbConfigWithHiddenPassword() {
    return getDbConfig(destinationPsql, true, true, Type.DESTINATION);
  }

  private JsonNode getDbConfig(final PostgreSQLContainer psql, final boolean hiddenPassword, final boolean withSchema, final Type connectorType) {
    try {
      final Map<Object, Object> dbConfig = (IS_KUBE && IS_GKE) ? GKEPostgresConfig.dbConfig(connectorType, hiddenPassword, withSchema)
          : localConfig(psql, hiddenPassword, withSchema);
      return Jsons.jsonNode(dbConfig);
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  private Map<Object, Object> localConfig(final PostgreSQLContainer psql, final boolean hiddenPassword, final boolean withSchema)
      throws UnknownHostException {
    final Map<Object, Object> dbConfig = new HashMap<>();
    // don't use psql.getHost() directly since the ip we need differs depending on environment
    if (IS_KUBE) {
      if (IS_MINIKUBE) {
        // used with minikube driver=none instance
        dbConfig.put("host", Inet4Address.getLocalHost().getHostAddress());
      } else {
        // used on a single node with docker driver
        dbConfig.put("host", "host.docker.internal");
      }
    } else if (IS_MAC) {
      dbConfig.put("host", "host.docker.internal");
    } else {
      dbConfig.put("host", "localhost");
    }

    if (hiddenPassword) {
      dbConfig.put("password", "**********");
    } else {
      dbConfig.put("password", psql.getPassword());
    }

    dbConfig.put("port", psql.getFirstMappedPort());
    dbConfig.put("database", psql.getDatabaseName());
    dbConfig.put("username", psql.getUsername());
    dbConfig.put("ssl", false);

    if (withSchema) {
      dbConfig.put("schema", "public");
    }
    return dbConfig;
  }

  private SourceDefinitionRead createE2eSourceDefinition() throws ApiException {
    return apiClient.getSourceDefinitionApi().createSourceDefinition(new SourceDefinitionCreate()
        .name("E2E Test Source")
        .dockerRepository("airbyte/source-e2e-test")
        .dockerImageTag(SOURCE_E2E_TEST_CONNECTOR_VERSION)
        .documentationUrl(URI.create("https://example.com")));
  }

  private DestinationDefinitionRead createE2eDestinationDefinition() throws ApiException {
    return apiClient.getDestinationDefinitionApi().createDestinationDefinition(new DestinationDefinitionCreate()
        .name("E2E Test Destination")
        .dockerRepository("airbyte/destination-e2e-test")
        .dockerImageTag(DESTINATION_E2E_TEST_CONNECTOR_VERSION)
        .documentationUrl(URI.create("https://example.com")));
  }

  private SourceRead createPostgresSource() throws ApiException {
    return createSource(
        "acceptanceTestDb-" + UUID.randomUUID(),
        workspaceId,
        getPostgresSourceDefinitionId(),
        getSourceDbConfig());
  }

  private SourceRead createSource(final String name, final UUID workspaceId, final UUID sourceDefId, final JsonNode sourceConfig)
      throws ApiException {
    final SourceRead source = apiClient.getSourceApi().createSource(new SourceCreate()
        .name(name)
        .sourceDefinitionId(sourceDefId)
        .workspaceId(workspaceId)
        .connectionConfiguration(sourceConfig));
    sourceIds.add(source.getSourceId());
    return source;
  }

  private UUID getPostgresSourceDefinitionId() throws ApiException {
    return apiClient.getSourceDefinitionApi().listSourceDefinitions().getSourceDefinitions()
        .stream()
        .filter(sourceRead -> sourceRead.getName().equalsIgnoreCase("postgres"))
        .findFirst()
        .orElseThrow()
        .getSourceDefinitionId();
  }

  private void clearSourceDbData() throws SQLException {
    final Database database = getSourceDatabase();
    final Set<SchemaTableNamePair> pairs = listAllTables(database);
    for (final SchemaTableNamePair pair : pairs) {
      database.query(context -> context.execute(String.format("DROP TABLE %s.%s", pair.schemaName, pair.tableName)));
    }
  }

  private void clearDestinationDbData() throws SQLException {
    final Database database = getDestinationDatabase();
    final Set<SchemaTableNamePair> pairs = listAllTables(database);
    for (final SchemaTableNamePair pair : pairs) {
      database.query(context -> context.execute(String.format("DROP TABLE %s.%s CASCADE", pair.schemaName, pair.tableName)));
    }
  }

  private void deleteSource(final UUID sourceId) throws ApiException {
    apiClient.getSourceApi().deleteSource(new SourceIdRequestBody().sourceId(sourceId));
  }

  private void disableConnection(final UUID connectionId) throws ApiException {
    final ConnectionRead connection = apiClient.getConnectionApi().getConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    final ConnectionUpdate connectionUpdate =
        new ConnectionUpdate()
            .prefix(connection.getPrefix())
            .connectionId(connectionId)
            .operationIds(connection.getOperationIds())
            .status(ConnectionStatus.DEPRECATED)
            .schedule(connection.getSchedule())
            .syncCatalog(connection.getSyncCatalog());
    apiClient.getConnectionApi().updateConnection(connectionUpdate);
  }

  private void deleteDestination(final UUID destinationId) throws ApiException {
    apiClient.getDestinationApi().deleteDestination(new DestinationIdRequestBody().destinationId(destinationId));
  }

  private void deleteOperation(final UUID destinationId) throws ApiException {
    apiClient.getOperationApi().deleteOperation(new OperationIdRequestBody().operationId(destinationId));
  }

  private static void waitForSuccessfulJob(final JobsApi jobsApi, final JobRead originalJob) throws InterruptedException, ApiException {
    final JobRead job = waitWhileJobHasStatus(jobsApi, originalJob, Sets.newHashSet(JobStatus.PENDING, JobStatus.RUNNING));

    if (!JobStatus.SUCCEEDED.equals(job.getStatus())) {
      // If a job failed during testing, show us why.
      final JobIdRequestBody id = new JobIdRequestBody();
      id.setId(originalJob.getId());
      for (final AttemptInfoRead attemptInfo : jobsApi.getJobInfo(id).getAttempts()) {
        LOGGER.warn("Unsuccessful job attempt " + attemptInfo.getAttempt().getId()
            + " with status " + job.getStatus() + " produced log output as follows: " + attemptInfo.getLogs().getLogLines());
      }
    }
    assertEquals(JobStatus.SUCCEEDED, job.getStatus());
  }

  private static JobRead waitWhileJobHasStatus(final JobsApi jobsApi, final JobRead originalJob, final Set<JobStatus> jobStatuses)
      throws InterruptedException, ApiException {
    return waitWhileJobHasStatus(jobsApi, originalJob, jobStatuses, Duration.ofMinutes(6));
  }

  @SuppressWarnings("BusyWait")
  private static JobRead waitWhileJobHasStatus(final JobsApi jobsApi,
                                               final JobRead originalJob,
                                               final Set<JobStatus> jobStatuses,
                                               final Duration maxWaitTime)
      throws InterruptedException, ApiException {
    JobRead job = originalJob;

    final Instant waitStart = Instant.now();
    while (jobStatuses.contains(job.getStatus())) {
      if (Duration.between(waitStart, Instant.now()).compareTo(maxWaitTime) > 0) {
        LOGGER.info("Max wait time of {} has been reached. Stopping wait.", maxWaitTime);
        break;
      }
      sleep(1000);

      job = jobsApi.getJobInfo(new JobIdRequestBody().id(job.getId())).getJob();
      LOGGER.info("waiting: job id: {} config type: {} status: {}", job.getId(), job.getConfigType(), job.getStatus());
    }
    return job;
  }

  @SuppressWarnings("BusyWait")
  private static ConnectionState waitForConnectionState(final AirbyteApiClient apiClient, final UUID connectionId)
      throws ApiException, InterruptedException {
    ConnectionState connectionState = apiClient.getConnectionApi().getState(new ConnectionIdRequestBody().connectionId(connectionId));
    int count = 0;
    while (count < 60 && (connectionState.getState() == null || connectionState.getState().isNull())) {
      LOGGER.info("fetching connection state. attempt: {}", count++);
      connectionState = apiClient.getConnectionApi().getState(new ConnectionIdRequestBody().connectionId(connectionId));
      sleep(1000);
    }
    return connectionState;
  }

  public enum Type {
    SOURCE,
    DESTINATION
  }

}
