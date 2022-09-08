package io.airbyte.workers.temporal.scheduling.connection.manager;

import io.airbyte.workers.temporal.scheduling.ConnectionUpdaterInput;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity.ScheduleRetrieverOutput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobCancelledInputWithAttemptNumber;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobSuccessInputWithAttemptNumber;
import io.airbyte.workers.temporal.scheduling.activities.StreamResetActivity.DeleteStreamResetRecordsForJobInput;
import io.airbyte.workers.temporal.scheduling.state.WorkflowState;
import io.airbyte.workers.temporal.scheduling.state.listener.TestStateListener;
import io.airbyte.workers.temporal.scheduling.state.listener.WorkflowStateChangedListener.ChangedStateEvent;
import io.airbyte.workers.temporal.scheduling.state.listener.WorkflowStateChangedListener.StateField;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.SleepingSyncWorkflow;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Queue;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import lombok.extern.slf4j.Slf4j;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.mockito.Mockito;

@Slf4j
public class SynchronousWorkflow extends BaseConnectionManagerWorkflowTest {

  @BeforeEach
  void setup() {
    setupSpecificChildWorkflow(SleepingSyncWorkflow.class);
  }

  @Test
  @Timeout(value = 10,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test workflow which receives a manual sync while running a scheduled sync does nothing")
  void manualRun() throws InterruptedException {
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

  @Test
  @Timeout(value = 10,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test that cancelling a running workflow cancels the sync")
  void cancelRunning() throws InterruptedException {

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
        .build();

    startWorkflowAndWaitUntilReady(workflow, input);

    // wait for workflow to initialize
    testEnv.sleep(Duration.ofMinutes(1));

    workflow.submitManualSync();

    // wait for the manual sync to start working
    testEnv.sleep(Duration.ofMinutes(1));

    workflow.cancelJob();

    Thread.sleep(500);

    final Queue<ChangedStateEvent> eventQueue = testStateListener.events(testId);
    final List<ChangedStateEvent> events = new ArrayList<>(eventQueue);

    for (final ChangedStateEvent event : events) {
      if (event.isValue()) {
        log.info(EVENT + event);
      }
    }

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.CANCELLED && changedStateEvent.isValue())
        .hasSizeGreaterThanOrEqualTo(1);

    Mockito.verify(mJobCreationAndStatusUpdateActivity)
        .jobCancelledWithAttemptNumber(Mockito.argThat(new HasCancellationFailure(JOB_ID, ATTEMPT_ID)));
  }

  @Timeout(value = 40,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test that deleting a running workflow cancels the sync")
  void deleteRunning() throws InterruptedException {

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
        .build();

    startWorkflowAndWaitUntilReady(workflow, input);

    // wait for workflow to initialize
    testEnv.sleep(Duration.ofMinutes(1));

    workflow.submitManualSync();

    // wait for the manual sync to start working
    testEnv.sleep(Duration.ofMinutes(1));

    workflow.deleteConnection();

    Thread.sleep(500);

    final Queue<ChangedStateEvent> eventQueue = testStateListener.events(testId);
    final List<ChangedStateEvent> events = new ArrayList<>(eventQueue);

    for (final ChangedStateEvent event : events) {
      if (event.isValue()) {
        log.info(EVENT + event);
      }
    }

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.CANCELLED && changedStateEvent.isValue())
        .hasSizeGreaterThanOrEqualTo(1);

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.DELETED && changedStateEvent.isValue())
        .hasSizeGreaterThanOrEqualTo(1);

    Mockito.verify(mJobCreationAndStatusUpdateActivity)
        .jobCancelledWithAttemptNumber(Mockito.argThat(new HasCancellationFailure(JOB_ID, ATTEMPT_ID)));
  }

  @Test
  @Timeout(value = 10,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test that resetting a non-running workflow starts a reset job")
  void resetStart() throws InterruptedException {

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
        .build();

    startWorkflowAndWaitUntilReady(workflow, input);
    testEnv.sleep(Duration.ofMinutes(5L));
    workflow.resetConnection();
    Thread.sleep(500);

    final Queue<ChangedStateEvent> events = testStateListener.events(testId);

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.SKIPPED_SCHEDULING && changedStateEvent.isValue())
        .hasSizeGreaterThanOrEqualTo(1);

  }

  @Test
  @Timeout(value = 60,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test that resetting a running workflow cancels the running workflow")
  void resetCancelRunningWorkflow() throws InterruptedException {

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
        .build();

    startWorkflowAndWaitUntilReady(workflow, input);

    testEnv.sleep(Duration.ofSeconds(30L));
    workflow.submitManualSync();
    testEnv.sleep(Duration.ofSeconds(30L));
    workflow.resetConnection();
    Thread.sleep(500);

    final Queue<ChangedStateEvent> eventQueue = testStateListener.events(testId);
    final List<ChangedStateEvent> events = new ArrayList<>(eventQueue);

    for (final ChangedStateEvent event : events) {
      if (event.isValue()) {
        log.info(EVENT + event);
      }
    }

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.CANCELLED_FOR_RESET && changedStateEvent.isValue())
        .hasSizeGreaterThanOrEqualTo(1);

    Mockito.verify(mJobCreationAndStatusUpdateActivity).jobCancelledWithAttemptNumber(Mockito.any(JobCancelledInputWithAttemptNumber.class));

  }

  @Test
  @Timeout(value = 60,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test that cancelling a reset deletes streamsToReset from stream_resets table")
  void cancelResetRemovesStreamsToReset() throws InterruptedException {
    final UUID connectionId = UUID.randomUUID();
    final UUID testId = UUID.randomUUID();
    final TestStateListener testStateListener = new TestStateListener();
    final WorkflowState workflowState = new WorkflowState(testId, testStateListener);

    final ConnectionUpdaterInput input = Mockito.spy(ConnectionUpdaterInput.builder()
        .connectionId(connectionId)
        .jobId(JOB_ID)
        .attemptId(ATTEMPT_ID)
        .fromFailure(false)
        .attemptNumber(1)
        .workflowState(workflowState)
        .skipScheduling(true)
        .build());

    startWorkflowAndWaitUntilReady(workflow, input);

    testEnv.sleep(Duration.ofSeconds(30L));
    workflow.cancelJob();
    Thread.sleep(500);

    Mockito.verify(mStreamResetActivity).deleteStreamResetRecordsForJob(new DeleteStreamResetRecordsForJobInput(connectionId, JOB_ID));
  }

  @Test
  @DisplayName("Test that running workflow which receives an update signal waits for the current run and reports the job status")
  void updatedSignalReceivedWhileRunning() throws InterruptedException {

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
        log.info(EVENT + event);
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
