package io.airbyte.workers.temporal.scheduling.connection.manager;

import static org.mockito.Mockito.atLeastOnce;

import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.ConnectorJobOutput.OutputType;
import io.airbyte.config.FailureReason;
import io.airbyte.config.FailureReason.FailureOrigin;
import io.airbyte.config.FailureReason.FailureType;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.workers.temporal.TemporalJobType;
import io.airbyte.workers.temporal.scheduling.ConnectionManagerWorkflow;
import io.airbyte.workers.temporal.scheduling.ConnectionManagerWorkflowImpl;
import io.airbyte.workers.temporal.scheduling.ConnectionUpdaterInput;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity.GetMaxAttemptOutput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.AttemptNumberCreationOutput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobCreationOutput;
import io.airbyte.workers.temporal.scheduling.state.WorkflowState;
import io.airbyte.workers.temporal.scheduling.state.listener.TestStateListener;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.DbtFailureSyncWorkflow;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.NormalizationFailureSyncWorkflow;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.NormalizationTraceFailureSyncWorkflow;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.PersistFailureSyncWorkflow;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.ReplicateFailureSyncWorkflow;
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

public class SyncWorkflowReplicationFailuresRecorded extends BaseConnectionManagerWorkflowTest {

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
  @DisplayName("Test that Source CHECK failures are recorded")
  void testSourceCheckFailuresRecorded() throws InterruptedException {
    Mockito.when(mJobCreationAndStatusUpdateActivity.createNewJob(Mockito.any()))
        .thenReturn(new JobCreationOutput(JOB_ID));
    Mockito.when(mJobCreationAndStatusUpdateActivity.createNewAttemptNumber(Mockito.any()))
        .thenReturn(new AttemptNumberCreationOutput(ATTEMPT_ID));
    Mockito.when(mCheckConnectionActivity.runWithJobOutput(Mockito.any()))
        .thenReturn(new ConnectorJobOutput().withOutputType(OutputType.CHECK_CONNECTION)
            .withCheckConnection(new StandardCheckConnectionOutput().withStatus(Status.FAILED).withMessage("nope")));

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
        .build();

    startWorkflowAndWaitUntilReady(workflow, input);

    // wait for workflow to initialize
    testEnv.sleep(Duration.ofMinutes(1));

    workflow.submitManualSync();
    Thread.sleep(500); // any time after no-waiting manual run

    Mockito.verify(mJobCreationAndStatusUpdateActivity)
        .attemptFailureWithAttemptNumber(Mockito.argThat(new HasFailureFromOriginWithType(FailureOrigin.SOURCE, FailureType.CONFIG_ERROR)));
  }

  @Test
  @Timeout(value = 10,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test that Source CHECK failure reasons are recorded")
  void testSourceCheckFailureReasonsRecorded() throws InterruptedException {
    Mockito.when(mJobCreationAndStatusUpdateActivity.createNewJob(Mockito.any()))
        .thenReturn(new JobCreationOutput(JOB_ID));
    Mockito.when(mJobCreationAndStatusUpdateActivity.createNewAttemptNumber(Mockito.any()))
        .thenReturn(new AttemptNumberCreationOutput(ATTEMPT_ID));
    Mockito.when(mCheckConnectionActivity.runWithJobOutput(Mockito.any()))
        .thenReturn(new ConnectorJobOutput().withOutputType(OutputType.CHECK_CONNECTION)
            .withFailureReason(new FailureReason().withFailureType(FailureType.SYSTEM_ERROR)));

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
        .build();

    startWorkflowAndWaitUntilReady(workflow, input);

    // wait for workflow to initialize
    testEnv.sleep(Duration.ofMinutes(1));

    workflow.submitManualSync();
    Thread.sleep(500); // any time after no-waiting manual run

    Mockito.verify(mJobCreationAndStatusUpdateActivity)
        .attemptFailureWithAttemptNumber(Mockito.argThat(new HasFailureFromOriginWithType(FailureOrigin.SOURCE, FailureType.SYSTEM_ERROR)));
  }

  @Test
  @Timeout(value = 10,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test that Destination CHECK failures are recorded")
  void testDestinationCheckFailuresRecorded() throws InterruptedException {
    Mockito.when(mJobCreationAndStatusUpdateActivity.createNewJob(Mockito.any()))
        .thenReturn(new JobCreationOutput(JOB_ID));
    Mockito.when(mJobCreationAndStatusUpdateActivity.createNewAttemptNumber(Mockito.any()))
        .thenReturn(new AttemptNumberCreationOutput(ATTEMPT_ID));
    Mockito.when(mCheckConnectionActivity.runWithJobOutput(Mockito.any()))
        // First call (source) succeeds
        .thenReturn(new ConnectorJobOutput().withOutputType(OutputType.CHECK_CONNECTION)
            .withCheckConnection(new StandardCheckConnectionOutput().withStatus(Status.SUCCEEDED).withMessage("all good")))

        // Second call (destination) fails
        .thenReturn(new ConnectorJobOutput().withOutputType(OutputType.CHECK_CONNECTION)
            .withCheckConnection(new StandardCheckConnectionOutput().withStatus(Status.FAILED).withMessage("nope")));

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
        .build();

    startWorkflowAndWaitUntilReady(workflow, input);

    // wait for workflow to initialize
    testEnv.sleep(Duration.ofMinutes(1));

    workflow.submitManualSync();
    Thread.sleep(500); // any time after no-waiting manual run

    Mockito.verify(mJobCreationAndStatusUpdateActivity)
        .attemptFailureWithAttemptNumber(Mockito.argThat(new HasFailureFromOriginWithType(FailureOrigin.DESTINATION, FailureType.CONFIG_ERROR)));
  }

  @Test
  @Timeout(value = 10,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test that Destination CHECK failure reasons are recorded")
  void testDestinationCheckFailureReasonsRecorded() throws InterruptedException {
    Mockito.when(mJobCreationAndStatusUpdateActivity.createNewJob(Mockito.any()))
        .thenReturn(new JobCreationOutput(JOB_ID));
    Mockito.when(mJobCreationAndStatusUpdateActivity.createNewAttemptNumber(Mockito.any()))
        .thenReturn(new AttemptNumberCreationOutput(ATTEMPT_ID));
    Mockito.when(mCheckConnectionActivity.runWithJobOutput(Mockito.any()))
        // First call (source) succeeds
        .thenReturn(new ConnectorJobOutput().withOutputType(OutputType.CHECK_CONNECTION)
            .withCheckConnection(new StandardCheckConnectionOutput().withStatus(Status.SUCCEEDED).withMessage("all good")))

        // Second call (destination) fails
        .thenReturn(new ConnectorJobOutput().withOutputType(OutputType.CHECK_CONNECTION)
            .withFailureReason(new FailureReason().withFailureType(FailureType.SYSTEM_ERROR)));

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
        .build();

    startWorkflowAndWaitUntilReady(workflow, input);

    // wait for workflow to initialize
    testEnv.sleep(Duration.ofMinutes(1));

    workflow.submitManualSync();
    Thread.sleep(500); // any time after no-waiting manual run

    Mockito.verify(mJobCreationAndStatusUpdateActivity)
        .attemptFailureWithAttemptNumber(Mockito.argThat(new HasFailureFromOriginWithType(FailureOrigin.DESTINATION, FailureType.SYSTEM_ERROR)));
  }

  @Test
  @Timeout(value = 10,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test that reset workflows do not CHECK the source")
  void testSourceCheckSkippedWhenReset() throws InterruptedException {
    Mockito.when(mJobCreationAndStatusUpdateActivity.createNewJob(Mockito.any()))
        .thenReturn(new JobCreationOutput(JOB_ID));
    Mockito.when(mJobCreationAndStatusUpdateActivity.createNewAttemptNumber(Mockito.any()))
        .thenReturn(new AttemptNumberCreationOutput(ATTEMPT_ID));
    mockResetJobInput();
    Mockito.when(mCheckConnectionActivity.runWithJobOutput(Mockito.any()))
        // first call, but should fail destination because source check is skipped
        .thenReturn(new ConnectorJobOutput().withOutputType(OutputType.CHECK_CONNECTION)
            .withCheckConnection(new StandardCheckConnectionOutput().withStatus(Status.FAILED).withMessage("nope")));

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
        .build();

    startWorkflowAndWaitUntilReady(workflow, input);

    // wait for workflow to initialize
    testEnv.sleep(Duration.ofMinutes(1));

    workflow.submitManualSync();
    Thread.sleep(500); // any time after no-waiting manual run

    Mockito.verify(mJobCreationAndStatusUpdateActivity, atLeastOnce())
        .attemptFailureWithAttemptNumber(Mockito.argThat(new HasFailureFromOriginWithType(FailureOrigin.DESTINATION, FailureType.CONFIG_ERROR)));
  }

  @Test
  @Timeout(value = 10,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test that source and destination failures are recorded")
  void testSourceAndDestinationFailuresRecorded() throws InterruptedException {
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
        .build();

    startWorkflowAndWaitUntilReady(workflow, input);

    // wait for workflow to initialize
    testEnv.sleep(Duration.ofMinutes(1));

    workflow.submitManualSync();
    Thread.sleep(500); // any time after no-waiting manual run

    Mockito.verify(mJobCreationAndStatusUpdateActivity)
        .attemptFailureWithAttemptNumber(Mockito.argThat(new HasFailureFromOrigin(FailureOrigin.SOURCE)));
    Mockito.verify(mJobCreationAndStatusUpdateActivity)
        .attemptFailureWithAttemptNumber(Mockito.argThat(new HasFailureFromOrigin(FailureOrigin.DESTINATION)));
  }

  @Test
  @Timeout(value = 10,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test that normalization failure is recorded")
  void testNormalizationFailure() throws InterruptedException {
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
        .build();

    startWorkflowAndWaitUntilReady(workflow, input);

    // wait for workflow to initialize
    testEnv.sleep(Duration.ofMinutes(1));

    workflow.submitManualSync();
    Thread.sleep(500); // any time after no-waiting manual run

    Mockito.verify(mJobCreationAndStatusUpdateActivity)
        .attemptFailureWithAttemptNumber(Mockito.argThat(new HasFailureFromOrigin(FailureOrigin.NORMALIZATION)));
  }

  @Test
  @Timeout(value = 10,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test that normalization trace failure is recorded")
  void testNormalizationTraceFailure() throws InterruptedException {
    final Worker syncWorker = testEnv.newWorker(TemporalJobType.SYNC.name());
    syncWorker.registerWorkflowImplementationTypes(NormalizationTraceFailureSyncWorkflow.class);

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
        .build();

    startWorkflowAndWaitUntilReady(workflow, input);

    // wait for workflow to initialize
    testEnv.sleep(Duration.ofMinutes(1));

    workflow.submitManualSync();
    Thread.sleep(500); // any time after no-waiting manual run

    Mockito.verify(mJobCreationAndStatusUpdateActivity)
        .attemptFailureWithAttemptNumber(Mockito.argThat(new HasFailureFromOrigin(FailureOrigin.NORMALIZATION)));
  }

  @Test
  @Timeout(value = 10,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test that dbt failure is recorded")
  void testDbtFailureRecorded() throws InterruptedException {
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
        .build();

    startWorkflowAndWaitUntilReady(workflow, input);

    // wait for workflow to initialize
    testEnv.sleep(Duration.ofMinutes(1));

    workflow.submitManualSync();
    Thread.sleep(500); // any time after no-waiting manual run

    Mockito.verify(mJobCreationAndStatusUpdateActivity)
        .attemptFailureWithAttemptNumber(Mockito.argThat(new HasFailureFromOrigin(FailureOrigin.DBT)));
  }

  @Test
  @Timeout(value = 10,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test that persistence failure is recorded")
  void testPersistenceFailureRecorded() throws InterruptedException {
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
        .build();

    startWorkflowAndWaitUntilReady(workflow, input);

    // wait for workflow to initialize
    testEnv.sleep(Duration.ofMinutes(1));

    workflow.submitManualSync();
    Thread.sleep(500); // any time after no-waiting manual run

    Mockito.verify(mJobCreationAndStatusUpdateActivity)
        .attemptFailureWithAttemptNumber(Mockito.argThat(new HasFailureFromOrigin(FailureOrigin.PERSISTENCE)));
  }

  @Test
  @Timeout(value = 10,
      unit = TimeUnit.SECONDS)
  @DisplayName("Test that replication worker failure is recorded")
  void testReplicationFailureRecorded() throws InterruptedException {
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
        .build();

    startWorkflowAndWaitUntilReady(workflow, input);

    // wait for workflow to initialize
    testEnv.sleep(Duration.ofMinutes(1));

    workflow.submitManualSync();
    Thread.sleep(500); // any time after no-waiting manual run

    Mockito.verify(mJobCreationAndStatusUpdateActivity)
        .attemptFailureWithAttemptNumber(Mockito.argThat(new HasFailureFromOrigin(FailureOrigin.REPLICATION)));
  }

}
