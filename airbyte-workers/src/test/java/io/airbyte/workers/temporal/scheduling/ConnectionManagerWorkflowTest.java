/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.airbyte.config.StandardSyncInput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.temporal.TemporalJobType;
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
import io.airbyte.workers.temporal.scheduling.state.listener.WorkflowStateChangedListener.StateField;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.EmptySyncWorkflow;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.SleepingSyncWorkflow;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.testing.TestWorkflowEnvironment;
import io.temporal.worker.Worker;
import java.time.Duration;
import java.util.Queue;
import java.util.UUID;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

public class ConnectionManagerWorkflowTest {

  private static final ConfigFetchActivity mConfigFetchActivity =
      Mockito.mock(ConfigFetchActivity.class, Mockito.withSettings().withoutAnnotations());
  private static final ConnectionDeletionActivity mConnectionDeletionActivity =
      Mockito.mock(ConnectionDeletionActivity.class, Mockito.withSettings().withoutAnnotations());
  private static final GenerateInputActivityImpl mGenerateInputActivityImpl =
      Mockito.mock(GenerateInputActivityImpl.class, Mockito.withSettings().withoutAnnotations());
  private static final JobCreationAndStatusUpdateActivity mJobCreationAndStatusUpdateActivity =
      Mockito.mock(JobCreationAndStatusUpdateActivity.class, Mockito.withSettings().withoutAnnotations());

  private TestWorkflowEnvironment testEnv;
  private Worker worker;
  private WorkflowClient client;
  private ConnectionManagerWorkflow workflow;

  @BeforeEach
  public void setUp() {
    Mockito.reset(mConfigFetchActivity);
    Mockito.reset(mConnectionDeletionActivity);
    Mockito.reset(mGenerateInputActivityImpl);
    Mockito.reset(mJobCreationAndStatusUpdateActivity);

    Mockito.when(mConfigFetchActivity.getTimeToWait(Mockito.any()))
        .thenReturn(new ScheduleRetrieverOutput(
            Duration.ofMinutes(1l)));

    Mockito.when(mJobCreationAndStatusUpdateActivity.createNewJob(Mockito.any()))
        .thenReturn(new JobCreationOutput(
            1L));

    Mockito.when(mJobCreationAndStatusUpdateActivity.createNewAttempt(Mockito.any()))
        .thenReturn(new AttemptCreationOutput(
            1));

    Mockito.when(mGenerateInputActivityImpl.getSyncWorkflowInput(Mockito.any(SyncInput.class)))
        .thenReturn(
            new SyncOutput(
                new JobRunConfig(),
                new IntegrationLauncherConfig(),
                new IntegrationLauncherConfig(),
                new StandardSyncInput()));
  }

  public void tearDown() {
    testEnv.shutdown();
  }

  @Nested
  @DisplayName("Test which without a long running child workflow")
  class AsynchronousWorkflow {

    @BeforeEach
    public void setup() {
      testEnv = TestWorkflowEnvironment.newInstance();
      worker = testEnv.newWorker(TemporalJobType.CONNECTION_UPDATER.name());
      // Register your workflow implementations
      worker.registerWorkflowImplementationTypes(ConnectionManagerWorkflowImpl.class, EmptySyncWorkflow.class);

      client = testEnv.getWorkflowClient();

      worker.registerActivitiesImplementations(mConfigFetchActivity, mConnectionDeletionActivity,
          mGenerateInputActivityImpl, mJobCreationAndStatusUpdateActivity);
      testEnv.start();

      workflow = client
          .newWorkflowStub(
              ConnectionManagerWorkflow.class,
              WorkflowOptions.newBuilder()
                  .setTaskQueue(TemporalJobType.CONNECTION_UPDATER.name())
                  .build());
    }

    @Test
    @DisplayName("Test that a successful workflow retries and wait")
    public void runSuccess() {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          1L,
          1,
          false,
          1,
          workflowState);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofSeconds(124L));
      Mockito.verify(mConfigFetchActivity, Mockito.atLeast(2)).getTimeToWait(Mockito.any());
      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RUNNING && changedStateEvent.isValue())
          .hasSize(2);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() != StateField.RUNNING && changedStateEvent.isValue())
          .isEmpty();

      testEnv.shutdown();
    }

    @Test
    @DisplayName("Test workflow do not wait to run after a failure")
    public void retryAfterFail() {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          1L,
          1,
          true,
          1,
          workflowState);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofSeconds(50L));
      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RUNNING && changedStateEvent.isValue())
          .hasSize(1);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() != StateField.RUNNING && changedStateEvent.isValue())
          .isEmpty();

      testEnv.shutdown();
    }

    @Test
    @DisplayName("Test workflow which recieved a manual run signal stop waiting")
    public void manualRun() {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          1L,
          1,
          false,
          1,
          workflowState);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofSeconds(2L));
      workflow.submitManualSync();
      testEnv.sleep(Duration.ofSeconds(50L));

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RUNNING && changedStateEvent.isValue())
          .hasSize(1);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.SKIPPED_SCHEDULING && changedStateEvent.isValue())
          .hasSize(1);

      Assertions.assertThat(events)
          .filteredOn(
              changedStateEvent -> (changedStateEvent.getField() != StateField.RUNNING
                  && changedStateEvent.getField() != StateField.SKIPPED_SCHEDULING)
                  && changedStateEvent.isValue())
          .isEmpty();

      testEnv.shutdown();
    }

    @Test
    @DisplayName("Test workflow which recieved an update signal stop waiting, don't run and don't update the job status")
    public void updatedSignalRecieved() {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          1L,
          1,
          false,
          1,
          workflowState);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofSeconds(2L));
      workflow.connectionUpdated();
      testEnv.sleep(Duration.ofSeconds(50L));

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RUNNING && changedStateEvent.isValue())
          .isEmpty();

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.UPDATED && changedStateEvent.isValue())
          .hasSize(1);

      Assertions.assertThat(events)
          .filteredOn(
              changedStateEvent -> changedStateEvent.getField() != StateField.UPDATED && changedStateEvent.isValue())
          .isEmpty();

      Mockito.verifyNoInteractions(mJobCreationAndStatusUpdateActivity);

      testEnv.shutdown();
    }

    @Test
    @DisplayName("Test that cancelling a non running workflow don't do anything")
    public void cancelNonRunning() {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          1L,
          1,
          false,
          1,
          workflowState);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofSeconds(50L));
      workflow.cancelJob();
      testEnv.sleep(Duration.ofSeconds(2L));

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RUNNING && changedStateEvent.isValue())
          .isEmpty();

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.CANCELLED && changedStateEvent.isValue())
          .isEmpty();

      Assertions.assertThat(events)
          .filteredOn(
              changedStateEvent -> changedStateEvent.getField() != StateField.CANCELLED && changedStateEvent.isValue())
          .isEmpty();

      Mockito.verifyNoInteractions(mJobCreationAndStatusUpdateActivity);

      testEnv.shutdown();
    }

    @Test
    @DisplayName("test that the sync is properly delete")
    public void deleteSync() {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          1L,
          1,
          false,
          1,
          workflowState);

      WorkflowClient.start(workflow::run, input);
      workflow.deleteConnection();
      testEnv.sleep(Duration.ofSeconds(50L));

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RUNNING && changedStateEvent.isValue())
          .isEmpty();

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.DELETED && changedStateEvent.isValue())
          .hasSize(1);

      Assertions.assertThat(events)
          .filteredOn(
              changedStateEvent -> changedStateEvent.getField() != StateField.DELETED && changedStateEvent.isValue())
          .isEmpty();

      Mockito.verify(mConnectionDeletionActivity).deleteConnection(Mockito.any());

      testEnv.shutdown();
    }

  }

  @Nested
  @DisplayName("Test which without a long running child workflow")
  class SynchronousWorkflow {

    @BeforeEach
    public void setup() {
      testEnv = TestWorkflowEnvironment.newInstance();
      worker = testEnv.newWorker(TemporalJobType.CONNECTION_UPDATER.name());
      // Register your workflow implementations
      worker.registerWorkflowImplementationTypes(ConnectionManagerWorkflowImpl.class, SleepingSyncWorkflow.class);

      client = testEnv.getWorkflowClient();

      worker.registerActivitiesImplementations(mConfigFetchActivity, mConnectionDeletionActivity,
          mGenerateInputActivityImpl, mJobCreationAndStatusUpdateActivity);
      testEnv.start();

      workflow = client
          .newWorkflowStub(
              ConnectionManagerWorkflow.class,
              WorkflowOptions.newBuilder()
                  .setTaskQueue(TemporalJobType.CONNECTION_UPDATER.name())
                  .build());
    }

    @Test
    @DisplayName("Test workflow which recieved a manual while running does nothing")
    public void manualRun() {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          1L,
          1,
          false,
          1,
          workflowState);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofSeconds(61L));
      workflow.submitManualSync();

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.SKIPPED_SCHEDULING && changedStateEvent.isValue())
          .isEmpty();

      testEnv.shutdown();
    }

    @Test
    @DisplayName("Test that cancelling a running workflow cancel the sync")
    public void cancelRunning() {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          1L,
          1,
          false,
          1,
          workflowState);

      WorkflowClient.start(workflow::run, input);
      workflow.submitManualSync();
      testEnv.sleep(Duration.ofSeconds(1L));
      workflow.cancelJob();
      testEnv.sleep(Duration.ofSeconds(2L));

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.CANCELLED && changedStateEvent.isValue())
          .hasSize(1);

      Mockito.verify(mJobCreationAndStatusUpdateActivity).jobCancelled(Mockito.any());

      testEnv.shutdown();
    }

  }

}
