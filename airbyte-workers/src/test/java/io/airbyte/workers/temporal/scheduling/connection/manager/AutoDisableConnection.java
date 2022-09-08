package io.airbyte.workers.temporal.scheduling.connection.manager;

import static org.mockito.Mockito.atLeastOnce;

import io.airbyte.workers.temporal.TemporalJobType;
import io.airbyte.workers.temporal.scheduling.ConnectionManagerWorkflow;
import io.airbyte.workers.temporal.scheduling.ConnectionManagerWorkflowImpl;
import io.airbyte.workers.temporal.scheduling.ConnectionUpdaterInput;
import io.airbyte.workers.temporal.scheduling.activities.AutoDisableConnectionActivity.AutoDisableConnectionActivityInput;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity.GetMaxAttemptOutput;
import io.airbyte.workers.temporal.scheduling.state.WorkflowState;
import io.airbyte.workers.temporal.scheduling.state.listener.TestStateListener;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.EmptySyncWorkflow;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.SourceAndDestinationFailureSyncWorkflow;
import io.temporal.client.WorkflowOptions;
import io.temporal.testing.TestWorkflowEnvironment;
import io.temporal.worker.Worker;
import java.time.Duration;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.mockito.Mockito;

public class AutoDisableConnection extends BaseConnectionManagerWorkflowTest {

  private static final long JOB_ID = 111L;
  private static final int ATTEMPT_ID = 222;

  @BeforeEach
  void setup() {
    testEnv = TestWorkflowEnvironment.newInstance();

    final Worker managerWorker = testEnv.newWorker(TemporalJobType.CONNECTION_UPDATER.name());
    managerWorker.registerWorkflowImplementationTypes(ConnectionManagerWorkflowImpl.class);
    managerWorker.registerActivitiesImplementations(mConfigFetchActivity, mCheckConnectionActivity, mConnectionDeletionActivity,
        mGenerateInputActivityImpl, mJobCreationAndStatusUpdateActivity, mAutoDisableConnectionActivity);

    client = testEnv.getWorkflowClient();
    workflow = client.newWorkflowStub(ConnectionManagerWorkflow.class,
        WorkflowOptions.newBuilder().setTaskQueue(TemporalJobType.CONNECTION_UPDATER.name()).build());

    Mockito.when(mConfigFetchActivity.getMaxAttempt()).thenReturn(new GetMaxAttemptOutput(1));
  }

  @Test
  @Timeout(value = 10,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test that auto disable activity is touched during failure")
  void testAutoDisableOnFailure() throws InterruptedException {
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
        .build();

    startWorkflowAndWaitUntilReady(workflow, input);

    // wait for workflow to initialize
    testEnv.sleep(Duration.ofMinutes(1));

    workflow.submitManualSync();
    Thread.sleep(500); // any time after no-waiting manual run

    Mockito.verify(mJobCreationAndStatusUpdateActivity, atLeastOnce()).attemptFailureWithAttemptNumber(Mockito.any());
    Mockito.verify(mJobCreationAndStatusUpdateActivity, atLeastOnce()).jobFailure(Mockito.any());
    Mockito.verify(mAutoDisableConnectionActivity)
        .autoDisableFailingConnection(new AutoDisableConnectionActivityInput(connectionId, Mockito.any()));
  }

  @Test
  @Timeout(value = 10,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test that auto disable activity is not touched during job success")
  void testNoAutoDisableOnSuccess() throws InterruptedException {
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
        .build();

    startWorkflowAndWaitUntilReady(workflow, input);

    // wait for workflow to initialize
    testEnv.sleep(Duration.ofMinutes(1));

    workflow.submitManualSync();
    Thread.sleep(500); // any time after no-waiting manual run
    Mockito.verifyNoInteractions(mAutoDisableConnectionActivity);
  }

}
