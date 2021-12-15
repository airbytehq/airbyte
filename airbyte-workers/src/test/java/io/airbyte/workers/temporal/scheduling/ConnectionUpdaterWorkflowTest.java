/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.airbyte.config.StandardSyncInput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity.ScheduleRetrieverOutput;
import io.airbyte.workers.temporal.scheduling.activities.ConnectionDeletionActivity;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivity.SyncInput;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivity.SyncOutput;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivityImpl;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.AttemptCreationOutput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobCreationOutput;
import io.airbyte.workers.temporal.scheduling.state.WorkflowState;
import io.airbyte.workers.temporal.scheduling.state.listener.TestStateListener;
import io.airbyte.workers.temporal.scheduling.state.listener.WorkflowStateChangedListener.ChangedStateEvent;
import io.airbyte.workers.temporal.sync.EmptySyncWorkflow;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.testing.TestWorkflowEnvironment;
import io.temporal.testing.TestWorkflowExtension;
import io.temporal.worker.Worker;
import java.time.Duration;
import java.util.Queue;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.RegisterExtension;
import org.mockito.Mockito;

@Slf4j
public class ConnectionUpdaterWorkflowTest {

  private static final ConfigFetchActivity mConfigFetchActivity =
      Mockito.mock(ConfigFetchActivity.class, Mockito.withSettings().withoutAnnotations());
  private static final ConnectionDeletionActivity mConnectionDeletionActivity =
      Mockito.mock(ConnectionDeletionActivity.class, Mockito.withSettings().withoutAnnotations());
  private static final GenerateInputActivityImpl mGenerateInputActivityImpl =
      Mockito.mock(GenerateInputActivityImpl.class, Mockito.withSettings().withoutAnnotations());
  private static final JobCreationAndStatusUpdateActivity mJobCreationAndStatusUpdateActivity =
      Mockito.mock(JobCreationAndStatusUpdateActivity.class, Mockito.withSettings().withoutAnnotations());

  @BeforeEach
  public void setUp() {
    Mockito.reset(mConfigFetchActivity);
    Mockito.reset(mConnectionDeletionActivity);
    Mockito.reset(mGenerateInputActivityImpl);
    Mockito.reset(mJobCreationAndStatusUpdateActivity);

    Mockito.when(mConfigFetchActivity.getPeriodicity(Mockito.any()))
        .thenReturn(new ScheduleRetrieverOutput(
            Duration.ofMinutes(1l)));

    Mockito.when(mJobCreationAndStatusUpdateActivity.createNewJob(Mockito.any()))
        .thenReturn(new JobCreationOutput(
            1L));

    Mockito.when(mJobCreationAndStatusUpdateActivity.createNewAttempt(Mockito.any()))
        .thenReturn(new AttemptCreationOutput(
            1));
  }

  @RegisterExtension
  public static final TestWorkflowExtension testWorkflowExtension =
      TestWorkflowExtension.newBuilder()
          .setWorkflowTypes(ConnectionUpdaterWorkflowImpl.class, EmptySyncWorkflow.class)
          .setActivityImplementations(
              mConfigFetchActivity,
              mConnectionDeletionActivity,
              mGenerateInputActivityImpl,
              mJobCreationAndStatusUpdateActivity)
          .build();

  @Test
  public void runSuccess(final TestWorkflowEnvironment testEnv, final WorkflowClient workflowClient, final Worker worker)
      throws InterruptedException {
    /*
     * worker.registerActivitiesImplementations( mConfigFetchActivity, mConnectionDeletionActivity,
     * mGenerateInputActivityImpl, mJobCreationAndStatusUpdateActivity ); testEnv.start();
     */
    final UUID testId = UUID.randomUUID();
    final TestStateListener testStateListener = new TestStateListener();
    final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

    final ConnectionUpdaterWorkflow workflow = workflowClient
        .newWorkflowStub(
            ConnectionUpdaterWorkflow.class,
            WorkflowOptions.newBuilder()
                .setTaskQueue(worker.getTaskQueue())
                .build());

    final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
        UUID.randomUUID(),
        1L,
        1,
        false,
        1,
        workflowState);

    Mockito.when(mGenerateInputActivityImpl.getSyncWorkflowInput(Mockito.any(SyncInput.class)))
        .thenReturn(
            new SyncOutput(
                new JobRunConfig(),
                new IntegrationLauncherConfig(),
                new IntegrationLauncherConfig(),
                new StandardSyncInput()));

    WorkflowClient.start(workflow::run, input);
    testEnv.sleep(Duration.ofSeconds(66L));
    log.error("Test");
    final Queue<ChangedStateEvent> events = testStateListener.events(testId);
    Mockito.verify(mConfigFetchActivity, Mockito.times(2)).getPeriodicity(Mockito.any());
    testEnv.shutdown();
  }

}
