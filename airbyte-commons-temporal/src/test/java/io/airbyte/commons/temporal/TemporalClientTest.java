/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal;

import static io.airbyte.commons.temporal.scheduling.ConnectionManagerWorkflow.NON_RUNNING_JOB_ID;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoMoreInteractions;
import static org.mockito.Mockito.when;

import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.temporal.TemporalClient.ManualOperationResult;
import io.airbyte.commons.temporal.scheduling.CheckConnectionWorkflow;
import io.airbyte.commons.temporal.scheduling.ConnectionManagerWorkflow;
import io.airbyte.commons.temporal.scheduling.ConnectionManagerWorkflow.JobInformation;
import io.airbyte.commons.temporal.scheduling.DiscoverCatalogWorkflow;
import io.airbyte.commons.temporal.scheduling.SpecWorkflow;
import io.airbyte.commons.temporal.scheduling.SyncWorkflow;
import io.airbyte.commons.temporal.scheduling.state.WorkflowState;
import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.FailureReason;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobDiscoverCatalogConfig;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.persistence.StreamResetPersistence;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.StreamDescriptor;
import io.temporal.api.enums.v1.WorkflowExecutionStatus;
import io.temporal.api.workflow.v1.WorkflowExecutionInfo;
import io.temporal.api.workflowservice.v1.DescribeWorkflowExecutionResponse;
import io.temporal.api.workflowservice.v1.WorkflowServiceGrpc.WorkflowServiceBlockingStub;
import io.temporal.client.BatchRequest;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowClientOptions;
import io.temporal.client.WorkflowOptions;
import io.temporal.client.WorkflowStub;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.workflow.Functions.Proc;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.Mockito;

@SuppressWarnings("PMD.JUnit5TestShouldBePackagePrivate")
public class TemporalClientTest {

  private static final UUID CONNECTION_ID = UUID.randomUUID();
  private static final UUID JOB_UUID = UUID.randomUUID();
  private static final long JOB_ID = 11L;
  private static final int ATTEMPT_ID = 21;
  private static final JobRunConfig JOB_RUN_CONFIG = new JobRunConfig()
      .withJobId(String.valueOf(JOB_ID))
      .withAttemptId((long) ATTEMPT_ID);
  private static final String IMAGE_NAME1 = "hms invincible";
  private static final String IMAGE_NAME2 = "hms defiant";
  private static final IntegrationLauncherConfig UUID_LAUNCHER_CONFIG = new IntegrationLauncherConfig()
      .withJobId(String.valueOf(JOB_UUID))
      .withAttemptId((long) ATTEMPT_ID)
      .withDockerImage(IMAGE_NAME1);
  private static final IntegrationLauncherConfig LAUNCHER_CONFIG = new IntegrationLauncherConfig()
      .withJobId(String.valueOf(JOB_ID))
      .withAttemptId((long) ATTEMPT_ID)
      .withDockerImage(IMAGE_NAME1);
  private static final String NAMESPACE = "namespace";
  private static final StreamDescriptor STREAM_DESCRIPTOR = new StreamDescriptor().withName("name");
  private static final String UNCHECKED = "unchecked";
  private static final String EXCEPTION_MESSAGE = "Force state exception to simulate workflow not running";

  private WorkflowClient workflowClient;
  private TemporalClient temporalClient;
  private Path logPath;
  private WorkflowServiceStubs workflowServiceStubs;
  private WorkflowServiceBlockingStub workflowServiceBlockingStub;
  private StreamResetPersistence streamResetPersistence;
  private ConnectionManagerUtils connectionManagerUtils;
  private StreamResetRecordsHelper streamResetRecordsHelper;
  private Path workspaceRoot;

  @BeforeEach
  void setup() throws IOException {
    workspaceRoot = Files.createTempDirectory(Path.of("/tmp"), "temporal_client_test");
    logPath = workspaceRoot.resolve(String.valueOf(JOB_ID)).resolve(String.valueOf(ATTEMPT_ID)).resolve(LogClientSingleton.LOG_FILENAME);
    workflowClient = mock(WorkflowClient.class);
    when(workflowClient.getOptions()).thenReturn(WorkflowClientOptions.newBuilder().setNamespace(NAMESPACE).build());
    workflowServiceStubs = mock(WorkflowServiceStubs.class);
    when(workflowClient.getWorkflowServiceStubs()).thenReturn(workflowServiceStubs);
    workflowServiceBlockingStub = mock(WorkflowServiceBlockingStub.class);
    when(workflowServiceStubs.blockingStub()).thenReturn(workflowServiceBlockingStub);
    streamResetPersistence = mock(StreamResetPersistence.class);
    mockWorkflowStatus(WorkflowExecutionStatus.WORKFLOW_EXECUTION_STATUS_RUNNING);
    connectionManagerUtils = spy(new ConnectionManagerUtils());
    streamResetRecordsHelper = mock(StreamResetRecordsHelper.class);
    temporalClient =
        spy(new TemporalClient(workspaceRoot, workflowClient, workflowServiceStubs, streamResetPersistence, connectionManagerUtils,
            streamResetRecordsHelper));
  }

  @Nested
  class RestartPerStatus {

    private ConnectionManagerUtils mConnectionManagerUtils;

    @BeforeEach
    void init() {
      mConnectionManagerUtils = mock(ConnectionManagerUtils.class);

      temporalClient = spy(
          new TemporalClient(workspaceRoot, workflowClient, workflowServiceStubs, streamResetPersistence, mConnectionManagerUtils,
              streamResetRecordsHelper));
    }

    @Test
    void testRestartFailed() {
      final ConnectionManagerWorkflow mConnectionManagerWorkflow = mock(ConnectionManagerWorkflow.class);

      when(workflowClient.newWorkflowStub(any(), anyString())).thenReturn(mConnectionManagerWorkflow);
      final UUID connectionId = UUID.fromString("ebbfdc4c-295b-48a0-844f-88551dfad3db");
      final Set<UUID> workflowIds = Set.of(connectionId);

      doReturn(workflowIds)
          .when(temporalClient).fetchClosedWorkflowsByStatus(WorkflowExecutionStatus.WORKFLOW_EXECUTION_STATUS_FAILED);
      doReturn(workflowIds)
          .when(temporalClient).filterOutRunningWorkspaceId(workflowIds);
      mockWorkflowStatus(WorkflowExecutionStatus.WORKFLOW_EXECUTION_STATUS_FAILED);
      temporalClient.restartClosedWorkflowByStatus(WorkflowExecutionStatus.WORKFLOW_EXECUTION_STATUS_FAILED);
      verify(mConnectionManagerUtils).safeTerminateWorkflow(eq(workflowClient), eq(connectionId),
          anyString());
      verify(mConnectionManagerUtils).startConnectionManagerNoSignal(eq(workflowClient), eq(connectionId));
    }

  }

  @Nested
  @DisplayName("Test execute method.")
  class ExecuteJob {

    @SuppressWarnings(UNCHECKED)
    @Test
    void testExecute() {
      final Supplier<String> supplier = mock(Supplier.class);
      when(supplier.get()).thenReturn("hello");

      final TemporalResponse<String> response = temporalClient.execute(JOB_RUN_CONFIG, supplier);

      assertNotNull(response);
      assertTrue(response.getOutput().isPresent());
      assertEquals("hello", response.getOutput().get());
      assertTrue(response.getMetadata().isSucceeded());
      assertEquals(logPath, response.getMetadata().getLogPath());
    }

    @SuppressWarnings(UNCHECKED)
    @Test
    void testExecuteWithException() {
      final Supplier<String> supplier = mock(Supplier.class);
      when(supplier.get()).thenThrow(IllegalStateException.class);

      final TemporalResponse<String> response = temporalClient.execute(JOB_RUN_CONFIG, supplier);

      assertNotNull(response);
      assertFalse(response.getOutput().isPresent());
      assertFalse(response.getMetadata().isSucceeded());
      assertEquals(logPath, response.getMetadata().getLogPath());
    }

    @Test
    void testExecuteWithConnectorJobFailure() {
      final Supplier<ConnectorJobOutput> supplier = mock(Supplier.class);
      final FailureReason mockFailureReason = mock(FailureReason.class);
      final ConnectorJobOutput connectorJobOutput = new ConnectorJobOutput()
          .withFailureReason(mockFailureReason);
      when(supplier.get()).thenReturn(connectorJobOutput);

      final TemporalResponse<ConnectorJobOutput> response = temporalClient.execute(JOB_RUN_CONFIG, supplier);

      assertNotNull(response);
      assertTrue(response.getOutput().isPresent());
      assertEquals(connectorJobOutput, response.getOutput().get());
      assertFalse(response.getMetadata().isSucceeded());
      assertEquals(logPath, response.getMetadata().getLogPath());
    }

  }

  @Nested
  @DisplayName("Test job creation for each configuration type.")
  class TestJobSubmission {

    @Test
    void testSubmitGetSpec() {
      final SpecWorkflow specWorkflow = mock(SpecWorkflow.class);
      when(workflowClient.newWorkflowStub(SpecWorkflow.class, TemporalWorkflowUtils.buildWorkflowOptions(TemporalJobType.GET_SPEC)))
          .thenReturn(specWorkflow);
      final JobGetSpecConfig getSpecConfig = new JobGetSpecConfig().withDockerImage(IMAGE_NAME1);

      temporalClient.submitGetSpec(JOB_UUID, ATTEMPT_ID, getSpecConfig);
      specWorkflow.run(JOB_RUN_CONFIG, UUID_LAUNCHER_CONFIG);
      verify(workflowClient).newWorkflowStub(SpecWorkflow.class, TemporalWorkflowUtils.buildWorkflowOptions(TemporalJobType.GET_SPEC));
    }

    @Test
    void testSubmitCheckConnection() {
      final CheckConnectionWorkflow checkConnectionWorkflow = mock(CheckConnectionWorkflow.class);
      when(
          workflowClient.newWorkflowStub(CheckConnectionWorkflow.class, TemporalWorkflowUtils.buildWorkflowOptions(TemporalJobType.CHECK_CONNECTION)))
              .thenReturn(checkConnectionWorkflow);
      final JobCheckConnectionConfig checkConnectionConfig = new JobCheckConnectionConfig()
          .withDockerImage(IMAGE_NAME1)
          .withConnectionConfiguration(Jsons.emptyObject());
      final StandardCheckConnectionInput input = new StandardCheckConnectionInput()
          .withConnectionConfiguration(checkConnectionConfig.getConnectionConfiguration());

      temporalClient.submitCheckConnection(JOB_UUID, ATTEMPT_ID, checkConnectionConfig);
      checkConnectionWorkflow.run(JOB_RUN_CONFIG, UUID_LAUNCHER_CONFIG, input);
      verify(workflowClient).newWorkflowStub(CheckConnectionWorkflow.class,
          TemporalWorkflowUtils.buildWorkflowOptions(TemporalJobType.CHECK_CONNECTION));
    }

    @Test
    void testSubmitDiscoverSchema() {
      final DiscoverCatalogWorkflow discoverCatalogWorkflow = mock(DiscoverCatalogWorkflow.class);
      when(workflowClient.newWorkflowStub(DiscoverCatalogWorkflow.class, TemporalWorkflowUtils.buildWorkflowOptions(TemporalJobType.DISCOVER_SCHEMA)))
          .thenReturn(discoverCatalogWorkflow);
      final JobDiscoverCatalogConfig checkConnectionConfig = new JobDiscoverCatalogConfig()
          .withDockerImage(IMAGE_NAME1)
          .withConnectionConfiguration(Jsons.emptyObject());
      final StandardDiscoverCatalogInput input = new StandardDiscoverCatalogInput()
          .withConnectionConfiguration(checkConnectionConfig.getConnectionConfiguration());

      temporalClient.submitDiscoverSchema(JOB_UUID, ATTEMPT_ID, checkConnectionConfig);
      discoverCatalogWorkflow.run(JOB_RUN_CONFIG, UUID_LAUNCHER_CONFIG, input);
      verify(workflowClient).newWorkflowStub(DiscoverCatalogWorkflow.class,
          TemporalWorkflowUtils.buildWorkflowOptions(TemporalJobType.DISCOVER_SCHEMA));
    }

    @Test
    void testSubmitSync() {
      final SyncWorkflow discoverCatalogWorkflow = mock(SyncWorkflow.class);
      when(workflowClient.newWorkflowStub(SyncWorkflow.class, TemporalWorkflowUtils.buildWorkflowOptions(TemporalJobType.SYNC)))
          .thenReturn(discoverCatalogWorkflow);
      final JobSyncConfig syncConfig = new JobSyncConfig()
          .withSourceDockerImage(IMAGE_NAME1)
          .withDestinationDockerImage(IMAGE_NAME2)
          .withSourceConfiguration(Jsons.emptyObject())
          .withDestinationConfiguration(Jsons.emptyObject())
          .withOperationSequence(List.of())
          .withConfiguredAirbyteCatalog(new ConfiguredAirbyteCatalog());
      final StandardSyncInput input = new StandardSyncInput()
          .withNamespaceDefinition(syncConfig.getNamespaceDefinition())
          .withNamespaceFormat(syncConfig.getNamespaceFormat())
          .withPrefix(syncConfig.getPrefix())
          .withSourceConfiguration(syncConfig.getSourceConfiguration())
          .withDestinationConfiguration(syncConfig.getDestinationConfiguration())
          .withOperationSequence(syncConfig.getOperationSequence())
          .withCatalog(syncConfig.getConfiguredAirbyteCatalog())
          .withState(syncConfig.getState());

      final IntegrationLauncherConfig destinationLauncherConfig = new IntegrationLauncherConfig()
          .withJobId(String.valueOf(JOB_ID))
          .withAttemptId((long) ATTEMPT_ID)
          .withDockerImage(IMAGE_NAME2);

      temporalClient.submitSync(JOB_ID, ATTEMPT_ID, syncConfig, CONNECTION_ID);
      discoverCatalogWorkflow.run(JOB_RUN_CONFIG, LAUNCHER_CONFIG, destinationLauncherConfig, input, CONNECTION_ID);
      verify(workflowClient).newWorkflowStub(SyncWorkflow.class, TemporalWorkflowUtils.buildWorkflowOptions(TemporalJobType.SYNC));
    }

  }

  @Nested
  @DisplayName("Test related to the migration to the new scheduler")
  class TestMigration {

    @DisplayName("Test that the migration is properly done if needed")
    @Test
    void migrateCalled() {
      final UUID nonMigratedId = UUID.randomUUID();
      final UUID migratedId = UUID.randomUUID();

      when(temporalClient.isInRunningWorkflowCache(connectionManagerUtils.getConnectionManagerName(nonMigratedId))).thenReturn(false);
      when(temporalClient.isInRunningWorkflowCache(connectionManagerUtils.getConnectionManagerName(migratedId))).thenReturn(true);

      doNothing()
          .when(temporalClient).refreshRunningWorkflow();
      final ConnectionManagerWorkflow mConnectionManagerWorkflow = mock(ConnectionManagerWorkflow.class);
      doReturn(mConnectionManagerWorkflow)
          .when(temporalClient).submitConnectionUpdaterAsync(nonMigratedId);

      temporalClient.migrateSyncIfNeeded(Sets.newHashSet(nonMigratedId, migratedId));

      verify(temporalClient, times(1)).submitConnectionUpdaterAsync(nonMigratedId);
      verify(temporalClient, times(0)).submitConnectionUpdaterAsync(migratedId);
    }

  }

  @Nested
  @DisplayName("Test delete connection method.")
  class ForceCancelConnection {

    @Test
    @SuppressWarnings(UNCHECKED)
    @DisplayName("Test delete connection method when workflow is in a running state.")
    void testforceCancelConnection() {
      final ConnectionManagerWorkflow mConnectionManagerWorkflow = mock(ConnectionManagerWorkflow.class);
      final WorkflowState mWorkflowState = mock(WorkflowState.class);
      when(mConnectionManagerWorkflow.getState()).thenReturn(mWorkflowState);
      when(mWorkflowState.isDeleted()).thenReturn(false);

      doReturn(true).when(temporalClient).isWorkflowReachable(any(UUID.class));
      when(workflowClient.newWorkflowStub(any(Class.class), anyString())).thenReturn(mConnectionManagerWorkflow);

      final JobSyncConfig syncConfig = new JobSyncConfig()
          .withSourceDockerImage(IMAGE_NAME1)
          .withDestinationDockerImage(IMAGE_NAME2)
          .withSourceConfiguration(Jsons.emptyObject())
          .withDestinationConfiguration(Jsons.emptyObject())
          .withOperationSequence(List.of())
          .withConfiguredAirbyteCatalog(new ConfiguredAirbyteCatalog());

      temporalClient.submitSync(JOB_ID, ATTEMPT_ID, syncConfig, CONNECTION_ID);
      temporalClient.forceDeleteWorkflow(CONNECTION_ID);

      verify(connectionManagerUtils).deleteWorkflowIfItExist(workflowClient, CONNECTION_ID);
    }

  }

  @Nested
  @DisplayName("Test update connection behavior")
  class UpdateConnection {

    @Test
    @SuppressWarnings(UNCHECKED)
    @DisplayName("Test update connection when workflow is running")
    void testUpdateConnection() {
      final ConnectionManagerWorkflow mConnectionManagerWorkflow = mock(ConnectionManagerWorkflow.class);
      final WorkflowState mWorkflowState = mock(WorkflowState.class);

      when(mWorkflowState.isRunning()).thenReturn(true);
      when(mWorkflowState.isDeleted()).thenReturn(false);
      when(mConnectionManagerWorkflow.getState()).thenReturn(mWorkflowState);
      when(workflowClient.newWorkflowStub(any(Class.class), any(String.class))).thenReturn(mConnectionManagerWorkflow);

      temporalClient.update(CONNECTION_ID);

      verify(mConnectionManagerWorkflow, Mockito.times(1)).connectionUpdated();
    }

    @Test
    @SuppressWarnings(UNCHECKED)
    @DisplayName("Test update connection method starts a new workflow when workflow is in an unexpected state")
    void testUpdateConnectionInUnexpectedState() {
      final ConnectionManagerWorkflow mConnectionManagerWorkflow = mock(ConnectionManagerWorkflow.class);

      when(mConnectionManagerWorkflow.getState()).thenThrow(new IllegalStateException(EXCEPTION_MESSAGE));
      when(workflowClient.newWorkflowStub(any(Class.class), any(String.class))).thenReturn(mConnectionManagerWorkflow);
      doReturn(mConnectionManagerWorkflow).when(temporalClient).submitConnectionUpdaterAsync(CONNECTION_ID);

      final WorkflowStub untypedWorkflowStub = mock(WorkflowStub.class);
      when(workflowClient.newUntypedWorkflowStub(anyString())).thenReturn(untypedWorkflowStub);

      temporalClient.update(CONNECTION_ID);

      // this is only called when updating an existing workflow
      verify(mConnectionManagerWorkflow, Mockito.never()).connectionUpdated();

      verify(untypedWorkflowStub, Mockito.times(1)).terminate(anyString());
      verify(temporalClient, Mockito.times(1)).submitConnectionUpdaterAsync(CONNECTION_ID);
    }

    @Test
    @SuppressWarnings(UNCHECKED)
    @DisplayName("Test update connection method does nothing when connection is deleted")
    void testUpdateConnectionDeletedWorkflow() {
      final ConnectionManagerWorkflow mConnectionManagerWorkflow = mock(ConnectionManagerWorkflow.class);
      final WorkflowState mWorkflowState = mock(WorkflowState.class);
      when(mConnectionManagerWorkflow.getState()).thenReturn(mWorkflowState);
      when(mWorkflowState.isDeleted()).thenReturn(true);
      when(workflowClient.newWorkflowStub(any(), anyString())).thenReturn(mConnectionManagerWorkflow);
      mockWorkflowStatus(WorkflowExecutionStatus.WORKFLOW_EXECUTION_STATUS_COMPLETED);

      temporalClient.update(CONNECTION_ID);

      // this is only called when updating an existing workflow
      verify(mConnectionManagerWorkflow, Mockito.never()).connectionUpdated();
      verify(temporalClient).update(CONNECTION_ID);
      verifyNoMoreInteractions(temporalClient);
    }

  }

  @Nested
  @DisplayName("Test manual sync behavior")
  class ManualSync {

    @Test
    @DisplayName("Test startNewManualSync successful")
    void testStartNewManualSyncSuccess() {
      final ConnectionManagerWorkflow mConnectionManagerWorkflow = mock(ConnectionManagerWorkflow.class);
      final WorkflowState mWorkflowState = mock(WorkflowState.class);
      when(mConnectionManagerWorkflow.getState()).thenReturn(mWorkflowState);
      when(mWorkflowState.isDeleted()).thenReturn(false);
      when(mWorkflowState.isRunning()).thenReturn(false).thenReturn(true);
      when(mConnectionManagerWorkflow.getJobInformation()).thenReturn(new JobInformation(JOB_ID, ATTEMPT_ID));
      when(workflowClient.newWorkflowStub(any(), anyString())).thenReturn(mConnectionManagerWorkflow);

      final ManualOperationResult result = temporalClient.startNewManualSync(CONNECTION_ID);

      assertTrue(result.getJobId().isPresent());
      assertEquals(JOB_ID, result.getJobId().get());
      assertFalse(result.getFailingReason().isPresent());
      verify(mConnectionManagerWorkflow).submitManualSync();
    }

    @Test
    @DisplayName("Test startNewManualSync fails if job is already running")
    void testStartNewManualSyncAlreadyRunning() {
      final ConnectionManagerWorkflow mConnectionManagerWorkflow = mock(ConnectionManagerWorkflow.class);
      final WorkflowState mWorkflowState = mock(WorkflowState.class);
      when(mConnectionManagerWorkflow.getState()).thenReturn(mWorkflowState);
      when(mWorkflowState.isDeleted()).thenReturn(false);
      when(mWorkflowState.isRunning()).thenReturn(true);
      when(mConnectionManagerWorkflow.getJobInformation()).thenReturn(new JobInformation(JOB_ID, ATTEMPT_ID));
      when(workflowClient.newWorkflowStub(any(), anyString())).thenReturn(mConnectionManagerWorkflow);

      final ManualOperationResult result = temporalClient.startNewManualSync(CONNECTION_ID);

      assertFalse(result.getJobId().isPresent());
      assertTrue(result.getFailingReason().isPresent());
      verify(mConnectionManagerWorkflow, times(0)).submitManualSync();
    }

    @Test
    @DisplayName("Test startNewManualSync repairs the workflow if it is in a bad state")
    void testStartNewManualSyncRepairsBadWorkflowState() {
      final ConnectionManagerWorkflow mTerminatedConnectionManagerWorkflow = mock(ConnectionManagerWorkflow.class);
      when(mTerminatedConnectionManagerWorkflow.getState())
          .thenThrow(new IllegalStateException(EXCEPTION_MESSAGE));
      when(mTerminatedConnectionManagerWorkflow.getJobInformation()).thenReturn(new JobInformation(JOB_ID, ATTEMPT_ID));

      final ConnectionManagerWorkflow mNewConnectionManagerWorkflow = mock(ConnectionManagerWorkflow.class);
      final WorkflowState mWorkflowState = mock(WorkflowState.class);
      when(mNewConnectionManagerWorkflow.getState()).thenReturn(mWorkflowState);
      when(mWorkflowState.isDeleted()).thenReturn(false);
      when(mWorkflowState.isRunning()).thenReturn(false).thenReturn(true);
      when(mNewConnectionManagerWorkflow.getJobInformation()).thenReturn(new JobInformation(JOB_ID, ATTEMPT_ID));
      when(workflowClient.newWorkflowStub(any(Class.class), any(WorkflowOptions.class))).thenReturn(mNewConnectionManagerWorkflow);
      final BatchRequest mBatchRequest = mock(BatchRequest.class);
      when(workflowClient.newSignalWithStartRequest()).thenReturn(mBatchRequest);

      when(workflowClient.newWorkflowStub(any(), anyString())).thenReturn(mTerminatedConnectionManagerWorkflow, mTerminatedConnectionManagerWorkflow,
          mNewConnectionManagerWorkflow);

      final ManualOperationResult result = temporalClient.startNewManualSync(CONNECTION_ID);

      assertTrue(result.getJobId().isPresent());
      assertEquals(JOB_ID, result.getJobId().get());
      assertFalse(result.getFailingReason().isPresent());
      verify(workflowClient).signalWithStart(mBatchRequest);

      // Verify that the submitManualSync signal was passed to the batch request by capturing the
      // argument,
      // executing the signal, and verifying that the desired signal was executed
      final ArgumentCaptor<Proc> batchRequestAddArgCaptor = ArgumentCaptor.forClass(Proc.class);
      verify(mBatchRequest).add(batchRequestAddArgCaptor.capture());
      final Proc signal = batchRequestAddArgCaptor.getValue();
      signal.apply();
      verify(mNewConnectionManagerWorkflow).submitManualSync();
    }

    @Test
    @SuppressWarnings(UNCHECKED)
    @DisplayName("Test startNewManualSync returns a failure reason when connection is deleted")
    void testStartNewManualSyncDeletedWorkflow() {
      final ConnectionManagerWorkflow mConnectionManagerWorkflow = mock(ConnectionManagerWorkflow.class);
      final WorkflowState mWorkflowState = mock(WorkflowState.class);
      when(mConnectionManagerWorkflow.getState()).thenReturn(mWorkflowState);
      when(mWorkflowState.isDeleted()).thenReturn(true);
      when(workflowClient.newWorkflowStub(any(), anyString())).thenReturn(mConnectionManagerWorkflow);
      mockWorkflowStatus(WorkflowExecutionStatus.WORKFLOW_EXECUTION_STATUS_COMPLETED);

      final ManualOperationResult result = temporalClient.startNewManualSync(CONNECTION_ID);

      // this is only called when updating an existing workflow
      assertFalse(result.getJobId().isPresent());
      assertTrue(result.getFailingReason().isPresent());
      verify(mConnectionManagerWorkflow, times(0)).submitManualSync();
    }

  }

  @Nested
  @DisplayName("Test cancellation behavior")
  class Cancellation {

    @Test
    @DisplayName("Test startNewCancellation successful")
    void testStartNewCancellationSuccess() {
      final ConnectionManagerWorkflow mConnectionManagerWorkflow = mock(ConnectionManagerWorkflow.class);
      final WorkflowState mWorkflowState = mock(WorkflowState.class);
      when(mConnectionManagerWorkflow.getState()).thenReturn(mWorkflowState);
      when(mWorkflowState.isDeleted()).thenReturn(false);
      when(mWorkflowState.isRunning()).thenReturn(true).thenReturn(false);
      when(mConnectionManagerWorkflow.getJobInformation()).thenReturn(new JobInformation(JOB_ID, ATTEMPT_ID));
      when(workflowClient.newWorkflowStub(any(), anyString())).thenReturn(mConnectionManagerWorkflow);

      final ManualOperationResult result = temporalClient.startNewCancellation(CONNECTION_ID);

      assertTrue(result.getJobId().isPresent());
      assertEquals(JOB_ID, result.getJobId().get());
      assertFalse(result.getFailingReason().isPresent());
      verify(mConnectionManagerWorkflow).cancelJob();
      verify(streamResetRecordsHelper).deleteStreamResetRecordsForJob(JOB_ID, CONNECTION_ID);
    }

    @Test
    @DisplayName("Test startNewCancellation repairs the workflow if it is in a bad state")
    void testStartNewCancellationRepairsBadWorkflowState() {
      final ConnectionManagerWorkflow mTerminatedConnectionManagerWorkflow = mock(ConnectionManagerWorkflow.class);
      when(mTerminatedConnectionManagerWorkflow.getState())
          .thenThrow(new IllegalStateException(EXCEPTION_MESSAGE));
      when(mTerminatedConnectionManagerWorkflow.getJobInformation()).thenReturn(new JobInformation(JOB_ID, ATTEMPT_ID));

      final ConnectionManagerWorkflow mNewConnectionManagerWorkflow = mock(ConnectionManagerWorkflow.class);
      final WorkflowState mWorkflowState = mock(WorkflowState.class);
      when(mNewConnectionManagerWorkflow.getState()).thenReturn(mWorkflowState);
      when(mWorkflowState.isDeleted()).thenReturn(false);
      when(mWorkflowState.isRunning()).thenReturn(true).thenReturn(false);
      when(mNewConnectionManagerWorkflow.getJobInformation()).thenReturn(new JobInformation(JOB_ID, ATTEMPT_ID));
      when(workflowClient.newWorkflowStub(any(Class.class), any(WorkflowOptions.class))).thenReturn(mNewConnectionManagerWorkflow);
      final BatchRequest mBatchRequest = mock(BatchRequest.class);
      when(workflowClient.newSignalWithStartRequest()).thenReturn(mBatchRequest);

      when(workflowClient.newWorkflowStub(any(), anyString())).thenReturn(mTerminatedConnectionManagerWorkflow, mTerminatedConnectionManagerWorkflow,
          mNewConnectionManagerWorkflow);

      final ManualOperationResult result = temporalClient.startNewCancellation(CONNECTION_ID);

      assertTrue(result.getJobId().isPresent());
      assertEquals(NON_RUNNING_JOB_ID, result.getJobId().get());
      assertFalse(result.getFailingReason().isPresent());
      verify(workflowClient).signalWithStart(mBatchRequest);

      // Verify that the cancelJob signal was passed to the batch request by capturing the argument,
      // executing the signal, and verifying that the desired signal was executed
      final ArgumentCaptor<Proc> batchRequestAddArgCaptor = ArgumentCaptor.forClass(Proc.class);
      verify(mBatchRequest).add(batchRequestAddArgCaptor.capture());
      final Proc signal = batchRequestAddArgCaptor.getValue();
      signal.apply();
      verify(mNewConnectionManagerWorkflow).cancelJob();
    }

    @Test
    @SuppressWarnings(UNCHECKED)
    @DisplayName("Test startNewCancellation returns a failure reason when connection is deleted")
    void testStartNewCancellationDeletedWorkflow() {
      final ConnectionManagerWorkflow mConnectionManagerWorkflow = mock(ConnectionManagerWorkflow.class);
      final WorkflowState mWorkflowState = mock(WorkflowState.class);
      when(mConnectionManagerWorkflow.getState()).thenReturn(mWorkflowState);
      when(mWorkflowState.isDeleted()).thenReturn(true);
      when(workflowClient.newWorkflowStub(any(), anyString())).thenReturn(mConnectionManagerWorkflow);
      mockWorkflowStatus(WorkflowExecutionStatus.WORKFLOW_EXECUTION_STATUS_COMPLETED);

      final ManualOperationResult result = temporalClient.startNewCancellation(CONNECTION_ID);

      // this is only called when updating an existing workflow
      assertFalse(result.getJobId().isPresent());
      assertTrue(result.getFailingReason().isPresent());
      verify(mConnectionManagerWorkflow, times(0)).cancelJob();
    }

  }

  @Nested
  @DisplayName("Test reset connection behavior")
  class ResetConnection {

    @Test
    @DisplayName("Test resetConnection successful")
    void testResetConnectionSuccess() throws IOException {
      final ConnectionManagerWorkflow mConnectionManagerWorkflow = mock(ConnectionManagerWorkflow.class);
      final WorkflowState mWorkflowState = mock(WorkflowState.class);
      when(mConnectionManagerWorkflow.getState()).thenReturn(mWorkflowState);
      when(mWorkflowState.isDeleted()).thenReturn(false);
      when(mWorkflowState.isRunning()).thenReturn(false);
      final long jobId1 = 1;
      final long jobId2 = 2;
      when(mConnectionManagerWorkflow.getJobInformation()).thenReturn(
          new JobInformation(jobId1, 0),
          new JobInformation(jobId1, 0),
          new JobInformation(NON_RUNNING_JOB_ID, 0),
          new JobInformation(NON_RUNNING_JOB_ID, 0),
          new JobInformation(jobId2, 0),
          new JobInformation(jobId2, 0));
      when(workflowClient.newWorkflowStub(any(), anyString())).thenReturn(mConnectionManagerWorkflow);

      final List<StreamDescriptor> streamsToReset = List.of(STREAM_DESCRIPTOR);
      final ManualOperationResult result = temporalClient.resetConnection(CONNECTION_ID, streamsToReset, false);

      verify(streamResetPersistence).createStreamResets(CONNECTION_ID, streamsToReset);

      assertTrue(result.getJobId().isPresent());
      assertEquals(jobId2, result.getJobId().get());
      assertFalse(result.getFailingReason().isPresent());
      verify(mConnectionManagerWorkflow).resetConnection();
    }

    @Test
    @DisplayName("Test resetConnection successful")
    void testResetConnectionSuccessAndContinue() throws IOException {
      final ConnectionManagerWorkflow mConnectionManagerWorkflow = mock(ConnectionManagerWorkflow.class);
      final WorkflowState mWorkflowState = mock(WorkflowState.class);
      when(mConnectionManagerWorkflow.getState()).thenReturn(mWorkflowState);
      when(mWorkflowState.isDeleted()).thenReturn(false);
      when(mWorkflowState.isRunning()).thenReturn(false);
      final long jobId1 = 1;
      final long jobId2 = 2;
      when(mConnectionManagerWorkflow.getJobInformation()).thenReturn(
          new JobInformation(jobId1, 0),
          new JobInformation(jobId1, 0),
          new JobInformation(NON_RUNNING_JOB_ID, 0),
          new JobInformation(NON_RUNNING_JOB_ID, 0),
          new JobInformation(jobId2, 0),
          new JobInformation(jobId2, 0));
      when(workflowClient.newWorkflowStub(any(), anyString())).thenReturn(mConnectionManagerWorkflow);

      final List<StreamDescriptor> streamsToReset = List.of(STREAM_DESCRIPTOR);
      final ManualOperationResult result = temporalClient.resetConnection(CONNECTION_ID, streamsToReset, true);

      verify(streamResetPersistence).createStreamResets(CONNECTION_ID, streamsToReset);

      assertTrue(result.getJobId().isPresent());
      assertEquals(jobId2, result.getJobId().get());
      assertFalse(result.getFailingReason().isPresent());
      verify(mConnectionManagerWorkflow).resetConnectionAndSkipNextScheduling();
    }

    @Test
    @DisplayName("Test resetConnection repairs the workflow if it is in a bad state")
    void testResetConnectionRepairsBadWorkflowState() throws IOException {
      final ConnectionManagerWorkflow mTerminatedConnectionManagerWorkflow = mock(ConnectionManagerWorkflow.class);
      when(mTerminatedConnectionManagerWorkflow.getState())
          .thenThrow(new IllegalStateException(EXCEPTION_MESSAGE));
      when(mTerminatedConnectionManagerWorkflow.getJobInformation()).thenReturn(new JobInformation(JOB_ID, ATTEMPT_ID));

      final ConnectionManagerWorkflow mNewConnectionManagerWorkflow = mock(ConnectionManagerWorkflow.class);
      final WorkflowState mWorkflowState = mock(WorkflowState.class);
      when(mNewConnectionManagerWorkflow.getState()).thenReturn(mWorkflowState);
      when(mWorkflowState.isDeleted()).thenReturn(false);
      when(mWorkflowState.isRunning()).thenReturn(false);
      when(mNewConnectionManagerWorkflow.getJobInformation()).thenReturn(
          new JobInformation(NON_RUNNING_JOB_ID, 0),
          new JobInformation(NON_RUNNING_JOB_ID, 0),
          new JobInformation(JOB_ID, 0),
          new JobInformation(JOB_ID, 0));
      when(workflowClient.newWorkflowStub(any(Class.class), any(WorkflowOptions.class))).thenReturn(mNewConnectionManagerWorkflow);
      final BatchRequest mBatchRequest = mock(BatchRequest.class);
      when(workflowClient.newSignalWithStartRequest()).thenReturn(mBatchRequest);

      when(workflowClient.newWorkflowStub(any(), anyString())).thenReturn(mTerminatedConnectionManagerWorkflow, mTerminatedConnectionManagerWorkflow,
          mNewConnectionManagerWorkflow);

      final List<StreamDescriptor> streamsToReset = List.of(STREAM_DESCRIPTOR);
      final ManualOperationResult result = temporalClient.resetConnection(CONNECTION_ID, streamsToReset, false);

      verify(streamResetPersistence).createStreamResets(CONNECTION_ID, streamsToReset);

      assertTrue(result.getJobId().isPresent());
      assertEquals(JOB_ID, result.getJobId().get());
      assertFalse(result.getFailingReason().isPresent());
      verify(workflowClient).signalWithStart(mBatchRequest);

      // Verify that the resetConnection signal was passed to the batch request by capturing the argument,
      // executing the signal, and verifying that the desired signal was executed
      final ArgumentCaptor<Proc> batchRequestAddArgCaptor = ArgumentCaptor.forClass(Proc.class);
      verify(mBatchRequest).add(batchRequestAddArgCaptor.capture());
      final Proc signal = batchRequestAddArgCaptor.getValue();
      signal.apply();
      verify(mNewConnectionManagerWorkflow).resetConnection();
    }

    @Test
    @SuppressWarnings(UNCHECKED)
    @DisplayName("Test resetConnection returns a failure reason when connection is deleted")
    void testResetConnectionDeletedWorkflow() throws IOException {
      final ConnectionManagerWorkflow mConnectionManagerWorkflow = mock(ConnectionManagerWorkflow.class);
      final WorkflowState mWorkflowState = mock(WorkflowState.class);
      when(mConnectionManagerWorkflow.getState()).thenReturn(mWorkflowState);
      when(mWorkflowState.isDeleted()).thenReturn(true);
      when(workflowClient.newWorkflowStub(any(), anyString())).thenReturn(mConnectionManagerWorkflow);
      mockWorkflowStatus(WorkflowExecutionStatus.WORKFLOW_EXECUTION_STATUS_COMPLETED);

      final List<StreamDescriptor> streamsToReset = List.of(STREAM_DESCRIPTOR);
      final ManualOperationResult result = temporalClient.resetConnection(CONNECTION_ID, streamsToReset, false);

      verify(streamResetPersistence).createStreamResets(CONNECTION_ID, streamsToReset);

      // this is only called when updating an existing workflow
      assertFalse(result.getJobId().isPresent());
      assertTrue(result.getFailingReason().isPresent());
      verify(mConnectionManagerWorkflow, times(0)).resetConnection();
    }

  }

  @Test
  @DisplayName("Test manual operation on completed workflow causes a restart")
  void testManualOperationOnCompletedWorkflow() {
    final ConnectionManagerWorkflow mConnectionManagerWorkflow = mock(ConnectionManagerWorkflow.class);
    final WorkflowState mWorkflowState = mock(WorkflowState.class);
    when(mConnectionManagerWorkflow.getState()).thenReturn(mWorkflowState);
    when(mWorkflowState.isDeleted()).thenReturn(false);
    when(workflowServiceBlockingStub.describeWorkflowExecution(any()))
        .thenReturn(DescribeWorkflowExecutionResponse.newBuilder().setWorkflowExecutionInfo(
            WorkflowExecutionInfo.newBuilder().setStatus(WorkflowExecutionStatus.WORKFLOW_EXECUTION_STATUS_COMPLETED).buildPartial()).build())
        .thenReturn(DescribeWorkflowExecutionResponse.newBuilder().setWorkflowExecutionInfo(
            WorkflowExecutionInfo.newBuilder().setStatus(WorkflowExecutionStatus.WORKFLOW_EXECUTION_STATUS_RUNNING).buildPartial()).build());

    final ConnectionManagerWorkflow mNewConnectionManagerWorkflow = mock(ConnectionManagerWorkflow.class);
    final WorkflowState mNewWorkflowState = mock(WorkflowState.class);
    when(mNewConnectionManagerWorkflow.getState()).thenReturn(mNewWorkflowState);
    when(mNewWorkflowState.isRunning()).thenReturn(false).thenReturn(true);
    when(mNewConnectionManagerWorkflow.getJobInformation()).thenReturn(new JobInformation(JOB_ID, ATTEMPT_ID));
    when(workflowClient.newWorkflowStub(any(Class.class), any(WorkflowOptions.class))).thenReturn(mNewConnectionManagerWorkflow);
    final BatchRequest mBatchRequest = mock(BatchRequest.class);
    when(workflowClient.newSignalWithStartRequest()).thenReturn(mBatchRequest);

    when(workflowClient.newWorkflowStub(any(), anyString())).thenReturn(mConnectionManagerWorkflow, mConnectionManagerWorkflow,
        mNewConnectionManagerWorkflow);

    final WorkflowStub mWorkflowStub = mock(WorkflowStub.class);
    when(workflowClient.newUntypedWorkflowStub(anyString())).thenReturn(mWorkflowStub);

    final ManualOperationResult result = temporalClient.startNewManualSync(CONNECTION_ID);

    assertTrue(result.getJobId().isPresent());
    assertEquals(JOB_ID, result.getJobId().get());
    assertFalse(result.getFailingReason().isPresent());
    verify(workflowClient).signalWithStart(mBatchRequest);
    verify(mWorkflowStub).terminate(anyString());

    // Verify that the submitManualSync signal was passed to the batch request by capturing the
    // argument,
    // executing the signal, and verifying that the desired signal was executed
    final ArgumentCaptor<Proc> batchRequestAddArgCaptor = ArgumentCaptor.forClass(Proc.class);
    verify(mBatchRequest).add(batchRequestAddArgCaptor.capture());
    final Proc signal = batchRequestAddArgCaptor.getValue();
    signal.apply();
    verify(mNewConnectionManagerWorkflow).submitManualSync();
  }

  private void mockWorkflowStatus(final WorkflowExecutionStatus status) {
    when(workflowServiceBlockingStub.describeWorkflowExecution(any())).thenReturn(
        DescribeWorkflowExecutionResponse.newBuilder().setWorkflowExecutionInfo(
            WorkflowExecutionInfo.newBuilder().setStatus(status).buildPartial()).build());
  }

}
