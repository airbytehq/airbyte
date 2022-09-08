package io.airbyte.workers.temporal.scheduling.connection.manager;

import io.airbyte.workers.temporal.scheduling.ConnectionUpdaterInput;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity.ScheduleRetrieverOutput;
import io.airbyte.workers.temporal.scheduling.state.WorkflowState;
import io.airbyte.workers.temporal.scheduling.state.listener.TestStateListener;
import io.airbyte.workers.temporal.scheduling.state.listener.WorkflowStateChangedListener.ChangedStateEvent;
import io.airbyte.workers.temporal.scheduling.state.listener.WorkflowStateChangedListener.StateField;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.EmptySyncWorkflow;
import java.time.Duration;
import java.util.Queue;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.mockito.Mockito;

public class AsynchronousWorkflow extends BaseConnectionManagerWorkflowTest {

  @BeforeEach
  void setup() {
    setupSpecificChildWorkflow(EmptySyncWorkflow.class);
  }

  @Test
  @Timeout(value = 10,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test that a successful workflow retries and waits")
  void runSuccess() throws InterruptedException {
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
    // wait to be scheduled, then to run, then schedule again
    testEnv.sleep(Duration.ofMinutes(SCHEDULE_WAIT.toMinutes() + SCHEDULE_WAIT.toMinutes() + 1));
    Mockito.verify(mConfigFetchActivity, Mockito.atLeast(2)).getTimeToWait(Mockito.any());
    final Queue<ChangedStateEvent> events = testStateListener.events(testId);

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RUNNING && changedStateEvent.isValue())
        .hasSize(2);

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.DONE_WAITING && changedStateEvent.isValue())
        .hasSize(2);

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> (changedStateEvent.getField() != StateField.RUNNING
            && changedStateEvent.getField() != StateField.SUCCESS
            && changedStateEvent.getField() != StateField.DONE_WAITING)
            && changedStateEvent.isValue())
        .isEmpty();
  }

  @Test
  @Timeout(value = 10,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test workflow does not wait to run after a failure")
  void retryAfterFail() throws InterruptedException {
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
        .build();

    startWorkflowAndWaitUntilReady(workflow, input);
    testEnv.sleep(Duration.ofMinutes(SCHEDULE_WAIT.toMinutes() - 1));
    final Queue<ChangedStateEvent> events = testStateListener.events(testId);

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RUNNING && changedStateEvent.isValue())
        .hasSize(1);

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.DONE_WAITING && changedStateEvent.isValue())
        .hasSize(1);

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> (changedStateEvent.getField() != StateField.RUNNING
            && changedStateEvent.getField() != StateField.SUCCESS
            && changedStateEvent.getField() != StateField.DONE_WAITING)
            && changedStateEvent.isValue())
        .isEmpty();
  }

  @Test
  @Timeout(value = 10,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test workflow which receives a manual run signal stops waiting")
  void manualRun() throws InterruptedException {

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
    testEnv.sleep(Duration.ofMinutes(1L)); // any value here, just so it's started
    workflow.submitManualSync();
    Thread.sleep(500);

    final Queue<ChangedStateEvent> events = testStateListener.events(testId);

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RUNNING && changedStateEvent.isValue())
        .hasSize(1);

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.SKIPPED_SCHEDULING && changedStateEvent.isValue())
        .hasSize(1);

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.DONE_WAITING && changedStateEvent.isValue())
        .hasSize(1);

    Assertions.assertThat(events)
        .filteredOn(
            changedStateEvent -> (changedStateEvent.getField() != StateField.RUNNING
                && changedStateEvent.getField() != StateField.SKIPPED_SCHEDULING
                && changedStateEvent.getField() != StateField.SUCCESS
                && changedStateEvent.getField() != StateField.DONE_WAITING)
                && changedStateEvent.isValue())
        .isEmpty();
  }

  @Test
  @Timeout(value = 10,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test workflow which receives an update signal stops waiting, doesn't run, and doesn't update the job status")
  void updatedSignalReceived() throws InterruptedException {

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
    workflow.connectionUpdated();
    Thread.sleep(500);

    final Queue<ChangedStateEvent> events = testStateListener.events(testId);

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RUNNING && changedStateEvent.isValue())
        .isEmpty();

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.UPDATED && changedStateEvent.isValue())
        .hasSize(1);

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.DONE_WAITING && changedStateEvent.isValue())
        .hasSize(1);

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> (changedStateEvent.getField() != StateField.UPDATED
            && changedStateEvent.getField() != StateField.SUCCESS
            && changedStateEvent.getField() != StateField.DONE_WAITING)
            && changedStateEvent.isValue())
        .isEmpty();

    Mockito.verifyNoInteractions(mJobCreationAndStatusUpdateActivity);
  }

  @Test
  @Timeout(value = 10,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test that cancelling a non-running workflow doesn't do anything")
  void cancelNonRunning() throws InterruptedException {

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

  @Test
  @Timeout(value = 10,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test that the sync is properly deleted")
  void deleteSync() throws InterruptedException {

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
    workflow.deleteConnection();
    Thread.sleep(500);

    final Queue<ChangedStateEvent> events = testStateListener.events(testId);

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RUNNING && changedStateEvent.isValue())
        .isEmpty();

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.DELETED && changedStateEvent.isValue())
        .hasSize(1);

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.DONE_WAITING && changedStateEvent.isValue())
        .hasSize(1);

    Assertions.assertThat(events)
        .filteredOn(
            changedStateEvent -> changedStateEvent.getField() != StateField.DELETED
                && changedStateEvent.getField() != StateField.SUCCESS
                && changedStateEvent.getField() != StateField.DONE_WAITING
                && changedStateEvent.isValue())
        .isEmpty();

    Mockito.verify(mConnectionDeletionActivity, Mockito.times(1)).deleteConnection(Mockito.any());
  }

  @Test
  @Timeout(value = 10,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test that fresh workflow cleans the job state")
  void testStartFromCleanJobState() throws InterruptedException {
    final ConnectionUpdaterInput input = ConnectionUpdaterInput.builder()
        .connectionId(UUID.randomUUID())
        .jobId(null)
        .attemptId(null)
        .fromFailure(false)
        .attemptNumber(1)
        .workflowState(null)
        .build();

    startWorkflowAndWaitUntilReady(workflow, input);
    testEnv.sleep(Duration.ofSeconds(30L));

    Mockito.verify(mJobCreationAndStatusUpdateActivity, Mockito.times(1)).ensureCleanJobState(Mockito.any());
  }

}
