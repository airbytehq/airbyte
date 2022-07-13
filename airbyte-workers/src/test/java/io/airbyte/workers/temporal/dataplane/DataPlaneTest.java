/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.dataplane;

import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.temporal.TemporalJobType;
import io.airbyte.workers.temporal.check.connection.CheckConnectionActivity;
import io.airbyte.workers.temporal.scheduling.ConnectionManagerWorkflow;
import io.airbyte.workers.temporal.scheduling.ConnectionManagerWorkflowImpl;
import io.airbyte.workers.temporal.scheduling.ConnectionUpdaterInput;
import io.airbyte.workers.temporal.scheduling.activities.AutoDisableConnectionActivity;
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
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobCreationOutput;
import io.airbyte.workers.temporal.scheduling.activities.StreamResetActivity;
import io.airbyte.workers.temporal.scheduling.state.WorkflowState;
import io.airbyte.workers.temporal.scheduling.state.listener.TestStateListener;
import io.airbyte.workers.temporal.sync.DbtTransformationActivity;
import io.airbyte.workers.temporal.sync.NormalizationActivity;
import io.airbyte.workers.temporal.sync.PersistStateActivity;
import io.airbyte.workers.temporal.sync.ReplicationActivity;
import io.airbyte.workers.temporal.sync.ReplicationActivityImpl;
import io.airbyte.workers.temporal.sync.SyncWorkflowImpl;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.testing.TestWorkflowEnvironment;
import io.temporal.worker.Worker;
import java.time.Duration;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

@Slf4j
public class DataPlaneTest {

  private TestWorkflowEnvironment testEnv;
  private WorkflowClient client;
  private ConnectionManagerWorkflow cmWorkflow;

  private final String CONTROL_PLANE = "CONTROL_PLANE";
  private final String DATA_PLANE_A = "DATA_PLANE_A";
  private final String DATA_PLANE_B = "DATA_PLANE_B";
  private static final String WORKFLOW_ID = "workflow-id";
  private static final long JOB_ID = 1L;
  private static final int ATTEMPT_ID = 1;

  private static final Duration SCHEDULE_WAIT = Duration.ofMinutes(20L);

  // ConnectionManager activities
  private final ConfigFetchActivity mConfigFetchActivity =
      Mockito.mock(ConfigFetchActivity.class, Mockito.withSettings().withoutAnnotations());
  private final CheckConnectionActivity mCheckConnectionActivity =
      Mockito.mock(CheckConnectionActivity.class, Mockito.withSettings().withoutAnnotations());
  private static final ConnectionDeletionActivity mConnectionDeletionActivity =
      Mockito.mock(ConnectionDeletionActivity.class, Mockito.withSettings().withoutAnnotations());
  private static final GenerateInputActivityImpl mGenerateInputActivityImpl =
      Mockito.mock(GenerateInputActivityImpl.class, Mockito.withSettings().withoutAnnotations());
  private static final JobCreationAndStatusUpdateActivity mJobCreationAndStatusUpdateActivity =
      Mockito.mock(JobCreationAndStatusUpdateActivity.class, Mockito.withSettings().withoutAnnotations());
  private static final AutoDisableConnectionActivity mAutoDisableConnectionActivity =
      Mockito.mock(AutoDisableConnectionActivity.class, Mockito.withSettings().withoutAnnotations());
  private static final StreamResetActivity mStreamResetActivity =
      Mockito.mock(StreamResetActivity.class, Mockito.withSettings().withoutAnnotations());

  // Sync activities
  private final ReplicationActivity mReplicationActivity =
      Mockito.mock(ReplicationActivity.class, Mockito.withSettings().withoutAnnotations());
  private final NormalizationActivity mNormalizationActivity =
      Mockito.mock(NormalizationActivity.class, Mockito.withSettings().withoutAnnotations());
  private static final DbtTransformationActivity mDbtTransformationActivity =
      Mockito.mock(DbtTransformationActivity.class, Mockito.withSettings().withoutAnnotations());
  private static final PersistStateActivity mPersistStateActivity =
      Mockito.mock(PersistStateActivity.class, Mockito.withSettings().withoutAnnotations());

  @BeforeEach
  public void setUp() {
    Mockito.reset(mConfigFetchActivity);
    Mockito.reset(mCheckConnectionActivity);
    Mockito.reset(mConnectionDeletionActivity);
    Mockito.reset(mGenerateInputActivityImpl);
    Mockito.reset(mJobCreationAndStatusUpdateActivity);
    Mockito.reset(mAutoDisableConnectionActivity);
    Mockito.reset(mStreamResetActivity);
    Mockito.reset(mReplicationActivity);
    Mockito.reset(mNormalizationActivity);
    Mockito.reset(mDbtTransformationActivity);
    Mockito.reset(mPersistStateActivity);

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
                new IntegrationLauncherConfig().withDockerImage("some_source"),
                new IntegrationLauncherConfig(),
                new StandardSyncInput()));

    Mockito.when(mCheckConnectionActivity.run(Mockito.any()))
        .thenReturn(new StandardCheckConnectionOutput().withStatus(Status.SUCCEEDED).withMessage("check worked"));

    Mockito.when(mAutoDisableConnectionActivity.autoDisableFailingConnection(Mockito.any()))
        .thenReturn(new AutoDisableConnectionOutput(false));
  }

  @AfterEach
  public void tearDown() {
    testEnv.shutdown();
    TestStateListener.reset();
  }

  @Test
  public void test() throws InterruptedException {
    testEnv = TestWorkflowEnvironment.newInstance();
    final Worker cpWorker = testEnv.newWorker(TemporalJobType.CONNECTION_UPDATER.name());
    final Worker syncWorker = testEnv.newWorker(TemporalJobType.SYNC.name());

    final Worker dpAWorkflowWorker = testEnv.newWorker(DATA_PLANE_A);
    final Worker dpAActivityWorker = testEnv.newWorker(DATA_PLANE_A);

    final Worker dpBWorkflowWorker = testEnv.newWorker(DATA_PLANE_B);
    final Worker dpBActivityWorker = testEnv.newWorker(DATA_PLANE_B);

    cpWorker.registerWorkflowImplementationTypes(ConnectionManagerWorkflowImpl.class);
    cpWorker.registerActivitiesImplementations(mConfigFetchActivity, mCheckConnectionActivity, mConnectionDeletionActivity,
        mGenerateInputActivityImpl, mJobCreationAndStatusUpdateActivity, mAutoDisableConnectionActivity, mStreamResetActivity);

    syncWorker.registerWorkflowImplementationTypes(SyncWorkflowImpl.class);

    // dpAActivityWorker.registerActivitiesImplementations(mReplicationActivity, mNormalizationActivity,
    // mDbtTransformationActivity, mPersistStateActivity);

    dpBActivityWorker.registerActivitiesImplementations(ReplicationActivityImpl.class, mNormalizationActivity, mDbtTransformationActivity,
        mPersistStateActivity);

    client = testEnv.getWorkflowClient();
    testEnv.start();

    cmWorkflow = client.newWorkflowStub(
        ConnectionManagerWorkflow.class,
        WorkflowOptions.newBuilder()
            .setTaskQueue(TemporalJobType.CONNECTION_UPDATER.name())
            .setWorkflowId(WORKFLOW_ID)
            .build());

    Mockito.when(mConfigFetchActivity.getTimeToWait(Mockito.any()))
        .thenReturn(new ScheduleRetrieverOutput(SCHEDULE_WAIT));
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
        .build();

    startWorkflowAndWaitUntilReady(cmWorkflow, input);

    System.err.println("Started cm workflow, about to sleep");
    testEnv.sleep(Duration.ofMinutes(SCHEDULE_WAIT.toMinutes() + SCHEDULE_WAIT.toMinutes() + 1));

    System.err.println("Finished sleep");
    Mockito.verify(mReplicationActivity, Mockito.atLeast(1)).replicate(Mockito.any(), Mockito.any(), Mockito.any(), Mockito.any());

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

}
