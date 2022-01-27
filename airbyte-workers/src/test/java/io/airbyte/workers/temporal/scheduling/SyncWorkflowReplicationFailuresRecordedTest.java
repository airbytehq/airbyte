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
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.DbtFailureSyncWorkflow;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.NormalizationFailureSyncWorkflow;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.PersistFailureSyncWorkflow;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.ReplicateFailureSyncWorkflow;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.SourceAndDestinationFailureSyncWorkflow;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.testing.TestWorkflowEnvironment;
import io.temporal.worker.Worker;
import java.time.Duration;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentMatcher;
import org.mockito.Mockito;

public class SyncWorkflowReplicationFailuresRecordedTest {
  private static final long JOB_ID = 111L;
  private static final int ATTEMPT_ID = 222;
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
  public void setup() {
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

    Mockito.verify(mJobCreationAndStatusUpdateActivity).attemptFailure(Mockito.argThat(new HasFailureFromSource(FailureOrigin.REPLICATION_WORKER)));

    testEnv.shutdown();
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
