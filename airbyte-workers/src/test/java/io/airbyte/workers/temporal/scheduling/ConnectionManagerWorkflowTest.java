/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.airbyte.config.FailureReason.FailureOrigin;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.temporal.TemporalJobType;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity.GetMaxAttemptOutput;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity.ScheduleRetrieverOutput;
import io.airbyte.workers.temporal.scheduling.activities.ConnectionDeletionActivity;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivity.SyncInput;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivity.SyncOutput;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivityImpl;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.AttemptCreationOutput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.AttemptFailureInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobCreationOutput;
import io.airbyte.workers.temporal.scheduling.state.WorkflowState;
import io.airbyte.workers.temporal.scheduling.state.listener.TestStateListener;
import io.airbyte.workers.temporal.scheduling.state.listener.WorkflowStateChangedListener.ChangedStateEvent;
import io.airbyte.workers.temporal.scheduling.state.listener.WorkflowStateChangedListener.StateField;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.DbtFailureSyncWorkflow;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.EmptySyncWorkflow;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.NormalizationFailureSyncWorkflow;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.PersistFailureSyncWorkflow;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.ReplicateFailureSyncWorkflow;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.SleepingSyncWorkflow;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.SourceAndDestinationFailureSyncWorkflow;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.testing.TestWorkflowEnvironment;
import io.temporal.worker.Worker;
import java.time.Duration;
import java.util.Queue;
import java.util.UUID;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentMatcher;
import org.mockito.Mockito;

public class ConnectionManagerWorkflowTest {

  private final ConfigFetchActivity mConfigFetchActivity =
      Mockito.mock(ConfigFetchActivity.class, Mockito.withSettings().withoutAnnotations());
  private final ConnectionDeletionActivity mConnectionDeletionActivity =
      Mockito.mock(ConnectionDeletionActivity.class, Mockito.withSettings().withoutAnnotations());
  private final GenerateInputActivityImpl mGenerateInputActivityImpl =
      Mockito.mock(GenerateInputActivityImpl.class, Mockito.withSettings().withoutAnnotations());
  private final JobCreationAndStatusUpdateActivity mJobCreationAndStatusUpdateActivity =
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
          workflowState,
          false);

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
          workflowState,
          false);

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
          workflowState,
          false);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofSeconds(30L));
      workflow.submitManualSync();
      testEnv.sleep(Duration.ofSeconds(20L));

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
          workflowState,
          false);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofSeconds(30L));
      workflow.connectionUpdated();
      testEnv.sleep(Duration.ofSeconds(20L));

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
          workflowState,
          false);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofSeconds(30L));
      workflow.cancelJob();
      testEnv.sleep(Duration.ofSeconds(20L));

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
          workflowState,
          false);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofSeconds(30L));
      workflow.deleteConnection();
      testEnv.sleep(Duration.ofMinutes(20L));

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
  @DisplayName("Test which with a long running child workflow")
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
          workflowState,
          false);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofMinutes(2L));
      workflow.submitManualSync();
      testEnv.shutdown();

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.SKIPPED_SCHEDULING && changedStateEvent.isValue())
          .isEmpty();

    }

    @Disabled
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
          workflowState,
          false);

      WorkflowClient.start(workflow::run, input);
      workflow.submitManualSync();
      testEnv.sleep(Duration.ofSeconds(10L));
      workflow.cancelJob();
      testEnv.sleep(Duration.ofMinutes(2L));
      testEnv.shutdown();

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.CANCELLED && changedStateEvent.isValue())
          .hasSizeGreaterThanOrEqualTo(1);

      Mockito.verify(mJobCreationAndStatusUpdateActivity).jobCancelled(Mockito.any());
    }

    @Test
    @DisplayName("Test that resetting a-non running workflow starts a reset")
    public void resetStart() {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          1L,
          1,
          false,
          1,
          workflowState,
          false);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofSeconds(30L));
      workflow.resetConnection();
      testEnv.sleep(Duration.ofSeconds(90L));
      testEnv.shutdown();

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RESET && changedStateEvent.isValue())
          .hasSizeGreaterThanOrEqualTo(1);

      Mockito.verify(mJobCreationAndStatusUpdateActivity).jobSuccess(Mockito.any());

    }

    @Test
    @DisplayName("Test that resetting a running workflow starts cancel the running workflow")
    public void resetCancelRunningWorkflow() {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          1L,
          1,
          false,
          1,
          workflowState,
          false);

      WorkflowClient.start(workflow::run, input);
      workflow.submitManualSync();
      testEnv.sleep(Duration.ofSeconds(30L));
      workflow.resetConnection();
      testEnv.sleep(Duration.ofMinutes(2L));
      testEnv.shutdown();

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RESET && changedStateEvent.isValue())
          .hasSizeGreaterThanOrEqualTo(1);

      Mockito.verify(mJobCreationAndStatusUpdateActivity).jobCancelled(Mockito.any());

    }

    @Test
    @DisplayName("Test that cancelling a reset don't restart a reset")
    public void cancelResetDontContinueAsReset() {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = Mockito.spy(new ConnectionUpdaterInput(
          UUID.randomUUID(),
          1L,
          1,
          false,
          1,
          workflowState,
          true));

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofSeconds(30L));
      workflow.cancelJob();
      testEnv.sleep(Duration.ofMinutes(2L));
      testEnv.shutdown();

      Assertions.assertThat(testStateListener.events(testId))
          .filteredOn((event) -> event.isValue() && event.getField() == StateField.CONTINUE_AS_RESET)
          .isEmpty();

      Assertions.assertThat(testStateListener.events(testId))
          .filteredOn((event) -> !event.isValue() && event.getField() == StateField.CONTINUE_AS_RESET)
          .hasSizeGreaterThanOrEqualTo(2);
    }

    @Test
    @DisplayName("Test workflow which recieved an update signal wait for the current run and report the job status")
    public void updatedSignalRecievedWhileRunning() {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          1L,
          1,
          false,
          1,
          workflowState,
          false);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofSeconds(30L));
      workflow.submitManualSync();
      testEnv.sleep(Duration.ofSeconds(30L));
      workflow.connectionUpdated();
      testEnv.sleep(Duration.ofMinutes(1L));
      testEnv.shutdown();

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RUNNING && changedStateEvent.isValue())
          .hasSizeGreaterThanOrEqualTo(1);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.UPDATED && changedStateEvent.isValue())
          .hasSizeGreaterThanOrEqualTo(1);

      Mockito.verify(mJobCreationAndStatusUpdateActivity).jobSuccess(Mockito.any());
    }

  }

  @Nested
  @DisplayName("Test that sync workflow failures are recorded")
  class SyncWorkflowReplicationFailuresRecorded {

    private static final long JOB_ID = 111L;
    private static final int ATTEMPT_ID = 222;

    @BeforeEach
    public void setup() {
      testEnv = TestWorkflowEnvironment.newInstance();
      worker = testEnv.newWorker(TemporalJobType.CONNECTION_UPDATER.name());
      client = testEnv.getWorkflowClient();
      worker.registerActivitiesImplementations(mConfigFetchActivity, mConnectionDeletionActivity, mGenerateInputActivityImpl,
          mJobCreationAndStatusUpdateActivity);
      workflow = client.newWorkflowStub(ConnectionManagerWorkflow.class,
          WorkflowOptions.newBuilder().setTaskQueue(TemporalJobType.CONNECTION_UPDATER.name()).build());

      Mockito.when(mConfigFetchActivity.getMaxAttempt()).thenReturn(new GetMaxAttemptOutput(1));
    }

    @Test
    @DisplayName("Test that source and destination failures are recorded")
    public void testSourceAndDestinationFailuresRecorded() {
      worker.registerWorkflowImplementationTypes(ConnectionManagerWorkflowImpl.class, SourceAndDestinationFailureSyncWorkflow.class);
      testEnv.start();

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);
      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(UUID.randomUUID(), JOB_ID, ATTEMPT_ID, false, 1, workflowState, false);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofMinutes(2L));
      workflow.submitManualSync();

      Mockito.verify(mJobCreationAndStatusUpdateActivity).attemptFailure(Mockito.argThat(new HasFailureFromSource(FailureOrigin.SOURCE)));
      Mockito.verify(mJobCreationAndStatusUpdateActivity).attemptFailure(Mockito.argThat(new HasFailureFromSource(FailureOrigin.DESTINATION)));

      testEnv.shutdown();
    }

    @Test
    @DisplayName("Test that normalization failure is recorded")
    public void testNormalizationFailure() {
      worker.registerWorkflowImplementationTypes(ConnectionManagerWorkflowImpl.class, NormalizationFailureSyncWorkflow.class);
      testEnv.start();

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);
      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(UUID.randomUUID(), JOB_ID, ATTEMPT_ID, false, 1, workflowState, false);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofMinutes(2L));
      workflow.submitManualSync();

      Mockito.verify(mJobCreationAndStatusUpdateActivity).attemptFailure(Mockito.argThat(new HasFailureFromSource(FailureOrigin.NORMALIZATION)));

      testEnv.shutdown();
    }

    @Test
    @DisplayName("Test that dbt failure is recorded")
    public void testDbtFailureRecorded() {
      worker.registerWorkflowImplementationTypes(ConnectionManagerWorkflowImpl.class, DbtFailureSyncWorkflow.class);
      testEnv.start();

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);
      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(UUID.randomUUID(), JOB_ID, ATTEMPT_ID, false, 1, workflowState, false);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofMinutes(2L));
      workflow.submitManualSync();

      Mockito.verify(mJobCreationAndStatusUpdateActivity).attemptFailure(Mockito.argThat(new HasFailureFromSource(FailureOrigin.DBT)));

      testEnv.shutdown();
    }

    @Test
    @DisplayName("Test that persistence failure is recorded")
    public void testPersistenceFailureRecorded() {
      worker.registerWorkflowImplementationTypes(ConnectionManagerWorkflowImpl.class, PersistFailureSyncWorkflow.class);
      testEnv.start();

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);
      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(UUID.randomUUID(), JOB_ID, ATTEMPT_ID, false, 1, workflowState, false);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofMinutes(2L));
      workflow.submitManualSync();

      Mockito.verify(mJobCreationAndStatusUpdateActivity).attemptFailure(Mockito.argThat(new HasFailureFromSource(FailureOrigin.PERSISTENCE)));

      testEnv.shutdown();
    }

    @Test
    @DisplayName("Test that replication worker failure is recorded")
    public void testReplicationFailureRecorded() {
      worker.registerWorkflowImplementationTypes(ConnectionManagerWorkflowImpl.class, ReplicateFailureSyncWorkflow.class);
      testEnv.start();

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);
      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(UUID.randomUUID(), JOB_ID, ATTEMPT_ID, false, 1, workflowState, false);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofMinutes(2L));
      workflow.submitManualSync();

      Mockito.verify(mJobCreationAndStatusUpdateActivity).attemptFailure(Mockito.argThat(new HasFailureFromSource(FailureOrigin.REPLICATION)));

      testEnv.shutdown();
    }

  }

  private class HasFailureFromSource implements ArgumentMatcher<AttemptFailureInput> {

    private final FailureOrigin expectedFailureOrigin;

    public HasFailureFromSource(final FailureOrigin failureOrigin) {
      this.expectedFailureOrigin = failureOrigin;
    }

    @Override
    public boolean matches(final AttemptFailureInput arg) {
      return arg.getAttemptFailureSummary().getFailures().stream().anyMatch(f -> f.getFailureOrigin().equals(expectedFailureOrigin));
    }

  }

}
