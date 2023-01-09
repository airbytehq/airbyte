/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import static org.mockito.Mockito.atLeastOnce;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.commons.temporal.TemporalJobType;
import io.airbyte.commons.temporal.scheduling.ConnectionManagerWorkflow;
import io.airbyte.commons.temporal.scheduling.ConnectionUpdaterInput;
import io.airbyte.commons.temporal.scheduling.SyncWorkflow;
import io.airbyte.commons.temporal.scheduling.state.WorkflowState;
import io.airbyte.commons.temporal.scheduling.state.listener.TestStateListener;
import io.airbyte.commons.temporal.scheduling.state.listener.WorkflowStateChangedListener.ChangedStateEvent;
import io.airbyte.commons.temporal.scheduling.state.listener.WorkflowStateChangedListener.StateField;
import io.airbyte.commons.version.Version;
import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.ConnectorJobOutput.OutputType;
import io.airbyte.config.FailureReason;
import io.airbyte.config.FailureReason.FailureOrigin;
import io.airbyte.config.FailureReason.FailureType;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.temporal.check.connection.CheckConnectionActivity;
import io.airbyte.workers.temporal.scheduling.activities.AutoDisableConnectionActivity;
import io.airbyte.workers.temporal.scheduling.activities.AutoDisableConnectionActivity.AutoDisableConnectionActivityInput;
import io.airbyte.workers.temporal.scheduling.activities.AutoDisableConnectionActivity.AutoDisableConnectionOutput;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity.GetMaxAttemptOutput;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity.ScheduleRetrieverOutput;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivity.GeneratedJobInput;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivity.SyncInputWithAttemptNumber;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivityImpl;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.AttemptNumberCreationOutput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.AttemptNumberFailureInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobCancelledInputWithAttemptNumber;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobCreationOutput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobSuccessInputWithAttemptNumber;
import io.airbyte.workers.temporal.scheduling.activities.RecordMetricActivity;
import io.airbyte.workers.temporal.scheduling.activities.RouteToSyncTaskQueueActivity;
import io.airbyte.workers.temporal.scheduling.activities.RouteToSyncTaskQueueActivity.RouteToSyncTaskQueueOutput;
import io.airbyte.workers.temporal.scheduling.activities.StreamResetActivity;
import io.airbyte.workers.temporal.scheduling.activities.WorkflowConfigActivity;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.DbtFailureSyncWorkflow;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.EmptySyncWorkflow;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.NormalizationFailureSyncWorkflow;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.NormalizationTraceFailureSyncWorkflow;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.PersistFailureSyncWorkflow;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.ReplicateFailureSyncWorkflow;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.SleepingSyncWorkflow;
import io.airbyte.workers.temporal.scheduling.testsyncworkflow.SourceAndDestinationFailureSyncWorkflow;
import io.airbyte.workers.temporal.support.TemporalProxyHelper;
import io.micronaut.context.BeanRegistration;
import io.micronaut.inject.BeanIdentifier;
import io.temporal.activity.ActivityOptions;
import io.temporal.api.enums.v1.WorkflowExecutionStatus;
import io.temporal.api.filter.v1.WorkflowExecutionFilter;
import io.temporal.api.workflowservice.v1.ListClosedWorkflowExecutionsRequest;
import io.temporal.api.workflowservice.v1.ListClosedWorkflowExecutionsResponse;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.common.RetryOptions;
import io.temporal.failure.ApplicationFailure;
import io.temporal.testing.TestWorkflowEnvironment;
import io.temporal.worker.Worker;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Queue;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.stream.Stream;
import lombok.extern.slf4j.Slf4j;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
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
class ConnectionManagerWorkflowTest {

  private static final long JOB_ID = 1L;
  private static final int ATTEMPT_ID = 1;

  private static final Duration SCHEDULE_WAIT = Duration.ofMinutes(20L);
  private static final String WORKFLOW_ID = "workflow-id";

  private static final Duration WORKFLOW_FAILURE_RESTART_DELAY = Duration.ofSeconds(600);

  private final ConfigFetchActivity mConfigFetchActivity =
      mock(ConfigFetchActivity.class, Mockito.withSettings().withoutAnnotations());
  private final CheckConnectionActivity mCheckConnectionActivity =
      mock(CheckConnectionActivity.class, Mockito.withSettings().withoutAnnotations());
  private static final GenerateInputActivityImpl mGenerateInputActivityImpl =
      mock(GenerateInputActivityImpl.class, Mockito.withSettings().withoutAnnotations());
  private static final JobCreationAndStatusUpdateActivity mJobCreationAndStatusUpdateActivity =
      mock(JobCreationAndStatusUpdateActivity.class, Mockito.withSettings().withoutAnnotations());
  private static final AutoDisableConnectionActivity mAutoDisableConnectionActivity =
      mock(AutoDisableConnectionActivity.class, Mockito.withSettings().withoutAnnotations());
  private static final StreamResetActivity mStreamResetActivity =
      mock(StreamResetActivity.class, Mockito.withSettings().withoutAnnotations());
  private static final RecordMetricActivity mRecordMetricActivity =
      mock(RecordMetricActivity.class, Mockito.withSettings().withoutAnnotations());
  private static final WorkflowConfigActivity mWorkflowConfigActivity =
      mock(WorkflowConfigActivity.class, Mockito.withSettings().withoutAnnotations());
  private static final RouteToSyncTaskQueueActivity mRouteToSyncTaskQueueActivity =
      mock(RouteToSyncTaskQueueActivity.class, Mockito.withSettings().withoutAnnotations());
  private static final String EVENT = "event = ";

  private TestWorkflowEnvironment testEnv;
  private WorkflowClient client;
  private ConnectionManagerWorkflow workflow;
  private ActivityOptions activityOptions;
  private TemporalProxyHelper temporalProxyHelper;

  static Stream<Arguments> getMaxAttemptForResetRetry() {
    return Stream.of(
        Arguments.of(3), // "The max attempt is 3, it will test that after a failed reset attempt the next attempt will also
                         // be a
        // reset")
        Arguments.of(1) // "The max attempt is 3, it will test that after a failed reset job the next attempt will also be a
                        // job")
    );
  }

  @BeforeEach
  void setUp() {
    Mockito.reset(mConfigFetchActivity);
    Mockito.reset(mCheckConnectionActivity);
    Mockito.reset(mGenerateInputActivityImpl);
    Mockito.reset(mJobCreationAndStatusUpdateActivity);
    Mockito.reset(mAutoDisableConnectionActivity);
    Mockito.reset(mStreamResetActivity);
    Mockito.reset(mRecordMetricActivity);
    Mockito.reset(mWorkflowConfigActivity);
    Mockito.reset(mRouteToSyncTaskQueueActivity);

    // default is to wait "forever"
    when(mConfigFetchActivity.getTimeToWait(Mockito.any())).thenReturn(new ScheduleRetrieverOutput(
        Duration.ofDays(100 * 365)));

    when(mJobCreationAndStatusUpdateActivity.createNewJob(Mockito.any()))
        .thenReturn(new JobCreationOutput(
            1L));

    when(mJobCreationAndStatusUpdateActivity.createNewAttemptNumber(Mockito.any()))
        .thenReturn(new AttemptNumberCreationOutput(
            1));

    when(mGenerateInputActivityImpl.getSyncWorkflowInputWithAttemptNumber(Mockito.any(SyncInputWithAttemptNumber.class)))
        .thenReturn(
            new GeneratedJobInput(
                new JobRunConfig(),
                new IntegrationLauncherConfig().withDockerImage("some_source"),
                new IntegrationLauncherConfig(),
                new StandardSyncInput()));

    when(mCheckConnectionActivity.runWithJobOutput(Mockito.any()))
        .thenReturn(new ConnectorJobOutput().withOutputType(OutputType.CHECK_CONNECTION)
            .withCheckConnection(new StandardCheckConnectionOutput().withStatus(Status.SUCCEEDED).withMessage("check worked")));

    when(mAutoDisableConnectionActivity.autoDisableFailingConnection(Mockito.any()))
        .thenReturn(new AutoDisableConnectionOutput(false));

    when(mWorkflowConfigActivity.getWorkflowRestartDelaySeconds())
        .thenReturn(WORKFLOW_FAILURE_RESTART_DELAY);

    // TODO: for now, always route to default 'SYNC' task queue. Add test for routing
    // to a different task queue
    when(mRouteToSyncTaskQueueActivity.route(Mockito.any()))
        .thenReturn(new RouteToSyncTaskQueueOutput(TemporalJobType.SYNC.name()));

    activityOptions = ActivityOptions.newBuilder()
        .setHeartbeatTimeout(Duration.ofSeconds(30))
        .setStartToCloseTimeout(Duration.ofSeconds(120))
        .setRetryOptions(RetryOptions.newBuilder()
            .setMaximumAttempts(5)
            .setInitialInterval(Duration.ofSeconds(30))
            .setMaximumInterval(Duration.ofSeconds(600))
            .build())

        .build();

    final BeanIdentifier activityOptionsBeanIdentifier = mock(BeanIdentifier.class);
    final BeanRegistration activityOptionsBeanRegistration = mock(BeanRegistration.class);
    when(activityOptionsBeanIdentifier.getName()).thenReturn("shortActivityOptions");
    when(activityOptionsBeanRegistration.getIdentifier()).thenReturn(activityOptionsBeanIdentifier);
    when(activityOptionsBeanRegistration.getBean()).thenReturn(activityOptions);
    temporalProxyHelper = new TemporalProxyHelper(List.of(activityOptionsBeanRegistration));
  }

  private void returnTrueForLastJobOrAttemptFailure() {
    when(mJobCreationAndStatusUpdateActivity.isLastJobOrAttemptFailure(Mockito.any()))
        .thenReturn(true);

    final JobRunConfig jobRunConfig = new JobRunConfig();
    jobRunConfig.setJobId(Long.toString(JOB_ID));
    jobRunConfig.setAttemptId((long) ATTEMPT_ID);
    when(mGenerateInputActivityImpl.getSyncWorkflowInputWithAttemptNumber(Mockito.any(SyncInputWithAttemptNumber.class)))
        .thenReturn(
            new GeneratedJobInput(
                jobRunConfig,
                new IntegrationLauncherConfig().withDockerImage("some_source").withProtocolVersion(new Version("0.2.0")),
                new IntegrationLauncherConfig().withProtocolVersion(new Version("0.2.0")),
                new StandardSyncInput()));
  }

  @AfterEach
  void tearDown() {
    testEnv.shutdown();
    TestStateListener.reset();
  }

  private void mockResetJobInput(final JobRunConfig jobRunConfig) {
    when(mGenerateInputActivityImpl.getSyncWorkflowInputWithAttemptNumber(Mockito.any(SyncInputWithAttemptNumber.class)))
        .thenReturn(
            new GeneratedJobInput(
                jobRunConfig,
                new IntegrationLauncherConfig().withDockerImage(WorkerConstants.RESET_JOB_SOURCE_DOCKER_IMAGE_STUB),
                new IntegrationLauncherConfig(),
                new StandardSyncInput()));
  }

  @Nested
  @DisplayName("Test which without a long running child workflow")
  class AsynchronousWorkflow {

    @BeforeEach
    void setup() {
      setupSpecificChildWorkflow(EmptySyncWorkflow.class);
    }

    @Test
    @Timeout(value = 10,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that a successful workflow retries and waits")
    void runSuccess() throws InterruptedException {
      returnTrueForLastJobOrAttemptFailure();
      when(mConfigFetchActivity.getTimeToWait(Mockito.any()))
          .thenReturn(new ScheduleRetrieverOutput(SCHEDULE_WAIT));
      when(mConfigFetchActivity.getMaxAttempt()).thenReturn(new GetMaxAttemptOutput(1));

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
          .hasSizeGreaterThan(0);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.DONE_WAITING && changedStateEvent.isValue())
          .hasSizeGreaterThan(0);

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
      returnTrueForLastJobOrAttemptFailure();
      when(mConfigFetchActivity.getTimeToWait(Mockito.any()))
          .thenReturn(new ScheduleRetrieverOutput(SCHEDULE_WAIT));
      when(mConfigFetchActivity.getMaxAttempt()).thenReturn(new GetMaxAttemptOutput(1));

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
          .hasSizeGreaterThan(0);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.DONE_WAITING && changedStateEvent.isValue())
          .hasSizeGreaterThan(0);

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

      returnTrueForLastJobOrAttemptFailure();
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

      returnTrueForLastJobOrAttemptFailure();
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

      returnTrueForLastJobOrAttemptFailure();
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

    // TODO: delete when the signal method can be removed
    @Test
    @Timeout(value = 10,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that the sync is properly deleted")
    void deleteSync() throws InterruptedException {

      returnTrueForLastJobOrAttemptFailure();
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
    }

    @Test
    @Timeout(value = 10,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that fresh workflow cleans the job state")
    void testStartFromCleanJobState() throws InterruptedException {

      returnTrueForLastJobOrAttemptFailure();
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

  @Nested
  @DisplayName("Test which with a long running child workflow")
  class SynchronousWorkflow {

    @BeforeEach
    void setup() {
      setupSpecificChildWorkflow(SleepingSyncWorkflow.class);
    }

    @Test
    @Timeout(value = 10,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test workflow which receives a manual sync while running a scheduled sync does nothing")
    void manualRun() throws InterruptedException {
      returnTrueForLastJobOrAttemptFailure();
      when(mConfigFetchActivity.getTimeToWait(Mockito.any()))
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

      returnTrueForLastJobOrAttemptFailure();
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

      returnTrueForLastJobOrAttemptFailure();
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

      returnTrueForLastJobOrAttemptFailure();
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
    @Timeout(value = 10,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that resetting a non-running workflow starts a reset job")
    void resetAndContinue() throws InterruptedException {

      returnTrueForLastJobOrAttemptFailure();
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
      workflow.resetConnectionAndSkipNextScheduling();
      Thread.sleep(500);

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.SKIPPED_SCHEDULING && changedStateEvent.isValue())
          .hasSizeGreaterThanOrEqualTo(1);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.SKIP_SCHEDULING_NEXT_WORKFLOW && changedStateEvent.isValue())
          .hasSizeGreaterThanOrEqualTo(1);
    }

    @Test
    @Timeout(value = 60,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that resetting a running workflow cancels the running workflow")
    void resetCancelRunningWorkflow() throws InterruptedException {

      returnTrueForLastJobOrAttemptFailure();
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
    @DisplayName("Test that running workflow which receives an update signal waits for the current run and reports the job status")
    void updatedSignalReceivedWhileRunning() throws InterruptedException {

      returnTrueForLastJobOrAttemptFailure();
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

  @Nested
  @DisplayName("Test that connections are auto disabled if conditions are met")
  class AutoDisableConnection {

    private static final long JOB_ID = 111L;
    private static final int ATTEMPT_ID = 222;

    @BeforeEach
    void setup() {
      testEnv = TestWorkflowEnvironment.newInstance();

      final Worker managerWorker = testEnv.newWorker(TemporalJobType.CONNECTION_UPDATER.name());
      managerWorker.registerWorkflowImplementationTypes(temporalProxyHelper.proxyWorkflowClass(ConnectionManagerWorkflowImpl.class));
      managerWorker.registerActivitiesImplementations(mConfigFetchActivity, mCheckConnectionActivity, mGenerateInputActivityImpl,
          mJobCreationAndStatusUpdateActivity, mAutoDisableConnectionActivity, mRecordMetricActivity,
          mWorkflowConfigActivity, mRouteToSyncTaskQueueActivity);

      client = testEnv.getWorkflowClient();
      workflow = client.newWorkflowStub(ConnectionManagerWorkflow.class,
          WorkflowOptions.newBuilder().setTaskQueue(TemporalJobType.CONNECTION_UPDATER.name()).build());

      when(mConfigFetchActivity.getMaxAttempt()).thenReturn(new GetMaxAttemptOutput(1));
    }

    @Test
    @Timeout(value = 10,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that auto disable activity is touched during failure")
    void testAutoDisableOnFailure() throws InterruptedException {
      returnTrueForLastJobOrAttemptFailure();
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
      returnTrueForLastJobOrAttemptFailure();
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

  @Nested
  @DisplayName("Test that sync workflow failures are recorded")
  class SyncWorkflowReplicationFailuresRecorded {

    private static final long JOB_ID = 111L;
    private static final int ATTEMPT_ID = 222;

    @BeforeEach
    void setup() {
      testEnv = TestWorkflowEnvironment.newInstance();

      final Worker managerWorker = testEnv.newWorker(TemporalJobType.CONNECTION_UPDATER.name());
      managerWorker.registerWorkflowImplementationTypes(temporalProxyHelper.proxyWorkflowClass(ConnectionManagerWorkflowImpl.class));
      managerWorker.registerActivitiesImplementations(mConfigFetchActivity, mCheckConnectionActivity, mGenerateInputActivityImpl,
          mJobCreationAndStatusUpdateActivity, mAutoDisableConnectionActivity, mRecordMetricActivity,
          mWorkflowConfigActivity, mRouteToSyncTaskQueueActivity);

      client = testEnv.getWorkflowClient();
      workflow = client.newWorkflowStub(ConnectionManagerWorkflow.class,
          WorkflowOptions.newBuilder().setTaskQueue(TemporalJobType.CONNECTION_UPDATER.name()).build());

      when(mConfigFetchActivity.getMaxAttempt()).thenReturn(new GetMaxAttemptOutput(1));
    }

    @Test
    @Timeout(value = 10,
             unit = TimeUnit.SECONDS)
    @DisplayName("Test that Source CHECK failures are recorded")
    void testSourceCheckFailuresRecorded() throws InterruptedException {
      returnTrueForLastJobOrAttemptFailure();
      when(mJobCreationAndStatusUpdateActivity.createNewJob(Mockito.any()))
          .thenReturn(new JobCreationOutput(JOB_ID));
      when(mJobCreationAndStatusUpdateActivity.createNewAttemptNumber(Mockito.any()))
          .thenReturn(new AttemptNumberCreationOutput(ATTEMPT_ID));
      when(mCheckConnectionActivity.runWithJobOutput(Mockito.any()))
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
      returnTrueForLastJobOrAttemptFailure();
      when(mJobCreationAndStatusUpdateActivity.createNewJob(Mockito.any()))
          .thenReturn(new JobCreationOutput(JOB_ID));
      when(mJobCreationAndStatusUpdateActivity.createNewAttemptNumber(Mockito.any()))
          .thenReturn(new AttemptNumberCreationOutput(ATTEMPT_ID));
      when(mCheckConnectionActivity.runWithJobOutput(Mockito.any()))
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
      returnTrueForLastJobOrAttemptFailure();
      when(mJobCreationAndStatusUpdateActivity.createNewJob(Mockito.any()))
          .thenReturn(new JobCreationOutput(JOB_ID));
      when(mJobCreationAndStatusUpdateActivity.createNewAttemptNumber(Mockito.any()))
          .thenReturn(new AttemptNumberCreationOutput(ATTEMPT_ID));
      when(mCheckConnectionActivity.runWithJobOutput(Mockito.any()))
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
      returnTrueForLastJobOrAttemptFailure();
      when(mJobCreationAndStatusUpdateActivity.createNewJob(Mockito.any()))
          .thenReturn(new JobCreationOutput(JOB_ID));
      when(mJobCreationAndStatusUpdateActivity.createNewAttemptNumber(Mockito.any()))
          .thenReturn(new AttemptNumberCreationOutput(ATTEMPT_ID));
      when(mCheckConnectionActivity.runWithJobOutput(Mockito.any()))
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

      when(mJobCreationAndStatusUpdateActivity.isLastJobOrAttemptFailure(Mockito.any()))
          .thenReturn(true);

      final JobRunConfig jobRunConfig = new JobRunConfig();
      jobRunConfig.setJobId(Long.toString(JOB_ID));
      jobRunConfig.setAttemptId((long) ATTEMPT_ID);
      when(mGenerateInputActivityImpl.getSyncWorkflowInputWithAttemptNumber(Mockito.any(SyncInputWithAttemptNumber.class)))
          .thenReturn(
              new GeneratedJobInput(
                  jobRunConfig,
                  new IntegrationLauncherConfig().withDockerImage("some_source"),
                  new IntegrationLauncherConfig(),
                  new StandardSyncInput()));

      when(mJobCreationAndStatusUpdateActivity.createNewJob(Mockito.any()))
          .thenReturn(new JobCreationOutput(JOB_ID));
      when(mJobCreationAndStatusUpdateActivity.createNewAttemptNumber(Mockito.any()))
          .thenReturn(new AttemptNumberCreationOutput(ATTEMPT_ID));
      mockResetJobInput(jobRunConfig);
      when(mCheckConnectionActivity.runWithJobOutput(Mockito.any()))
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
      returnTrueForLastJobOrAttemptFailure();
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
      returnTrueForLastJobOrAttemptFailure();
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
      returnTrueForLastJobOrAttemptFailure();
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
      returnTrueForLastJobOrAttemptFailure();
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
      returnTrueForLastJobOrAttemptFailure();
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
      returnTrueForLastJobOrAttemptFailure();
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

  @Nested
  @DisplayName("Test that the workflow is properly restarted after activity failures.")
  class FailedActivityWorkflow {

    @BeforeEach
    void setup() {
      setupSpecificChildWorkflow(SleepingSyncWorkflow.class);
    }

    static Stream<Arguments> getSetupFailingActivity() {
      return Stream.of(
          Arguments.of(new Thread(() -> when(mJobCreationAndStatusUpdateActivity.createNewJob(Mockito.any()))
              .thenThrow(ApplicationFailure.newNonRetryableFailure("", "")))),
          Arguments.of(new Thread(() -> when(mJobCreationAndStatusUpdateActivity.createNewAttemptNumber(Mockito.any()))
              .thenThrow(ApplicationFailure.newNonRetryableFailure("", "")))),
          Arguments.of(new Thread(() -> Mockito.doThrow(ApplicationFailure.newNonRetryableFailure("", ""))
              .when(mJobCreationAndStatusUpdateActivity).reportJobStart(Mockito.any()))),
          Arguments.of(new Thread(
              () -> when(mGenerateInputActivityImpl.getSyncWorkflowInputWithAttemptNumber(Mockito.any(SyncInputWithAttemptNumber.class)))
                  .thenThrow(ApplicationFailure.newNonRetryableFailure("", "")))));
    }

    @ParameterizedTest
    @MethodSource("getSetupFailingActivity")
    void testWorkflowRestartedAfterFailedActivity(final Thread mockSetup) throws InterruptedException {
      returnTrueForLastJobOrAttemptFailure();
      mockSetup.run();
      when(mConfigFetchActivity.getTimeToWait(Mockito.any())).thenReturn(new ScheduleRetrieverOutput(
          Duration.ZERO));
      when(mConfigFetchActivity.getMaxAttempt()).thenReturn(new GetMaxAttemptOutput(1));

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
      testEnv.sleep(WORKFLOW_FAILURE_RESTART_DELAY.plus(Duration.ofSeconds(10)));

      final Queue<ChangedStateEvent> events = testStateListener.events(testId);

      Assertions.assertThat(events)
          .filteredOn(changedStateEvent -> changedStateEvent.getField() == StateField.RUNNING && changedStateEvent.isValue())
          .isEmpty();

      assertWorkflowWasContinuedAsNew();
    }

  }

  private class HasFailureFromOrigin implements ArgumentMatcher<AttemptNumberFailureInput> {

    private final FailureOrigin expectedFailureOrigin;

    HasFailureFromOrigin(final FailureOrigin failureOrigin) {
      this.expectedFailureOrigin = failureOrigin;
    }

    @Override
    public boolean matches(final AttemptNumberFailureInput arg) {
      return arg.getAttemptFailureSummary().getFailures().stream().anyMatch(f -> f.getFailureOrigin().equals(expectedFailureOrigin));
    }

  }

  private class HasFailureFromOriginWithType implements ArgumentMatcher<AttemptNumberFailureInput> {

    private final FailureOrigin expectedFailureOrigin;
    private final FailureType expectedFailureType;

    HasFailureFromOriginWithType(final FailureOrigin failureOrigin, final FailureType failureType) {
      this.expectedFailureOrigin = failureOrigin;
      this.expectedFailureType = failureType;
    }

    @Override
    public boolean matches(final AttemptNumberFailureInput arg) {
      final Stream<FailureReason> stream = arg.getAttemptFailureSummary().getFailures().stream();
      return stream.anyMatch(f -> f.getFailureOrigin().equals(expectedFailureOrigin) && f.getFailureType().equals(expectedFailureType));
    }

  }

  private class HasCancellationFailure implements ArgumentMatcher<JobCancelledInputWithAttemptNumber> {

    private final long expectedJobId;
    private final int expectedAttemptNumber;

    HasCancellationFailure(final long jobId, final int attemptNumber) {
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
    managerWorker.registerWorkflowImplementationTypes(temporalProxyHelper.proxyWorkflowClass(ConnectionManagerWorkflowImpl.class));
    managerWorker.registerActivitiesImplementations(mConfigFetchActivity, mCheckConnectionActivity, mGenerateInputActivityImpl,
        mJobCreationAndStatusUpdateActivity, mAutoDisableConnectionActivity, mRecordMetricActivity,
        mWorkflowConfigActivity, mRouteToSyncTaskQueueActivity);

    client = testEnv.getWorkflowClient();
    testEnv.start();

    workflow = client
        .newWorkflowStub(
            ConnectionManagerWorkflow.class,
            WorkflowOptions.newBuilder()
                .setTaskQueue(TemporalJobType.CONNECTION_UPDATER.name())
                .setWorkflowId(WORKFLOW_ID)
                .build());
  }

  private void assertWorkflowWasContinuedAsNew() {
    final ListClosedWorkflowExecutionsRequest request = ListClosedWorkflowExecutionsRequest.newBuilder()
        .setNamespace(testEnv.getNamespace())
        .setExecutionFilter(WorkflowExecutionFilter.newBuilder().setWorkflowId(WORKFLOW_ID))
        .build();
    final ListClosedWorkflowExecutionsResponse listResponse = testEnv
        .getWorkflowService()
        .blockingStub()
        .listClosedWorkflowExecutions(request);
    Assertions.assertThat(listResponse.getExecutionsCount()).isGreaterThanOrEqualTo(1);
    Assertions.assertThat(listResponse.getExecutionsList().get(0).getStatus())
        .isEqualTo(WorkflowExecutionStatus.WORKFLOW_EXECUTION_STATUS_CONTINUED_AS_NEW);
  }

}
