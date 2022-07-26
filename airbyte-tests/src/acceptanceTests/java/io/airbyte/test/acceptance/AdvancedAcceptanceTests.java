/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.acceptance;

import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.COLUMN_ID;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.SOURCE_PASSWORD;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.waitForConnectionState;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.waitForSuccessfulJob;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.waitWhileJobHasStatus;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.invoker.generated.ApiClient;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.AirbyteCatalog;
import io.airbyte.api.client.model.generated.AirbyteStream;
import io.airbyte.api.client.model.generated.AttemptInfoRead;
import io.airbyte.api.client.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.client.model.generated.ConnectionState;
import io.airbyte.api.client.model.generated.DestinationDefinitionIdRequestBody;
import io.airbyte.api.client.model.generated.DestinationDefinitionRead;
import io.airbyte.api.client.model.generated.DestinationRead;
import io.airbyte.api.client.model.generated.DestinationSyncMode;
import io.airbyte.api.client.model.generated.JobIdRequestBody;
import io.airbyte.api.client.model.generated.JobInfoRead;
import io.airbyte.api.client.model.generated.JobRead;
import io.airbyte.api.client.model.generated.JobStatus;
import io.airbyte.api.client.model.generated.LogType;
import io.airbyte.api.client.model.generated.LogsRequestBody;
import io.airbyte.api.client.model.generated.SourceDefinitionIdRequestBody;
import io.airbyte.api.client.model.generated.SourceDefinitionRead;
import io.airbyte.api.client.model.generated.SourceRead;
import io.airbyte.api.client.model.generated.SyncMode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.MoreBooleans;
import io.airbyte.container_orchestrator.ContainerOrchestratorApp;
import io.airbyte.test.utils.AirbyteAcceptanceTestHarness;
import io.fabric8.kubernetes.client.KubernetesClient;
import java.io.IOException;
import java.net.URISyntaxException;
import java.nio.charset.Charset;
import java.sql.SQLException;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
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

  private static AirbyteAcceptanceTestHarness testHarness;
  private static AirbyteApiClient apiClient;
  private static UUID workspaceId;
  private static KubernetesClient kubernetesClient;

  @SuppressWarnings("UnstableApiUsage")
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
    kubernetesClient = testHarness.getKubernetesClient();
  }

  @AfterAll
  public static void end() {
    testHarness.stopDbAndContainers();
  }

  @BeforeEach
  public void setup() throws URISyntaxException, IOException, SQLException {
    testHarness.setup();
  }

  @AfterEach
  public void tearDown() {
    testHarness.cleanup();
  }

  @RetryingTest(3)
  @Order(1)
  public void testManualSync() throws Exception {
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

  @RetryingTest(3)
  @Order(2)
  public void testCheckpointing() throws Exception {
    final SourceDefinitionRead sourceDefinition = testHarness.createE2eSourceDefinition();
    final DestinationDefinitionRead destinationDefinition = testHarness.createE2eDestinationDefinition();

    final SourceRead source = testHarness.createSource(
        "E2E Test Source -" + UUID.randomUUID(),
        workspaceId,
        sourceDefinition.getSourceDefinitionId(),
        Jsons.jsonNode(ImmutableMap.builder()
            .put("type", "EXCEPTION_AFTER_N")
            .put("throw_after_n_records", 100)
            .build()));

    final DestinationRead destination = testHarness.createDestination(
        "E2E Test Destination -" + UUID.randomUUID(),
        workspaceId,
        destinationDefinition.getDestinationDefinitionId(),
        Jsons.jsonNode(ImmutableMap.of("type", "SILENT")));

    final String connectionName = "test-connection";
    final UUID sourceId = source.getSourceId();
    final UUID destinationId = destination.getDestinationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
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
        testHarness.createConnection(connectionName, sourceId, destinationId, Collections.emptyList(), catalog, null)
            .getConnectionId();
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
    final SourceDefinitionRead sourceDefinition = testHarness.createE2eSourceDefinition();
    final DestinationDefinitionRead destinationDefinition = testHarness.createE2eDestinationDefinition();

    final SourceRead source = testHarness.createSource(
        "E2E Test Source -" + UUID.randomUUID(),
        workspaceId,
        sourceDefinition.getSourceDefinitionId(),
        Jsons.jsonNode(ImmutableMap.builder()
            .put("type", "INFINITE_FEED")
            .put("max_records", 5000)
            .build()));

    final DestinationRead destination = testHarness.createDestination(
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
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);

    final UUID connectionId =
        testHarness.createConnection(connectionName, sourceId, destinationId, Collections.emptyList(), catalog, null)
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
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createDestination().getDestinationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));

    for (final var input : List.of("KILL_BOTH_NON_SYNC_SLIGHTLY_FIRST", "KILL_ONLY_SYNC", "KILL_ONLY_NON_SYNC")) {
      LOGGER.info("Checking " + input);

      final UUID connectionId =
          testHarness.createConnection(connectionName, sourceId, destinationId, List.of(), catalog, null).getConnectionId();

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
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));

    LOGGER.info("Creating connection...");
    final UUID connectionId =
        testHarness.createConnection(connectionName, sourceId, destinationId, List.of(operationId), catalog, null).getConnectionId();

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
    final UUID sourceId = testHarness.createPostgresSource().getSourceId();
    final UUID destinationId = testHarness.createDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));

    LOGGER.info("Creating connection...");
    final UUID connectionId =
        testHarness.createConnection(connectionName, sourceId, destinationId, List.of(operationId), catalog, null).getConnectionId();

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

}
