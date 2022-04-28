/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;

import io.airbyte.config.NormalizationInput;
import io.airbyte.config.NormalizationSummary;
import io.airbyte.config.OperatorDbtInput;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.TestConfigHelpers;
import io.airbyte.workers.temporal.check.connection.CheckConnectionActivity;
import io.airbyte.workers.temporal.check.connection.CheckConnectionActivityImpl;
import io.airbyte.workers.temporal.sync.DbtTransformationActivity;
import io.airbyte.workers.temporal.sync.DbtTransformationActivityImpl;
import io.airbyte.workers.temporal.sync.NormalizationActivity;
import io.airbyte.workers.temporal.sync.NormalizationActivityImpl;
import io.airbyte.workers.temporal.sync.PersistStateActivity;
import io.airbyte.workers.temporal.sync.PersistStateActivityImpl;
import io.airbyte.workers.temporal.sync.ReplicationActivity;
import io.airbyte.workers.temporal.sync.ReplicationActivityImpl;
import io.airbyte.workers.temporal.sync.SyncWorkflow;
import io.airbyte.workers.temporal.sync.SyncWorkflowImpl;
import io.temporal.api.common.v1.WorkflowExecution;
import io.temporal.api.workflowservice.v1.RequestCancelWorkflowExecutionRequest;
import io.temporal.api.workflowservice.v1.WorkflowServiceGrpc.WorkflowServiceBlockingStub;
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

class SyncWorkflowTest {

  // TEMPORAL

  private TestWorkflowEnvironment testEnv;
  private Worker syncWorker;
  private WorkflowClient client;
  private CheckConnectionActivityImpl checkActivity;
  private ReplicationActivityImpl replicationActivity;
  private NormalizationActivityImpl normalizationActivity;
  private DbtTransformationActivityImpl dbtTransformationActivity;
  private PersistStateActivityImpl persistStateActivity;

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
  private NormalizationInput normalizationInput;
  private OperatorDbtInput operatorDbtInput;

  private StandardSyncOutput replicationSuccessOutput;
  private NormalizationSummary normalizationSummary;

  @BeforeEach
  public void setUp() {
    testEnv = TestWorkflowEnvironment.newInstance();
    syncWorker = testEnv.newWorker(TemporalJobType.SYNC.name());
    syncWorker.registerWorkflowImplementationTypes(SyncWorkflowImpl.class);

    client = testEnv.getWorkflowClient();

    final ImmutablePair<StandardSync, StandardSyncInput> syncPair = TestConfigHelpers.createSyncConfig();
    sync = syncPair.getKey();
    syncInput = syncPair.getValue();
    replicationSuccessOutput = new StandardSyncOutput().withOutputCatalog(syncInput.getCatalog());
    normalizationSummary = new NormalizationSummary();

    normalizationInput = new NormalizationInput()
        .withDestinationConfiguration(syncInput.getDestinationConfiguration())
        .withCatalog(syncInput.getCatalog());

    operatorDbtInput = new OperatorDbtInput()
        .withDestinationConfiguration(syncInput.getDestinationConfiguration())
        .withOperatorDbt(syncInput.getOperationSequence().get(1).getOperatorDbt());

    checkActivity = mock(CheckConnectionActivityImpl.class);
    replicationActivity = mock(ReplicationActivityImpl.class);
    normalizationActivity = mock(NormalizationActivityImpl.class);
    dbtTransformationActivity = mock(DbtTransformationActivityImpl.class);
    persistStateActivity = mock(PersistStateActivityImpl.class);
  }

  // bundle up all the temporal worker setup / execution into one method.
  private StandardSyncOutput execute() {
    syncWorker.registerActivitiesImplementations(checkActivity, replicationActivity, normalizationActivity, dbtTransformationActivity, persistStateActivity);
    testEnv.start();
    final SyncWorkflow workflow =
        client.newWorkflowStub(SyncWorkflow.class, WorkflowOptions.newBuilder().setTaskQueue(TemporalJobType.SYNC.name()).build());

    return workflow.run(JOB_RUN_CONFIG, SOURCE_LAUNCHER_CONFIG, DESTINATION_LAUNCHER_CONFIG, syncInput, sync.getConnectionId());
  }

  @Test
  void testSuccess() {
    doReturn(replicationSuccessOutput).when(replicationActivity).replicate(
        JOB_RUN_CONFIG,
        SOURCE_LAUNCHER_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        syncInput);

    doReturn(normalizationSummary).when(normalizationActivity).normalize(
        JOB_RUN_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        normalizationInput);

    final StandardSyncOutput actualOutput = execute();

    verifyReplication(replicationActivity, syncInput, sync.getConnectionId());
    verifyPersistState(persistStateActivity, sync, replicationSuccessOutput);
    verifyNormalize(normalizationActivity, normalizationInput);
    verifyDbtTransform(dbtTransformationActivity, syncInput.getResourceRequirements(), operatorDbtInput);
    assertEquals(replicationSuccessOutput.withNormalizationSummary(normalizationSummary), actualOutput);
  }

  @Test
  void testReplicationFailure() {
    doThrow(new IllegalArgumentException("induced exception")).when(replicationActivity).replicate(
        JOB_RUN_CONFIG,
        SOURCE_LAUNCHER_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        syncInput);

    assertThrows(WorkflowFailedException.class, this::execute);

    verifyReplication(replicationActivity, syncInput, sync.getConnectionId());
    verifyNoInteractions(persistStateActivity);
    verifyNoInteractions(normalizationActivity);
    verifyNoInteractions(dbtTransformationActivity);
  }

  @Test
  void testNormalizationFailure() {
    doReturn(replicationSuccessOutput).when(replicationActivity).replicate(
        JOB_RUN_CONFIG,
        SOURCE_LAUNCHER_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        syncInput);

    doThrow(new IllegalArgumentException("induced exception")).when(normalizationActivity).normalize(
        JOB_RUN_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        normalizationInput);

    assertThrows(WorkflowFailedException.class, this::execute);

    verifyReplication(replicationActivity, syncInput, sync.getConnectionId());
    verifyPersistState(persistStateActivity, sync, replicationSuccessOutput);
    verifyNormalize(normalizationActivity, normalizationInput);
    verifyNoInteractions(dbtTransformationActivity);
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
        syncInput);

    assertThrows(WorkflowFailedException.class, this::execute);

    verifyReplication(replicationActivity, syncInput, sync.getConnectionId());
    verifyNoInteractions(persistStateActivity);
    verifyNoInteractions(normalizationActivity);
    verifyNoInteractions(dbtTransformationActivity);
  }

  @Test
  void testCancelDuringNormalization() {
    doReturn(replicationSuccessOutput).when(replicationActivity).replicate(
        JOB_RUN_CONFIG,
        SOURCE_LAUNCHER_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        syncInput);

    doAnswer(ignored -> {
      cancelWorkflow();
      return replicationSuccessOutput;
    }).when(normalizationActivity).normalize(
        JOB_RUN_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        normalizationInput);

    assertThrows(WorkflowFailedException.class, this::execute);

    verifyReplication(replicationActivity, syncInput, sync.getConnectionId());
    verifyPersistState(persistStateActivity, sync, replicationSuccessOutput);
    verifyNormalize(normalizationActivity, normalizationInput);
    verifyNoInteractions(dbtTransformationActivity);
  }

  @SuppressWarnings("ResultOfMethodCallIgnored")
  private void cancelWorkflow() {
    final WorkflowServiceBlockingStub temporalService = testEnv.getWorkflowService().blockingStub();
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
        syncInput);
  }

  private static void verifyPersistState(final PersistStateActivity persistStateActivity,
                                         final StandardSync sync,
                                         final StandardSyncOutput syncOutput) {
    verify(persistStateActivity).persist(
        sync.getConnectionId(),
        syncOutput);
  }

  private static void verifyNormalize(final NormalizationActivity normalizationActivity, final NormalizationInput normalizationInput) {
    verify(normalizationActivity).normalize(
        JOB_RUN_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        normalizationInput);
  }

  private static void verifyDbtTransform(final DbtTransformationActivity dbtTransformationActivity,
                                         final ResourceRequirements resourceRequirements,
                                         final OperatorDbtInput operatorDbtInput) {
    verify(dbtTransformationActivity).run(
        JOB_RUN_CONFIG,
        DESTINATION_LAUNCHER_CONFIG,
        resourceRequirements,
        operatorDbtInput);
  }

  @AfterEach
  public void tearDown() {
    testEnv.close();
  }

}
