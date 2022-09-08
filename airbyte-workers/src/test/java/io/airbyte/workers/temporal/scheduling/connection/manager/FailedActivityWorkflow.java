package io.airbyte.workers.temporal.scheduling.connection.manager;

import io.airbyte.workers.temporal.scheduling.ConnectionManagerWorkflowImpl;
import io.airbyte.workers.temporal.scheduling.ConnectionUpdaterInput;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity.ScheduleRetrieverOutput;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivity.SyncInputWithAttemptNumber;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobCreationOutput;
import io.airbyte.workers.temporal.scheduling.state.WorkflowState;
import io.airbyte.workers.temporal.scheduling.state.listener.TestStateListener;
import io.airbyte.workers.temporal.scheduling.state.listener.WorkflowStateChangedListener.ChangedStateEvent;
import io.airbyte.workers.temporal.scheduling.state.listener.WorkflowStateChangedListener.StateField;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.SleepingSyncWorkflow;
import io.temporal.failure.ApplicationFailure;
import java.time.Duration;
import java.util.Queue;
import java.util.UUID;
import java.util.stream.Stream;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.mockito.Mockito;

public class FailedActivityWorkflow extends BaseConnectionManagerWorkflowTest {

  @BeforeEach
  void setup() {
    setupSpecificChildWorkflow(SleepingSyncWorkflow.class);
  }

  static Stream<Arguments> getSetupFailingActivity() {
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
  @MethodSource("getSetupFailingActivity")
  void testWorkflowRestartedAfterFailedActivity(final Thread mockSetup) throws InterruptedException {
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
        .build();

    startWorkflowAndWaitUntilReady(workflow, input);

    // Sleep test env for restart delay, plus a small buffer to ensure that the workflow executed the
    // logic after the delay
    testEnv.sleep(ConnectionManagerWorkflowImpl.WORKFLOW_FAILURE_RESTART_DELAY.plus(Duration.ofSeconds(10)));

    final Queue<ChangedStateEvent> events = testStateListener.events(testId);

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RUNNING && changedStateEvent.isValue())
        .isEmpty();

    assertWorkflowWasContinuedAsNew();
  }

  @Test
  void testCanRetryFailedActivity() throws InterruptedException {
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
        .build();

    startWorkflowAndWaitUntilReady(workflow, input);

    // Sleep test env for half of restart delay, so that we know we are in the middle of the delay
    testEnv.sleep(ConnectionManagerWorkflowImpl.WORKFLOW_FAILURE_RESTART_DELAY.dividedBy(2));
    workflow.retryFailedActivity();
    Thread.sleep(500); // any time after no-waiting manual run

    final Queue<ChangedStateEvent> events = testStateListener.events(testId);

    Assertions.assertThat(events)
        .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RETRY_FAILED_ACTIVITY && changedStateEvent.isValue())
        .hasSize(1);
  }

}
