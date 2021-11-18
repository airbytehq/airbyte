/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;
import static org.mockito.Mockito.verify;

import io.airbyte.config.*;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.TestConfigHelpers;
import io.airbyte.workers.temporal.TemporalJobType;
import io.temporal.api.common.v1.WorkflowExecution;
import io.temporal.api.workflowservice.v1.RequestCancelWorkflowExecutionRequest;
import io.temporal.api.workflowservice.v1.WorkflowServiceGrpc;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowFailedException;
import io.temporal.client.WorkflowOptions;
import io.temporal.testing.TestWorkflowEnvironment;
import io.temporal.worker.Worker;
import java.util.UUID;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ReplicationOrchestratorWorkflowTest {

  // TEMPORAL

  private TestWorkflowEnvironment testEnv;
  private Worker replicationOrchestratorWorker;
  private WorkflowClient client;
  private ReplicationActivityImpl replicationActivity;

  // AIRBYTE CONFIGURATION
  private static final long JOB_ID = 11L;
  private static final int ATTEMPT_ID = 21;
  private static final JobRunConfig JOB_RUN_CONFIG = new JobRunConfig()
      .withJobId(String.valueOf(JOB_ID))
      .withAttemptId((long) ATTEMPT_ID);
  private static final String IMAGE_NAME1 = "hms invincible";
  private static final String IMAGE_NAME2 = "hms defiant";
  private static final IntegrationLauncherConfig SOURCE_LAUNCHER_CONFIG = new IntegrationLauncherConfig()
      .withJobId(String.valueOf(JOB_ID))
      .withAttemptId((long) ATTEMPT_ID)
      .withDockerImage(IMAGE_NAME1);
  private static final IntegrationLauncherConfig DESTINATION_LAUNCHER_CONFIG = new IntegrationLauncherConfig()
      .withJobId(String.valueOf(JOB_ID))
      .withAttemptId((long) ATTEMPT_ID)
      .withDockerImage(IMAGE_NAME2);

  private StandardSync sync;
  private StandardSyncInput syncInput;

  private StandardSyncOutput replicationSuccessOutput;

  @BeforeEach
  public void setUp() {
    testEnv = TestWorkflowEnvironment.newInstance();

    replicationOrchestratorWorker = testEnv.newWorker(TemporalJobType.REPLICATION_ORCHESTRATOR.name());
    replicationOrchestratorWorker.registerWorkflowImplementationTypes(ReplicationOrchestratorWorkflowImpl.class);

    client = testEnv.getWorkflowClient();

    final ImmutablePair<StandardSync, StandardSyncInput> syncPair = TestConfigHelpers.createSyncConfig();
    sync = syncPair.getKey();
    syncInput = syncPair.getValue();
    replicationSuccessOutput = new StandardSyncOutput().withOutputCatalog(syncInput.getCatalog());

    replicationActivity = mock(ReplicationActivityImpl.class);
  }

  // bundle up all the temporal worker setup / execution into one method.
  private StandardSyncOutput execute() {
    replicationOrchestratorWorker.registerActivitiesImplementations(replicationActivity);
    testEnv.start();
    final ReplicationOrchestratorWorkflow workflow = client.newWorkflowStub(ReplicationOrchestratorWorkflow.class,
        WorkflowOptions.newBuilder().setTaskQueue(TemporalJobType.REPLICATION_ORCHESTRATOR.name()).build());

    return workflow.run(JOB_RUN_CONFIG, SOURCE_LAUNCHER_CONFIG, DESTINATION_LAUNCHER_CONFIG, syncInput, sync.getConnectionId());
  }

  @Test
  void testSuccess() {
    doReturn(replicationSuccessOutput).when(replicationActivity).replicate(
        JOB_RUN_CONFIG,
        SOURCE_LAUNCHER_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        syncInput,
        sync.getConnectionId());

    final StandardSyncOutput actualOutput = execute();
    assertEquals(replicationSuccessOutput, actualOutput);

    verifyReplication(replicationActivity, syncInput, sync.getConnectionId());
  }

  @Test
  void testReplicationFailure() {
    doThrow(new IllegalArgumentException("induced exception")).when(replicationActivity).replicate(
        JOB_RUN_CONFIG,
        SOURCE_LAUNCHER_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        syncInput,
        sync.getConnectionId());

    assertThrows(WorkflowFailedException.class, this::execute);

    verifyReplication(replicationActivity, syncInput, sync.getConnectionId());
  }

  @Test
  void testCancelDuringReplication() {
    doAnswer(ignored -> {
      cancelWorkflow();
      return replicationSuccessOutput;
    }).when(replicationActivity).replicate(
        JOB_RUN_CONFIG,
        SOURCE_LAUNCHER_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        syncInput,
        sync.getConnectionId());

    assertThrows(WorkflowFailedException.class, this::execute);

    verifyReplication(replicationActivity, syncInput, sync.getConnectionId());
  }

  @SuppressWarnings("ResultOfMethodCallIgnored")
  private void cancelWorkflow() {
    final WorkflowServiceGrpc.WorkflowServiceBlockingStub temporalService = testEnv.getWorkflowService().blockingStub();
    // there should only be one execution running.
    final String workflowId = temporalService.listOpenWorkflowExecutions(null).getExecutionsList().get(0).getExecution().getWorkflowId();

    final WorkflowExecution workflowExecution = WorkflowExecution.newBuilder()
        .setWorkflowId(workflowId)
        .build();

    final RequestCancelWorkflowExecutionRequest cancelRequest = RequestCancelWorkflowExecutionRequest.newBuilder()
        .setWorkflowExecution(workflowExecution)
        .build();

    testEnv.getWorkflowService().blockingStub().requestCancelWorkflowExecution(cancelRequest);
  }

  private static void verifyReplication(final ReplicationActivity replicationActivity, final StandardSyncInput syncInput, final UUID connectionId) {
    verify(replicationActivity).replicate(
        JOB_RUN_CONFIG,
        SOURCE_LAUNCHER_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        syncInput,
        connectionId);
  }

  @AfterEach
  public void tearDown() {
    testEnv.close();
  }

}
