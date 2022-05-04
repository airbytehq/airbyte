/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import static org.mockito.Mockito.atLeastOnce;

import io.airbyte.config.FailureReason.FailureOrigin;
import io.airbyte.config.FailureReason.FailureType;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.temporal.TemporalJobType;
import io.airbyte.workers.temporal.scheduling.activities.AutoDisableConnectionActivity;
import io.airbyte.workers.temporal.scheduling.activities.AutoDisableConnectionActivity.AutoDisableConnectionActivityInput;
import io.airbyte.workers.temporal.scheduling.activities.AutoDisableConnectionActivity.AutoDisableConnectionOutput;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity.GetMaxAttemptOutput;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity.ScheduleRetrieverOutput;
import io.airbyte.workers.temporal.scheduling.activities.ConnectionDeletionActivity;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivity.GeneratedJobInput;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivity.SyncInputWithAttemptNumber;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivityImpl;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.AttemptNumberCreationOutput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.AttemptNumberFailureInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobCancelledInputWithAttemptNumber;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobCreationOutput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobSuccessInputWithAttemptNumber;
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
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.SyncWorkflowFailingWithHearbeatTimeoutException;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.SyncWorkflowWithActivityFailureException;
import io.airbyte.workers.temporal.sync.SyncWorkflow;
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
import org.junit.jupiter.api.Disabled;
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
  private static final AutoDisableConnectionActivity mAutoDisableConnectionActivity =
      Mockito.mock(AutoDisableConnectionActivity.class, Mockito.withSettings().withoutAnnotations());

  private TestWorkflowEnvironment testEnv;
  private WorkflowClient client;
  private ConnectionManagerWorkflow workflow;

  public static Stream<Arguments> getMaxAttemptForResetRetry() {
    return Stream.of(
        Arguments.of(3), // "The max attempt is 3, it will test that after a failed reset attempt the next attempt will also
                         // be a
        // reset")
        Arguments.of(1) // "The max attempt is 3, it will test that after a failed reset job the next attempt will also be a
                        // job")
    );
  }

  @BeforeEach
  public void setUp() {
    Mockito.reset(mConfigFetchActivity);
    Mockito.reset(mConnectionDeletionActivity);
    Mockito.reset(mGenerateInputActivityImpl);
    Mockito.reset(mJobCreationAndStatusUpdateActivity);
    Mockito.reset(mAutoDisableConnectionActivity);

    // default is to wait "forever"
    Mockito.when(mConfigFetchActivity.getTimeToWait(Mockito.any())).thenReturn(new ScheduleRetrieverOutput(
        Duration.ofDays(100 * 365)));

    Mockito.when(mJobCreationAndStatusUpdateActivity.createNewJob(Mockito.any()))
        .thenReturn(new JobCreationOutput(
            1L));

    Mockito.when(mJobCreationAndStatusUpdateActivity.createNewAttemptNumber(Mockito.any()))
        .thenReturn(new AttemptNumberCreationOutput(
            1));

    Mockito.when(mGenerateInputActivityImpl.getSyncWorkflowInputWithAttemptNumber(Mockito.any(SyncInputWithAttemptNumber.class)))
        .thenReturn(
            new GeneratedJobInput(
                new JobRunConfig(),
                new IntegrationLauncherConfig(),
                new IntegrationLauncherConfig(),
                new StandardSyncInput()));

    Mockito.when(mAutoDisableConnectionActivity.autoDisableFailingConnection(Mockito.any()))
        .thenReturn(new AutoDisableConnectionOutput(false));
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
      setupSpecificChildWorkflow(EmptySyncWorkflow.class);
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that a successful workflow retries and waits")
    public void runSuccess() throws InterruptedException {
      Mockito.when(mConfigFetchActivity.getTimeToWait(Mockito.any()))
          .thenReturn(new ScheduleRetrieverOutput(SCHEDULE_WAIT));

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
          .connectionId(UUID.randomUUID())
          .jobId(JOB_ID)
          .attemptId(ATTEMPT_ID)
          .fromFailure(false)
          .attemptNumber(1)
          .workflowState(workflowState)
          .resetConnection(false)
          .fromJobResetFailure(false)
          .build();

      startWorkflowAndWaitUntilReady(workflow, input);
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
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test workflow does not wait to run after a failure")
    public void retryAfterFail() throws InterruptedException {
      Mockito.when(mConfigFetchActivity.getTimeToWait(Mockito.any()))
          .thenReturn(new ScheduleRetrieverOutput(SCHEDULE_WAIT));

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
          .connectionId(UUID.randomUUID())
          .jobId(JOB_ID)
          .attemptId(ATTEMPT_ID)
          .fromFailure(true)
          .attemptNumber(1)
          .workflowState(workflowState)
          .resetConnection(false)
          .fromJobResetFailure(false)
          .build();

      startWorkflowAndWaitUntilReady(workflow, input);
      testEnv.sleep(Duration.ofMinutes(SCHEDULE_WAIT.toMinutes() - 1));
      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RUNNING && changedStateEvent.isValue())
          .hasSize(1);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> (changedStateEvent.getField() != StateField.RUNNING && changedStateEvent.getField() != StateField.SUCCESS)
              && changedStateEvent.isValue())
          .isEmpty();
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test workflow which receives a manual run signal stops waiting")
    public void manualRun() throws InterruptedException {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
          .connectionId(UUID.randomUUID())
          .jobId(JOB_ID)
          .attemptId(ATTEMPT_ID)
          .fromFailure(false)
          .attemptNumber(1)
          .workflowState(workflowState)
          .resetConnection(false)
          .fromJobResetFailure(false)
          .build();

      startWorkflowAndWaitUntilReady(workflow, input);
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
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test workflow which receives an update signal stops waiting, doesn't run, and doesn't update the job status")
    public void updatedSignalReceived() throws InterruptedException {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
          .connectionId(UUID.randomUUID())
          .jobId(JOB_ID)
          .attemptId(ATTEMPT_ID)
          .fromFailure(false)
          .attemptNumber(1)
          .workflowState(workflowState)
          .resetConnection(false)
          .fromJobResetFailure(false)
          .build();

      startWorkflowAndWaitUntilReady(workflow, input);
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
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that cancelling a non-running workflow doesn't do anything")
    public void cancelNonRunning() throws InterruptedException {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
          .connectionId(UUID.randomUUID())
          .jobId(JOB_ID)
          .attemptId(ATTEMPT_ID)
          .fromFailure(false)
          .attemptNumber(1)
          .workflowState(workflowState)
          .resetConnection(false)
          .fromJobResetFailure(false)
          .build();

      startWorkflowAndWaitUntilReady(workflow, input);
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
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that the sync is properly deleted")
    public void deleteSync() throws InterruptedException {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
          .connectionId(UUID.randomUUID())
          .jobId(JOB_ID)
          .attemptId(ATTEMPT_ID)
          .fromFailure(false)
          .attemptNumber(1)
          .workflowState(workflowState)
          .resetConnection(false)
          .fromJobResetFailure(false)
          .build();

      startWorkflowAndWaitUntilReady(workflow, input);
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

      Mockito.verify(mConnectionDeletionActivity, Mockito.times(1)).deleteConnection(Mockito.any());
    }

  }

  @Nested
  @DisplayName("Test which with a long running child workflow")
  class SynchronousWorkflow {

    @BeforeEach
    public void setup() {
      setupSpecificChildWorkflow(SleepingSyncWorkflow.class);
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test workflow which receives a manual sync while running a scheduled sync does nothing")
    public void manualRun() throws InterruptedException {
      Mockito.when(mConfigFetchActivity.getTimeToWait(Mockito.any()))
          .thenReturn(new ScheduleRetrieverOutput(SCHEDULE_WAIT));

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
          .connectionId(UUID.randomUUID())
          .jobId(JOB_ID)
          .attemptId(ATTEMPT_ID)
          .fromFailure(false)
          .attemptNumber(1)
          .workflowState(workflowState)
          .resetConnection(false)
          .fromJobResetFailure(false)
          .build();

      startWorkflowAndWaitUntilReady(workflow, input);

      // wait until the middle of the run
      testEnv.sleep(Duration.ofMinutes(SCHEDULE_WAIT.toMinutes() + SleepingSyncWorkflow.RUN_TIME.toMinutes() / 2));

      // trigger the manual sync
      workflow.submitManualSync();

      // wait for the rest of the workflow
      testEnv.sleep(Duration.ofMinutes(SleepingSyncWorkflow.RUN_TIME.toMinutes() / 2 + 1));

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.SKIPPED_SCHEDULING && changedStateEvent.isValue())
          .isEmpty();

    }

    @Disabled
    @RepeatedTest(10)
    @Timeout(value = 10,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that cancelling a running workflow cancels the sync")
    public void cancelRunning() throws InterruptedException {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
          .connectionId(UUID.randomUUID())
          .jobId(JOB_ID)
          .attemptId(ATTEMPT_ID)
          .fromFailure(false)
          .attemptNumber(1)
          .workflowState(workflowState)
          .resetConnection(false)
          .fromJobResetFailure(false)
          .build();

      startWorkflowAndWaitUntilReady(workflow, input);

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

      final Queue<ChangedStateEvent> eventQueue = testStateListener.events(testId);
      final List<ChangedStateEvent> events = new ArrayList<>(eventQueue);

      for (final ChangedStateEvent event : events) {
        if (event.isValue()) {
          log.info("event = " + event);
        }
      }

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.CANCELLED && changedStateEvent.isValue())
          .hasSizeGreaterThanOrEqualTo(1);

      Mockito.verify(mJobCreationAndStatusUpdateActivity)
          .jobCancelledWithAttemptNumber(Mockito.argThat(new HasCancellationFailure(JOB_ID, ATTEMPT_ID)));
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that resetting a non-running workflow starts a reset")
    public void resetStart() throws InterruptedException {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
          .connectionId(UUID.randomUUID())
          .jobId(JOB_ID)
          .attemptId(ATTEMPT_ID)
          .fromFailure(false)
          .attemptNumber(1)
          .workflowState(workflowState)
          .resetConnection(false)
          .fromJobResetFailure(false)
          .build();

      startWorkflowAndWaitUntilReady(workflow, input);
      testEnv.sleep(Duration.ofMinutes(5L));
      workflow.resetConnection();
      testEnv.sleep(Duration.ofMinutes(15L));

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RESET && changedStateEvent.isValue())
          .hasSizeGreaterThanOrEqualTo(1);

    }

    @RepeatedTest(10)
    @Timeout(value = 30,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that resetting a running workflow cancels the running workflow")
    @Disabled
    public void resetCancelRunningWorkflow() throws InterruptedException {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
          .connectionId(UUID.randomUUID())
          .jobId(JOB_ID)
          .attemptId(ATTEMPT_ID)
          .fromFailure(false)
          .attemptNumber(1)
          .workflowState(workflowState)
          .resetConnection(false)
          .fromJobResetFailure(false)
          .build();

      startWorkflowAndWaitUntilReady(workflow, input);

      testEnv.sleep(Duration.ofSeconds(30L));
      workflow.submitManualSync();
      testEnv.sleep(Duration.ofSeconds(30L));
      workflow.resetConnection();
      testEnv.sleep(Duration.ofMinutes(15L));

      final Queue<ChangedStateEvent> eventQueue = testStateListener.events(testId);
      final List<ChangedStateEvent> events = new ArrayList<>(eventQueue);

      for (final ChangedStateEvent event : events) {
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

      Mockito.verify(mJobCreationAndStatusUpdateActivity).jobCancelledWithAttemptNumber(Mockito.any(JobCancelledInputWithAttemptNumber.class));

    }

    @RepeatedTest(10)
    @Timeout(value = 10,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that cancelling a reset doesn't restart a reset")
    public void cancelResetDontContinueAsReset() throws InterruptedException {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = Mockito.spy(ConnectionUpdaterInput.builder()
          .connectionId(UUID.randomUUID())
          .jobId(JOB_ID)
          .attemptId(ATTEMPT_ID)
          .fromFailure(false)
          .attemptNumber(1)
          .workflowState(workflowState)
          .resetConnection(true)
          .fromJobResetFailure(false)
          .build());

      startWorkflowAndWaitUntilReady(workflow, input);

      testEnv.sleep(Duration.ofSeconds(30L));
      workflow.cancelJob();
      testEnv.sleep(Duration.ofMinutes(2L));

      Assertions.assertThat(testStateListener.events(testId))
          .filteredOn((event) -> event.isValue() && event.getField() == StateField.CONTINUE_AS_RESET)
          .isEmpty();

      Assertions.assertThat(testStateListener.events(testId))
          .filteredOn((event) -> !event.isValue() && event.getField() == StateField.CONTINUE_AS_RESET)
          .hasSizeGreaterThanOrEqualTo(2);
    }

    @RepeatedTest(10)
    @DisplayName("Test workflow which receives an update signal waits for the current run and reports the job status")
    public void updatedSignalReceivedWhileRunning() throws InterruptedException {

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
          .connectionId(UUID.randomUUID())
          .jobId(JOB_ID)
          .attemptId(ATTEMPT_ID)
          .fromFailure(false)
          .attemptNumber(1)
          .workflowState(workflowState)
          .resetConnection(false)
          .fromJobResetFailure(false)
          .build();

      startWorkflowAndWaitUntilReady(workflow, input);

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

      final Queue<ChangedStateEvent> eventQueue = testStateListener.events(testId);
      final List<ChangedStateEvent> events = new ArrayList<>(eventQueue);

      for (final ChangedStateEvent event : events) {
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

      Mockito.verify(mJobCreationAndStatusUpdateActivity).jobSuccessWithAttemptNumber(Mockito.any(JobSuccessInputWithAttemptNumber.class));
    }

  }

  @Nested
  @DisplayName("Test that connections are auto disabled if conditions are met")
  class AutoDisableConnection {

    private static final long JOB_ID = 111L;
    private static final int ATTEMPT_ID = 222;

    @BeforeEach
    public void setup() {
      testEnv = TestWorkflowEnvironment.newInstance();

      final Worker managerWorker = testEnv.newWorker(TemporalJobType.CONNECTION_UPDATER.name());
      managerWorker.registerWorkflowImplementationTypes(ConnectionManagerWorkflowImpl.class);
      managerWorker.registerActivitiesImplementations(mConfigFetchActivity, mConnectionDeletionActivity,
          mGenerateInputActivityImpl, mJobCreationAndStatusUpdateActivity, mAutoDisableConnectionActivity);

      client = testEnv.getWorkflowClient();
      workflow = client.newWorkflowStub(ConnectionManagerWorkflow.class,
          WorkflowOptions.newBuilder().setTaskQueue(TemporalJobType.CONNECTION_UPDATER.name()).build());

      Mockito.when(mConfigFetchActivity.getMaxAttempt()).thenReturn(new GetMaxAttemptOutput(1));
    }

    @Test
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that auto disable activity is touched during failure")
    public void testAutoDisableOnFailure() throws InterruptedException {
      final Worker syncWorker = testEnv.newWorker(TemporalJobType.SYNC.name());
      syncWorker.registerWorkflowImplementationTypes(SourceAndDestinationFailureSyncWorkflow.class);

      testEnv.start();

      final UUID testId = UUID.randomUUID();
      final UUID connectionId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);
      final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
          .connectionId(connectionId)
          .jobId(JOB_ID)
          .attemptId(ATTEMPT_ID)
          .fromFailure(false)
          .attemptNumber(1)
          .workflowState(workflowState)
          .resetConnection(false)
          .fromJobResetFailure(false)
          .build();

      startWorkflowAndWaitUntilReady(workflow, input);

      // wait for workflow to initialize
      testEnv.sleep(Duration.ofMinutes(1));

      workflow.submitManualSync();
      testEnv.sleep(Duration.ofMinutes(1L)); // any time after no-waiting manual run

      Mockito.verify(mJobCreationAndStatusUpdateActivity, atLeastOnce()).attemptFailureWithAttemptNumber(Mockito.any());
      Mockito.verify(mJobCreationAndStatusUpdateActivity, atLeastOnce()).jobFailure(Mockito.any());
      Mockito.verify(mAutoDisableConnectionActivity)
          .autoDisableFailingConnection(new AutoDisableConnectionActivityInput(connectionId, Mockito.any()));
    }

    @Test
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that auto disable activity is not touched during job success")
    public void testNoAutoDisableOnSuccess() throws InterruptedException {
      final Worker syncWorker = testEnv.newWorker(TemporalJobType.SYNC.name());
      syncWorker.registerWorkflowImplementationTypes(EmptySyncWorkflow.class);

      testEnv.start();

      final UUID testId = UUID.randomUUID();
      final UUID connectionId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);
      final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
          .connectionId(connectionId)
          .jobId(JOB_ID)
          .attemptId(ATTEMPT_ID)
          .fromFailure(false)
          .attemptNumber(0)
          .workflowState(workflowState)
          .resetConnection(false)
          .fromJobResetFailure(false)
          .build();

      startWorkflowAndWaitUntilReady(workflow, input);

      // wait for workflow to initialize
      testEnv.sleep(Duration.ofMinutes(1));

      workflow.submitManualSync();
      testEnv.sleep(Duration.ofMinutes(1L)); // any time after no-waiting manual run
      Mockito.verifyNoInteractions(mAutoDisableConnectionActivity);
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

      final Worker managerWorker = testEnv.newWorker(TemporalJobType.CONNECTION_UPDATER.name());
      managerWorker.registerWorkflowImplementationTypes(ConnectionManagerWorkflowImpl.class);
      managerWorker.registerActivitiesImplementations(mConfigFetchActivity, mConnectionDeletionActivity,
          mGenerateInputActivityImpl, mJobCreationAndStatusUpdateActivity, mAutoDisableConnectionActivity);

      client = testEnv.getWorkflowClient();
      workflow = client.newWorkflowStub(ConnectionManagerWorkflow.class,
          WorkflowOptions.newBuilder().setTaskQueue(TemporalJobType.CONNECTION_UPDATER.name()).build());

      Mockito.when(mConfigFetchActivity.getMaxAttempt()).thenReturn(new GetMaxAttemptOutput(1));
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that source and destination failures are recorded")
    public void testSourceAndDestinationFailuresRecorded() throws InterruptedException {
      final Worker syncWorker = testEnv.newWorker(TemporalJobType.SYNC.name());
      syncWorker.registerWorkflowImplementationTypes(SourceAndDestinationFailureSyncWorkflow.class);

      testEnv.start();

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);
      final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
          .connectionId(UUID.randomUUID())
          .jobId(JOB_ID)
          .attemptId(ATTEMPT_ID)
          .fromFailure(false)
          .attemptNumber(1)
          .workflowState(workflowState)
          .resetConnection(false)
          .fromJobResetFailure(false)
          .build();

      startWorkflowAndWaitUntilReady(workflow, input);

      // wait for workflow to initialize
      testEnv.sleep(Duration.ofMinutes(1));

      workflow.submitManualSync();
      testEnv.sleep(Duration.ofMinutes(1L)); // any time after no-waiting manual run

      Mockito.verify(mJobCreationAndStatusUpdateActivity)
          .attemptFailureWithAttemptNumber(Mockito.argThat(new HasFailureFromOrigin(FailureOrigin.SOURCE)));
      Mockito.verify(mJobCreationAndStatusUpdateActivity)
          .attemptFailureWithAttemptNumber(Mockito.argThat(new HasFailureFromOrigin(FailureOrigin.DESTINATION)));
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that normalization failure is recorded")
    public void testNormalizationFailure() throws InterruptedException {
      final Worker syncWorker = testEnv.newWorker(TemporalJobType.SYNC.name());
      syncWorker.registerWorkflowImplementationTypes(NormalizationFailureSyncWorkflow.class);

      testEnv.start();

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);
      final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
          .connectionId(UUID.randomUUID())
          .jobId(JOB_ID)
          .attemptId(ATTEMPT_ID)
          .fromFailure(false)
          .attemptNumber(1)
          .workflowState(workflowState)
          .resetConnection(false)
          .fromJobResetFailure(false)
          .build();

      startWorkflowAndWaitUntilReady(workflow, input);

      // wait for workflow to initialize
      testEnv.sleep(Duration.ofMinutes(1));

      workflow.submitManualSync();
      testEnv.sleep(Duration.ofMinutes(1L)); // any time after no-waiting manual run

      Mockito.verify(mJobCreationAndStatusUpdateActivity)
          .attemptFailureWithAttemptNumber(Mockito.argThat(new HasFailureFromOrigin(FailureOrigin.NORMALIZATION)));
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that dbt failure is recorded")
    public void testDbtFailureRecorded() throws InterruptedException {
      final Worker syncWorker = testEnv.newWorker(TemporalJobType.SYNC.name());
      syncWorker.registerWorkflowImplementationTypes(DbtFailureSyncWorkflow.class);

      testEnv.start();

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);
      final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
          .connectionId(UUID.randomUUID())
          .jobId(JOB_ID)
          .attemptId(ATTEMPT_ID)
          .fromFailure(false)
          .attemptNumber(1)
          .workflowState(workflowState)
          .resetConnection(false)
          .fromJobResetFailure(false)
          .build();

      startWorkflowAndWaitUntilReady(workflow, input);

      // wait for workflow to initialize
      testEnv.sleep(Duration.ofMinutes(1));

      workflow.submitManualSync();
      testEnv.sleep(Duration.ofMinutes(1L)); // any time after no-waiting manual run

      Mockito.verify(mJobCreationAndStatusUpdateActivity)
          .attemptFailureWithAttemptNumber(Mockito.argThat(new HasFailureFromOrigin(FailureOrigin.DBT)));
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that persistence failure is recorded")
    public void testPersistenceFailureRecorded() throws InterruptedException {
      final Worker syncWorker = testEnv.newWorker(TemporalJobType.SYNC.name());
      syncWorker.registerWorkflowImplementationTypes(PersistFailureSyncWorkflow.class);

      testEnv.start();

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);
      final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
          .connectionId(UUID.randomUUID())
          .jobId(JOB_ID)
          .attemptId(ATTEMPT_ID)
          .fromFailure(false)
          .attemptNumber(1)
          .workflowState(workflowState)
          .resetConnection(false)
          .fromJobResetFailure(false)
          .build();

      startWorkflowAndWaitUntilReady(workflow, input);

      // wait for workflow to initialize
      testEnv.sleep(Duration.ofMinutes(1));

      workflow.submitManualSync();
      testEnv.sleep(Duration.ofMinutes(1L)); // any time after no-waiting manual run

      Mockito.verify(mJobCreationAndStatusUpdateActivity)
          .attemptFailureWithAttemptNumber(Mockito.argThat(new HasFailureFromOrigin(FailureOrigin.PERSISTENCE)));
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that replication worker failure is recorded")
    public void testReplicationFailureRecorded() throws InterruptedException {
      final Worker syncWorker = testEnv.newWorker(TemporalJobType.SYNC.name());
      syncWorker.registerWorkflowImplementationTypes(ReplicateFailureSyncWorkflow.class);

      testEnv.start();

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);
      final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
          .connectionId(UUID.randomUUID())
          .jobId(JOB_ID)
          .attemptId(ATTEMPT_ID)
          .fromFailure(false)
          .attemptNumber(1)
          .workflowState(workflowState)
          .resetConnection(false)
          .fromJobResetFailure(false)
          .build();

      startWorkflowAndWaitUntilReady(workflow, input);

      // wait for workflow to initialize
      testEnv.sleep(Duration.ofMinutes(1));

      workflow.submitManualSync();
      testEnv.sleep(Duration.ofMinutes(1L)); // any time after no-waiting manual run

      Mockito.verify(mJobCreationAndStatusUpdateActivity)
          .attemptFailureWithAttemptNumber(Mockito.argThat(new HasFailureFromOrigin(FailureOrigin.REPLICATION)));
    }

  }

  @Nested
  @DisplayName("Test that the workflow are properly getting stuck")
  class StuckWorkflow {

    @BeforeEach
    public void setup() {
      setupSpecificChildWorkflow(SleepingSyncWorkflow.class);
    }

    public static Stream<Arguments> getSetupFailingFailingActivityBeforeRun() {
      return Stream.of(
          Arguments.of(new Thread(() -> Mockito.when(mJobCreationAndStatusUpdateActivity.createNewJob(Mockito.any()))
              .thenThrow(ApplicationFailure.newNonRetryableFailure("", "")))),
          Arguments.of(new Thread(() -> Mockito.when(mJobCreationAndStatusUpdateActivity.createNewAttemptNumber(Mockito.any()))
              .thenThrow(ApplicationFailure.newNonRetryableFailure("", "")))),
          Arguments.of(new Thread(() -> Mockito.doThrow(ApplicationFailure.newNonRetryableFailure("", ""))
              .when(mJobCreationAndStatusUpdateActivity).reportJobStart(Mockito.any()))),
          Arguments.of(new Thread(
              () -> Mockito.when(mGenerateInputActivityImpl.getSyncWorkflowInputWithAttemptNumber(Mockito.any(SyncInputWithAttemptNumber.class)))
                  .thenThrow(ApplicationFailure.newNonRetryableFailure("", "")))));
    }

    @ParameterizedTest
    @MethodSource("getSetupFailingFailingActivityBeforeRun")
    void testGetStuckBeforeRun(final Thread mockSetup) throws InterruptedException {
      mockSetup.run();
      Mockito.when(mConfigFetchActivity.getTimeToWait(Mockito.any())).thenReturn(new ScheduleRetrieverOutput(
          Duration.ZERO));

      final UUID testId = UUID.randomUUID();
      TestStateListener.reset();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
          .connectionId(UUID.randomUUID())
          .jobId(null)
          .attemptId(null)
          .fromFailure(false)
          .attemptNumber(1)
          .workflowState(workflowState)
          .resetConnection(false)
          .fromJobResetFailure(false)
          .build();

      startWorkflowAndWaitUntilReady(workflow, input);
      testEnv.sleep(Duration.ofMinutes(2L));

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RUNNING && changedStateEvent.isValue())
          .isEmpty();

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.QUARANTINED && changedStateEvent.isValue())
          .hasSize(1);
    }

    @Test
    void testCanGetUnstuck() throws InterruptedException {
      Mockito.when(mJobCreationAndStatusUpdateActivity.createNewJob(Mockito.any()))
          .thenThrow(ApplicationFailure.newNonRetryableFailure("", ""))
          .thenReturn(new JobCreationOutput(1l));

      Mockito.when(mConfigFetchActivity.getTimeToWait(Mockito.any())).thenReturn(new ScheduleRetrieverOutput(
          Duration.ZERO));

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
          .connectionId(UUID.randomUUID())
          .jobId(null)
          .attemptId(null)
          .fromFailure(false)
          .attemptNumber(1)
          .workflowState(workflowState)
          .resetConnection(false)
          .fromJobResetFailure(false)
          .build();

      startWorkflowAndWaitUntilReady(workflow, input);

      testEnv.sleep(Duration.ofSeconds(80L));
      workflow.retryFailedActivity();
      testEnv.sleep(Duration.ofSeconds(30L));

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.QUARANTINED && changedStateEvent.isValue())
          .hasSizeGreaterThanOrEqualTo(1);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RETRY_FAILED_ACTIVITY && changedStateEvent.isValue())
          .hasSize(1);
    }

    public static Stream<Arguments> getSetupFailingFailingActivityAfterRun() {
      return Stream.of(
          Arguments.of((Consumer<ConnectionManagerWorkflow>) ((ConnectionManagerWorkflow workflow) -> System.out.println("do Nothing")),
              new Thread(() -> Mockito.doThrow(ApplicationFailure.newNonRetryableFailure("", ""))
                  .when(mJobCreationAndStatusUpdateActivity).jobSuccessWithAttemptNumber(Mockito.any(JobSuccessInputWithAttemptNumber.class)))),
          Arguments.of((Consumer<ConnectionManagerWorkflow>) ((ConnectionManagerWorkflow workflow) -> workflow.cancelJob()),
              new Thread(() -> Mockito.doThrow(ApplicationFailure.newNonRetryableFailure("", ""))
                  .when(mJobCreationAndStatusUpdateActivity).jobCancelledWithAttemptNumber(Mockito.any(JobCancelledInputWithAttemptNumber.class)))),
          Arguments.of((Consumer<ConnectionManagerWorkflow>) ((ConnectionManagerWorkflow workflow) -> workflow.deleteConnection()),
              new Thread(() -> Mockito.doThrow(ApplicationFailure.newNonRetryableFailure("", ""))
                  .when(mConnectionDeletionActivity).deleteConnection(Mockito.any()))));
    }

    @ParameterizedTest
    @MethodSource("getSetupFailingFailingActivityAfterRun")
    void testGetStuckAfterRun(final Consumer<ConnectionManagerWorkflow> signalSender, final Thread mockSetup) throws InterruptedException {
      mockSetup.run();

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
          .connectionId(UUID.randomUUID())
          .jobId(null)
          .attemptId(null)
          .fromFailure(false)
          .attemptNumber(1)
          .workflowState(workflowState)
          .resetConnection(false)
          .fromJobResetFailure(false)
          .build();

      startWorkflowAndWaitUntilReady(workflow, input);

      // wait for workflow to initialize
      testEnv.sleep(Duration.ofSeconds(5));
      workflow.submitManualSync();

      // wait for workflow to initialize
      testEnv.sleep(Duration.ofSeconds(5));
      signalSender.accept(workflow);

      // TODO
      // For some reason this transiently fails if it is below the runtime.
      // However, this should be reported almost immediately. I think this is a bug.
      testEnv.sleep(Duration.ofSeconds(SleepingSyncWorkflow.RUN_TIME.toSeconds() + 2));

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.QUARANTINED && changedStateEvent.isValue())
          .hasSizeGreaterThanOrEqualTo(1);
    }

  }

  @Nested
  @DisplayName("Test workflow where the child workflow throw a hearbeat timeout exception")
  class HeartbeatFailureWorkflow {

    @BeforeEach
    public void setup() {
      setupSpecificChildWorkflow(SyncWorkflowFailingWithHearbeatTimeoutException.class);
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.workers.temporal.scheduling.ConnectionManagerWorkflowTest#getMaxAttemptForResetRetry")
    public void failedResetContinueAttemptAsReset(final int maxAttempt) throws InterruptedException {
      runRetryResetTest(maxAttempt);
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that a reset job that fails waits after retrying")
    public void failedResetJobWaitsOnRestart() throws InterruptedException {
      runRetryResetWaitsAfterJobFailureTest();
    }

  }

  @Nested
  @DisplayName("Test workflow where the child workflow failed and report it in its output")
  class OutputFailureWorkflow {

    @BeforeEach
    public void setup() {
      setupSpecificChildWorkflow(SyncWorkflowFailingWithHearbeatTimeoutException.class);
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that resetting a non-running workflow starts a reset")
    public void failedResetContinueAsReset() throws InterruptedException {

      Mockito.when(mConfigFetchActivity.getMaxAttempt())
          .thenReturn(new GetMaxAttemptOutput(3));

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
          .connectionId(UUID.randomUUID())
          .jobId(JOB_ID)
          .attemptId(ATTEMPT_ID)
          .fromFailure(false)
          .attemptNumber(1)
          .workflowState(workflowState)
          .resetConnection(false)
          .fromJobResetFailure(false)
          .build();

      startWorkflowAndWaitUntilReady(workflow, input);
      testEnv.sleep(Duration.ofSeconds(30L));
      testEnv.sleep(Duration.ofMinutes(5L));
      workflow.resetConnection();
      testEnv.sleep(Duration.ofMinutes(15L));

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.CONTINUE_AS_RESET && changedStateEvent.isValue())
          .hasSizeGreaterThanOrEqualTo(1);

    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that we are getting stuck if the report of a failure happen")
    void testGetStuckAfterRun() throws InterruptedException {
      Mockito.doThrow(ApplicationFailure.newNonRetryableFailure("", ""))
          .when(mJobCreationAndStatusUpdateActivity).attemptFailureWithAttemptNumber(Mockito.any());

      Mockito.when(mConfigFetchActivity.getMaxAttempt())
          .thenReturn(new GetMaxAttemptOutput(3));

      final UUID testId = UUID.randomUUID();
      final TestStateListener testStateListener = new TestStateListener();
      final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

      final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
          .connectionId(UUID.randomUUID())
          .jobId(null)
          .attemptId(null)
          .fromFailure(false)
          .attemptNumber(1)
          .workflowState(workflowState)
          .resetConnection(false)
          .fromJobResetFailure(false)
          .build();

      startWorkflowAndWaitUntilReady(workflow, input);

      // wait for workflow to initialize
      testEnv.sleep(Duration.ofSeconds(5));
      workflow.submitManualSync();

      // wait for workflow to initialize
      testEnv.sleep(Duration.ofSeconds(5));

      // TODO
      // For some reason this transiently fails if it is below the runtime.
      // However, this should be reported almost immediately. I think this is a bug.
      testEnv.sleep(Duration.ofSeconds(SleepingSyncWorkflow.RUN_TIME.toSeconds() + 2));

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.QUARANTINED && changedStateEvent.isValue())
          .hasSize(1);
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.workers.temporal.scheduling.ConnectionManagerWorkflowTest#getMaxAttemptForResetRetry")
    public void failedResetContinueAttemptAsReset(final int maxAttempt) throws InterruptedException {
      runRetryResetTest(maxAttempt);
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that a reset job that fails wait after retrying")
    public void failedResetJobWaitOnRestart() throws InterruptedException {
      runRetryResetWaitsAfterJobFailureTest();
    }

  }

  @Nested
  @DisplayName("Test workflow where the child workflow throw an activity failure exception")
  class ActivityFailureWorkflow {

    @BeforeEach
    public void setup() {
      setupSpecificChildWorkflow(SyncWorkflowWithActivityFailureException.class);
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.workers.temporal.scheduling.ConnectionManagerWorkflowTest#getMaxAttemptForResetRetry")
    public void failedResetContinueAttemptAsReset(final int maxAttempt) throws InterruptedException {
      runRetryResetTest(maxAttempt);
    }

    @RepeatedTest(10)
    @Timeout(value = 2,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that a reset job that fails waits after retrying")
    public void failedResetJobWaitsOnRestart() throws InterruptedException {
      runRetryResetWaitsAfterJobFailureTest();
    }

  }

  private class HasFailureFromOrigin implements ArgumentMatcher<AttemptNumberFailureInput> {

    private final FailureOrigin expectedFailureOrigin;

    public HasFailureFromOrigin(final FailureOrigin failureOrigin) {
      this.expectedFailureOrigin = failureOrigin;
    }

    @Override
    public boolean matches(final AttemptNumberFailureInput arg) {
      return arg.getAttemptFailureSummary().getFailures().stream().anyMatch(f -> f.getFailureOrigin().equals(expectedFailureOrigin));
    }

  }

  private class HasCancellationFailure implements ArgumentMatcher<JobCancelledInputWithAttemptNumber> {

    private final long expectedJobId;
    private final int expectedAttemptNumber;

    public HasCancellationFailure(final long jobId, final int attemptNumber) {
      this.expectedJobId = jobId;
      this.expectedAttemptNumber = attemptNumber;
    }

    @Override
    public boolean matches(final JobCancelledInputWithAttemptNumber arg) {
      return arg.getAttemptFailureSummary().getFailures().stream().anyMatch(f -> f.getFailureType().equals(FailureType.MANUAL_CANCELLATION))
          && arg.getJobId() == expectedJobId && arg.getAttemptNumber() == expectedAttemptNumber;
    }

  }

  private static void startWorkflowAndWaitUntilReady(final ConnectionManagerWorkflow workflow, final ConnectionUpdaterInput input)
      throws InterruptedException {
    WorkflowClient.start(workflow::run, input);

    boolean isReady = false;

    while (!isReady) {
      try {
        isReady = workflow.getState() != null;
      } catch (final Exception e) {
        log.info("retrying...");
        Thread.sleep(100);
      }
    }
  }

  private <T extends SyncWorkflow> void setupSpecificChildWorkflow(final Class<T> mockedSyncedWorkflow) {
    testEnv = TestWorkflowEnvironment.newInstance();

    final Worker syncWorker = testEnv.newWorker(TemporalJobType.SYNC.name());
    syncWorker.registerWorkflowImplementationTypes(mockedSyncedWorkflow);

    final Worker managerWorker = testEnv.newWorker(TemporalJobType.CONNECTION_UPDATER.name());
    managerWorker.registerWorkflowImplementationTypes(ConnectionManagerWorkflowImpl.class);
    managerWorker.registerActivitiesImplementations(mConfigFetchActivity, mConnectionDeletionActivity,
        mGenerateInputActivityImpl, mJobCreationAndStatusUpdateActivity, mAutoDisableConnectionActivity);

    client = testEnv.getWorkflowClient();
    testEnv.start();

    workflow = client
        .newWorkflowStub(
            ConnectionManagerWorkflow.class,
            WorkflowOptions.newBuilder()
                .setTaskQueue(TemporalJobType.CONNECTION_UPDATER.name())
                .build());
  }

  private void runRetryResetTest(final int maxAttempt) throws InterruptedException {
    Mockito.when(mConfigFetchActivity.getMaxAttempt())
        .thenReturn(new GetMaxAttemptOutput(maxAttempt));

    final UUID testId = UUID.randomUUID();
    final TestStateListener testStateListener = new TestStateListener();
    final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

    final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
        .connectionId(UUID.randomUUID())
        .jobId(JOB_ID)
        .attemptId(ATTEMPT_ID)
        .fromFailure(false)
        .attemptNumber(1)
        .workflowState(workflowState)
        .resetConnection(false)
        .fromJobResetFailure(false)
        .build();

    startWorkflowAndWaitUntilReady(workflow, input);
    testEnv.sleep(Duration.ofMinutes(5L));
    workflow.resetConnection();
    testEnv.sleep(SleepingSyncWorkflow.RUN_TIME.plusMinutes(2));

    final Queue<ChangedStateEvent> events = testStateListener.events(testId);

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.CONTINUE_AS_RESET && changedStateEvent.isValue())
        .hasSizeGreaterThanOrEqualTo(1);
  }

  private void runRetryResetWaitsAfterJobFailureTest() throws InterruptedException {
    Mockito.when(mConfigFetchActivity.getMaxAttempt())
        .thenReturn(new GetMaxAttemptOutput(1));

    final UUID testId = UUID.randomUUID();
    final TestStateListener testStateListener = new TestStateListener();
    final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

    final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
        .connectionId(UUID.randomUUID())
        .jobId(JOB_ID)
        .attemptId(ATTEMPT_ID)
        .fromFailure(false)
        .attemptNumber(1)
        .workflowState(workflowState)
        .resetConnection(false)
        .fromJobResetFailure(false)
        .build();

    startWorkflowAndWaitUntilReady(workflow, input);
    testEnv.sleep(Duration.ofMinutes(5L));
    workflow.resetConnection();
    testEnv.sleep(SleepingSyncWorkflow.RUN_TIME.plusMinutes(2));

    final WorkflowState state = workflow.getState();

    Assertions.assertThat(state.isRunning())
        .isFalse();
  }

}
