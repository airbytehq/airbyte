/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.airbyte.config.FailureReason.FailureOrigin;
import io.airbyte.config.FailureReason.FailureType;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.temporal.TemporalJobType;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity.GetMaxAttemptOutput;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity.ScheduleRetrieverOutput;
import io.airbyte.workers.temporal.scheduling.activities.ConnectionDeletionActivity;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivity.GeneratedJobInput;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivity.SyncInput;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivityImpl;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.AttemptCreationOutput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.AttemptFailureInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobCancelledInput;
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
import io.temporal.failure.ApplicationFailure;
import io.temporal.testing.TestWorkflowEnvironment;
import io.temporal.worker.Worker;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Queue;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.stream.Stream;
import lombok.extern.slf4j.Slf4j;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.RepeatedTest;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.mockito.ArgumentMatcher;
import org.mockito.Mockito;

/**
 * Tests the core state machine of the connection manager workflow.
 *
 * We've had race conditions in this in the past which is why (after addressing them) we have
 * repeated cases, just in case there's a regression where a race condition is added back to a test.
 */
@Slf4j
public class ConnectionManagerWorkflowTest {

  private static final long JOB_ID = 1L;
  private static final int ATTEMPT_ID = 1;

  private static final Duration SCHEDULE_WAIT = Duration.ofMinutes(20L);

  private final ConfigFetchActivity mConfigFetchActivity =
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

    // default is to wait "forever"
    Mockito.when(mConfigFetchActivity.getTimeToWait(Mockito.any())).thenReturn(new ScheduleRetrieverOutput(
        Duration.ofDays(100 * 365)));

    Mockito.when(mJobCreationAndStatusUpdateActivity.createNewJob(Mockito.any()))
        .thenReturn(new JobCreationOutput(
            1L));

    Mockito.when(mJobCreationAndStatusUpdateActivity.createNewAttempt(Mockito.any()))
        .thenReturn(new AttemptCreationOutput(
            1));

    Mockito.when(mGenerateInputActivityImpl.getSyncWorkflowInput(Mockito.any(SyncInput.class)))
        .thenReturn(
            new GeneratedJobInput(
                new JobRunConfig(),
                new IntegrationLauncherConfig(),
                new IntegrationLauncherConfig(),
                new StandardSyncInput()));
  }

  @AfterEach
  public void tearDown() {
    testEnv.shutdown();
    TestStateListener.reset();
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

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that a successful workflow retries and waits")
    public void runSuccess() {
      Mockito.when(mConfigFetchActivity.getTimeToWait(Mockito.any()))
          .thenReturn(new ScheduleRetrieverOutput(SCHEDULE_WAIT));

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          JOB_ID,
          false,
          1,
          workflowState,
          false);

      WorkflowClient.start(workflow::run, input);
      // wait to be scheduled, then to run, then schedule again
      testEnv.sleep(Duration.ofMinutes(SCHEDULE_WAIT.toMinutes() + SCHEDULE_WAIT.toMinutes() + 1));
      Mockito.verify(mConfigFetchActivity, Mockito.atLeast(2)).getTimeToWait(Mockito.any());
      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RUNNING && changedStateEvent.isValue())
          .hasSize(2);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> (changedStateEvent.getField() != StateField.RUNNING && changedStateEvent.getField() != StateField.SUCCESS)
              && changedStateEvent.isValue())
          .isEmpty();

      testEnv.shutdown();
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test workflow does not wait to run after a failure")
    public void retryAfterFail() {
      Mockito.when(mConfigFetchActivity.getTimeToWait(Mockito.any()))
          .thenReturn(new ScheduleRetrieverOutput(SCHEDULE_WAIT));

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          JOB_ID,
          true,
          1,
          workflowState,
          false);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofMinutes(SCHEDULE_WAIT.toMinutes() - 1));
      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RUNNING && changedStateEvent.isValue())
          .hasSize(1);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> (changedStateEvent.getField() != StateField.RUNNING && changedStateEvent.getField() != StateField.SUCCESS)
              && changedStateEvent.isValue())
          .isEmpty();

      testEnv.shutdown();
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test workflow which receives a manual run signal stops waiting")
    public void manualRun() {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          JOB_ID,
          false,
          1,
          workflowState,
          false);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofMinutes(1L)); // any value here, just so it's started
      workflow.submitManualSync();
      testEnv.sleep(Duration.ofMinutes(1L)); // any value here, just so it's past the empty workflow run

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
                  && changedStateEvent.getField() != StateField.SKIPPED_SCHEDULING
                  && changedStateEvent.getField() != StateField.SUCCESS)
                  && changedStateEvent.isValue())
          .isEmpty();

      testEnv.shutdown();
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test workflow which receives an update signal stops waiting, doesn't run, and doesn't update the job status")
    public void updatedSignalReceived() {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          JOB_ID,
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
              changedStateEvent -> (changedStateEvent.getField() != StateField.UPDATED && changedStateEvent.getField() != StateField.SUCCESS)
                  && changedStateEvent.isValue())
          .isEmpty();

      Mockito.verifyNoInteractions(mJobCreationAndStatusUpdateActivity);

      testEnv.shutdown();
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that cancelling a non-running workflow doesn't do anything")
    public void cancelNonRunning() {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          JOB_ID,
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
              changedStateEvent -> (changedStateEvent.getField() != StateField.CANCELLED && changedStateEvent.getField() != StateField.SUCCESS)
                  && changedStateEvent.isValue())
          .isEmpty();

      Mockito.verifyNoInteractions(mJobCreationAndStatusUpdateActivity);

      testEnv.shutdown();
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that the sync is properly deleted")
    public void deleteSync() {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          JOB_ID,
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
              changedStateEvent -> changedStateEvent.getField() != StateField.DELETED && changedStateEvent.getField() != StateField.SUCCESS
                  && changedStateEvent.isValue())
          .isEmpty();

      Mockito.verify(mConnectionDeletionActivity, Mockito.atLeast(1)).deleteConnection(Mockito.any());

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

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test workflow which receives a manual sync while running a scheduled sync does nothing")
    public void manualRun() {
      Mockito.when(mConfigFetchActivity.getTimeToWait(Mockito.any()))
          .thenReturn(new ScheduleRetrieverOutput(SCHEDULE_WAIT));

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          JOB_ID,
          false,
          1,
          workflowState,
          false);

      WorkflowClient.start(workflow::run, input);

      // wait until the middle of the run
      testEnv.sleep(Duration.ofMinutes(SCHEDULE_WAIT.toMinutes() + SleepingSyncWorkflow.RUN_TIME.toMinutes() / 2));

      // trigger the manual sync
      workflow.submitManualSync();

      // wait for the rest of the workflow
      testEnv.sleep(Duration.ofMinutes(SleepingSyncWorkflow.RUN_TIME.toMinutes() / 2 + 1));
      testEnv.shutdown();

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.SKIPPED_SCHEDULING && changedStateEvent.isValue())
          .isEmpty();

    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that cancelling a running workflow cancels the sync")
    public void cancelRunning() {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          JOB_ID,
          false,
          1,
          workflowState,
          false);

      WorkflowClient.start(workflow::run, input);

      // wait for workflow to initialize
      testEnv.sleep(Duration.ofMinutes(1));

      workflow.submitManualSync();

      // wait for the manual sync to start working
      testEnv.sleep(Duration.ofMinutes(1));

      workflow.cancelJob();

      // TODO
      // For some reason this transiently fails if it is below the runtime.
      // However, this should be reported almost immediately. I think this is a bug.
      testEnv.sleep(Duration.ofMinutes(SleepingSyncWorkflow.RUN_TIME.toMinutes() + 1));

      testEnv.shutdown();

      final Queue<ChangedStateEvent> eventQueue = testStateListener.events(testId);
      final List<ChangedStateEvent> events = new ArrayList<>(eventQueue);

      for (ChangedStateEvent event : events) {
        if (event.isValue()) {
          log.info("event = " + event);
        }
      }

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.CANCELLED && changedStateEvent.isValue())
          .hasSizeGreaterThanOrEqualTo(1);

      Mockito.verify(mJobCreationAndStatusUpdateActivity).jobCancelled(Mockito.argThat(new HasCancellationFailure(JOB_ID, ATTEMPT_ID)));
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that resetting a non-running workflow starts a reset")
    public void resetStart() {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          JOB_ID,
          false,
          1,
          workflowState,
          false);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofMinutes(5L));
      workflow.resetConnection();
      testEnv.sleep(Duration.ofMinutes(15L));
      testEnv.shutdown();

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RESET && changedStateEvent.isValue())
          .hasSizeGreaterThanOrEqualTo(1);

    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that resetting a running workflow cancels the running workflow")
    public void resetCancelRunningWorkflow() {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          JOB_ID,
          false,
          1,
          workflowState,
          false);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofSeconds(30L));
      workflow.submitManualSync();
      testEnv.sleep(Duration.ofSeconds(30L));
      workflow.resetConnection();
      testEnv.sleep(Duration.ofMinutes(15L));
      testEnv.shutdown();

      final Queue<ChangedStateEvent> eventQueue = testStateListener.events(testId);
      final List<ChangedStateEvent> events = new ArrayList<>(eventQueue);

      for (ChangedStateEvent event : events) {
        if (event.isValue()) {
          log.info("event = " + event);
        }
      }

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.CANCELLED_FOR_RESET && changedStateEvent.isValue())
          .hasSizeGreaterThanOrEqualTo(1);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RESET && changedStateEvent.isValue())
          .hasSizeGreaterThanOrEqualTo(1);

      Mockito.verify(mJobCreationAndStatusUpdateActivity).jobCancelled(Mockito.any());

    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that cancelling a reset doesn't restart a reset")
    public void cancelResetDontContinueAsReset() {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = Mockito.spy(new ConnectionUpdaterInput(
          UUID.randomUUID(),
          JOB_ID,
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

    @RepeatedTest(10)
    @DisplayName("Test workflow which receives an update signal waits for the current run and reports the job status")
    public void updatedSignalReceivedWhileRunning() {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          JOB_ID,
          false,
          1,
          workflowState,
          false);

      WorkflowClient.start(workflow::run, input);

      // wait for workflow to initialize
      testEnv.sleep(Duration.ofMinutes(1));

      // submit sync
      workflow.submitManualSync();

      // wait until the middle of the manual run
      testEnv.sleep(Duration.ofMinutes(SleepingSyncWorkflow.RUN_TIME.toMinutes() / 2));

      // indicate connection update
      workflow.connectionUpdated();

      // wait after the rest of the run
      testEnv.sleep(Duration.ofMinutes(SleepingSyncWorkflow.RUN_TIME.toMinutes() / 2 + 1));

      testEnv.shutdown();

      final Queue<ChangedStateEvent> eventQueue = testStateListener.events(testId);
      final List<ChangedStateEvent> events = new ArrayList<>(eventQueue);

      for (ChangedStateEvent event : events) {
        if (event.isValue()) {
          log.info("event = " + event);
        }
      }

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

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that source and destination failures are recorded")
    public void testSourceAndDestinationFailuresRecorded() {
      worker.registerWorkflowImplementationTypes(ConnectionManagerWorkflowImpl.class, SourceAndDestinationFailureSyncWorkflow.class);
      testEnv.start();

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);
      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(UUID.randomUUID(), JOB_ID, false, 1, workflowState, false);

      WorkflowClient.start(workflow::run, input);

      // wait for workflow to initialize
      testEnv.sleep(Duration.ofMinutes(1));

      workflow.submitManualSync();
      testEnv.sleep(Duration.ofMinutes(1L)); // any time after no-waiting manual run

      Mockito.verify(mJobCreationAndStatusUpdateActivity).attemptFailure(Mockito.argThat(new HasFailureFromOrigin(FailureOrigin.SOURCE)));
      Mockito.verify(mJobCreationAndStatusUpdateActivity).attemptFailure(Mockito.argThat(new HasFailureFromOrigin(FailureOrigin.DESTINATION)));

      testEnv.shutdown();
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that normalization failure is recorded")
    public void testNormalizationFailure() {
      worker.registerWorkflowImplementationTypes(ConnectionManagerWorkflowImpl.class, NormalizationFailureSyncWorkflow.class);
      testEnv.start();

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);
      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(UUID.randomUUID(), JOB_ID, false, 1, workflowState, false);

      WorkflowClient.start(workflow::run, input);

      // wait for workflow to initialize
      testEnv.sleep(Duration.ofMinutes(1));

      workflow.submitManualSync();
      testEnv.sleep(Duration.ofMinutes(1L)); // any time after no-waiting manual run

      Mockito.verify(mJobCreationAndStatusUpdateActivity).attemptFailure(Mockito.argThat(new HasFailureFromOrigin(FailureOrigin.NORMALIZATION)));

      testEnv.shutdown();
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that dbt failure is recorded")
    public void testDbtFailureRecorded() {
      worker.registerWorkflowImplementationTypes(ConnectionManagerWorkflowImpl.class, DbtFailureSyncWorkflow.class);
      testEnv.start();

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);
      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(UUID.randomUUID(), JOB_ID, false, 1, workflowState, false);

      WorkflowClient.start(workflow::run, input);

      // wait for workflow to initialize
      testEnv.sleep(Duration.ofMinutes(1));

      workflow.submitManualSync();
      testEnv.sleep(Duration.ofMinutes(1L)); // any time after no-waiting manual run

      Mockito.verify(mJobCreationAndStatusUpdateActivity).attemptFailure(Mockito.argThat(new HasFailureFromOrigin(FailureOrigin.DBT)));

      testEnv.shutdown();
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that persistence failure is recorded")
    public void testPersistenceFailureRecorded() {
      worker.registerWorkflowImplementationTypes(ConnectionManagerWorkflowImpl.class, PersistFailureSyncWorkflow.class);
      testEnv.start();

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);
      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(UUID.randomUUID(), JOB_ID, false, 1, workflowState, false);

      WorkflowClient.start(workflow::run, input);

      // wait for workflow to initialize
      testEnv.sleep(Duration.ofMinutes(1));

      workflow.submitManualSync();
      testEnv.sleep(Duration.ofMinutes(1L)); // any time after no-waiting manual run

      Mockito.verify(mJobCreationAndStatusUpdateActivity).attemptFailure(Mockito.argThat(new HasFailureFromOrigin(FailureOrigin.PERSISTENCE)));

      testEnv.shutdown();
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that replication worker failure is recorded")
    public void testReplicationFailureRecorded() {
      worker.registerWorkflowImplementationTypes(ConnectionManagerWorkflowImpl.class, ReplicateFailureSyncWorkflow.class);
      testEnv.start();

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);
      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(UUID.randomUUID(), JOB_ID, false, 1, workflowState, false);

      WorkflowClient.start(workflow::run, input);

      // wait for workflow to initialize
      testEnv.sleep(Duration.ofMinutes(1));

      workflow.submitManualSync();
      testEnv.sleep(Duration.ofMinutes(1L)); // any time after no-waiting manual run

      Mockito.verify(mJobCreationAndStatusUpdateActivity).attemptFailure(Mockito.argThat(new HasFailureFromOrigin(FailureOrigin.REPLICATION)));

      testEnv.shutdown();
    }

  }

  @Nested
  @DisplayName("Test that the workflow are properly getting stuck")
  class StuckWorkflow {

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

    public static Stream<Arguments> getSetupFailingFailingActivityBeforeRun() {
      Thread.currentThread().run();
      return Stream.of(
          Arguments.of(new Thread(() -> Mockito.when(mJobCreationAndStatusUpdateActivity.createNewJob(Mockito.any()))
              .thenThrow(ApplicationFailure.newNonRetryableFailure("", "")))),
          Arguments.of(new Thread(() -> Mockito.when(mJobCreationAndStatusUpdateActivity.createNewAttempt(Mockito.any()))
              .thenThrow(ApplicationFailure.newNonRetryableFailure("", "")))),
          Arguments.of(new Thread(() -> Mockito.doThrow(ApplicationFailure.newNonRetryableFailure("", ""))
              .when(mJobCreationAndStatusUpdateActivity).reportJobStart(Mockito.any()))),
          Arguments.of(new Thread(() -> Mockito.when(mGenerateInputActivityImpl.getSyncWorkflowInput(Mockito.any()))
              .thenThrow(ApplicationFailure.newNonRetryableFailure("", "")))));
    }

    @ParameterizedTest
    @MethodSource("getSetupFailingFailingActivityBeforeRun")
    void testGetStuckBeforeRun(Thread mockSetup) {
      mockSetup.run();
      Mockito.when(mConfigFetchActivity.getTimeToWait(Mockito.any())).thenReturn(new ScheduleRetrieverOutput(
          Duration.ZERO));

      final UUID testId = UUID.randomUUID();
      TestStateListener.reset();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          null,
          false,
          1,
          workflowState,
          false);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofMinutes(2L));
      testEnv.shutdown();

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RUNNING && changedStateEvent.isValue())
          .isEmpty();

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.QUARANTINED && changedStateEvent.isValue())
          .hasSize(1);
    }

    @Test
    void testCanGetUnstuck() {
      Mockito.when(mJobCreationAndStatusUpdateActivity.createNewJob(Mockito.any()))
          .thenThrow(ApplicationFailure.newNonRetryableFailure("", ""))
          .thenReturn(new JobCreationOutput(1l));

      Mockito.when(mConfigFetchActivity.getTimeToWait(Mockito.any())).thenReturn(new ScheduleRetrieverOutput(
          Duration.ZERO));

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          null,
          false,
          1,
          workflowState,
          false);

      WorkflowClient.start(workflow::run, input);
      testEnv.sleep(Duration.ofSeconds(80L));
      workflow.retryFailedActivity();
      testEnv.sleep(Duration.ofSeconds(30L));

      testEnv.shutdown();

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.QUARANTINED && changedStateEvent.isValue())
          .hasSizeGreaterThanOrEqualTo(1);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RETRY_FAILED_ACTIVITY && changedStateEvent.isValue())
          .hasSize(1);
    }

    public static Stream<Arguments> getSetupFailingFailingActivityAfterRun() {
      Thread.currentThread().run();
      return Stream.of(
          Arguments.of((Consumer<ConnectionManagerWorkflow>) ((ConnectionManagerWorkflow workflow) -> System.out.println("do Nothing")),
              new Thread(() -> Mockito.doThrow(ApplicationFailure.newNonRetryableFailure("", ""))
                  .when(mJobCreationAndStatusUpdateActivity).jobSuccess(Mockito.any()))),
          Arguments.of((Consumer<ConnectionManagerWorkflow>) ((ConnectionManagerWorkflow workflow) -> workflow.cancelJob()),
              new Thread(() -> Mockito.doThrow(ApplicationFailure.newNonRetryableFailure("", ""))
                  .when(mJobCreationAndStatusUpdateActivity).jobCancelled(Mockito.any()))),
          Arguments.of((Consumer<ConnectionManagerWorkflow>) ((ConnectionManagerWorkflow workflow) -> workflow.deleteConnection()),
              new Thread(() -> Mockito.doThrow(ApplicationFailure.newNonRetryableFailure("", ""))
                  .when(mConnectionDeletionActivity).deleteConnection(Mockito.any()))),
          Arguments.of((Consumer<ConnectionManagerWorkflow>) ((ConnectionManagerWorkflow workflow) -> workflow.simulateFailure()),
              new Thread(() -> Mockito.doThrow(ApplicationFailure.newNonRetryableFailure("", ""))
                  .when(mJobCreationAndStatusUpdateActivity).attemptFailure(Mockito.any()))));
    }

    @ParameterizedTest
    @MethodSource("getSetupFailingFailingActivityAfterRun")
    void testGetStuckAfterRun(Consumer<ConnectionManagerWorkflow> signalSender, Thread mockSetup) {
      mockSetup.run();

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
          UUID.randomUUID(),
          null,
          false,
          1,
          workflowState,
          false);

      WorkflowClient.start(workflow::run, input);

      // wait for workflow to initialize
      testEnv.sleep(Duration.ofMinutes(1));
      workflow.submitManualSync();

      // wait for workflow to initialize
      testEnv.sleep(Duration.ofMinutes(1));
      signalSender.accept(workflow);

      // TODO
      // For some reason this transiently fails if it is below the runtime.
      // However, this should be reported almost immediately. I think this is a bug.
      testEnv.sleep(Duration.ofMinutes(SleepingSyncWorkflow.RUN_TIME.toMinutes() + 1));
      testEnv.shutdown();

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.QUARANTINED && changedStateEvent.isValue())
          .hasSize(1);
    }

  }

  private class HasFailureFromOrigin implements ArgumentMatcher<AttemptFailureInput> {

    private final FailureOrigin expectedFailureOrigin;

    public HasFailureFromOrigin(final FailureOrigin failureOrigin) {
      this.expectedFailureOrigin = failureOrigin;
    }

    @Override
    public boolean matches(final AttemptFailureInput arg) {
      return arg.getAttemptFailureSummary().getFailures().stream().anyMatch(f -> f.getFailureOrigin().equals(expectedFailureOrigin));
    }

  }

  private class HasCancellationFailure implements ArgumentMatcher<JobCancelledInput> {

    private final long expectedJobId;
    private final int expectedAttemptId;

    public HasCancellationFailure(final long jobId, final int attemptId) {
      this.expectedJobId = jobId;
      this.expectedAttemptId = attemptId;
    }

    @Override
    public boolean matches(final JobCancelledInput arg) {
      return arg.getAttemptFailureSummary().getFailures().stream().anyMatch(f -> f.getFailureType().equals(FailureType.MANUAL_CANCELLATION))
          && arg.getJobId() == expectedJobId && arg.getAttemptId() == expectedAttemptId;
    }

  }

}
