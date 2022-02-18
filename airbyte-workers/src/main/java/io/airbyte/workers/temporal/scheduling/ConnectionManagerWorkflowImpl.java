/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.airbyte.config.FailureReason;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.StandardSyncSummary.ReplicationStatus;
import io.airbyte.workers.helper.FailureHelper;
import io.airbyte.workers.temporal.TemporalJobType;
import io.airbyte.workers.temporal.exception.RetryableException;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity.ScheduleRetrieverInput;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity.ScheduleRetrieverOutput;
import io.airbyte.workers.temporal.scheduling.activities.ConnectionDeletionActivity;
import io.airbyte.workers.temporal.scheduling.activities.ConnectionDeletionActivity.ConnectionDeletionInput;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivity;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivity.GeneratedJobInput;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivity.SyncInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.AttemptCreationInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.AttemptCreationOutput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.AttemptFailureInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobCancelledInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobCreationInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobCreationOutput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobFailureInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobSuccessInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.ReportJobStartInput;
import io.airbyte.workers.temporal.scheduling.shared.ActivityConfiguration;
import io.airbyte.workers.temporal.scheduling.state.WorkflowState;
import io.airbyte.workers.temporal.scheduling.state.listener.NoopStateListener;
import io.airbyte.workers.temporal.sync.SyncWorkflow;
import io.temporal.api.enums.v1.ParentClosePolicy;
import io.temporal.failure.ActivityFailure;
import io.temporal.failure.CanceledFailure;
import io.temporal.failure.ChildWorkflowFailure;
import io.temporal.workflow.CancellationScope;
import io.temporal.workflow.ChildWorkflowOptions;
import io.temporal.workflow.Workflow;
import java.time.Duration;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import java.util.function.Consumer;
import java.util.function.Function;
import lombok.extern.slf4j.Slf4j;
import lombok.val;

@Slf4j
public class ConnectionManagerWorkflowImpl implements ConnectionManagerWorkflow {

  public long NON_RUNNING_JOB_ID;
  public int NON_RUNNING_ATTEMPT_ID;

  private WorkflowState workflowState = new WorkflowState(UUID.randomUUID(), new NoopStateListener());

  Long jobId = null;
  Integer attemptId = null;

  // StandardSyncOutput standardSyncOutput = null;
  final Set<FailureReason> failures = new HashSet<>();
  Boolean partialSuccess = null;

  private final GenerateInputActivity getSyncInputActivity =
      Workflow.newActivityStub(GenerateInputActivity.class, ActivityConfiguration.SHORT_ACTIVITY_OPTIONS);
  private final JobCreationAndStatusUpdateActivity jobCreationAndStatusUpdateActivity =
      Workflow.newActivityStub(JobCreationAndStatusUpdateActivity.class, ActivityConfiguration.SHORT_ACTIVITY_OPTIONS);
  private final ConfigFetchActivity configFetchActivity =
      Workflow.newActivityStub(ConfigFetchActivity.class, ActivityConfiguration.SHORT_ACTIVITY_OPTIONS);
  private final ConnectionDeletionActivity connectionDeletionActivity =
      Workflow.newActivityStub(ConnectionDeletionActivity.class, ActivityConfiguration.SHORT_ACTIVITY_OPTIONS);

  private CancellationScope cancellableSyncWorkflow;

  private UUID connectionId;

  public ConnectionManagerWorkflowImpl() {}

  @Override
  public void run(final ConnectionUpdaterInput connectionUpdaterInput) throws RetryableException {
    try {
      try {
        cancellableSyncWorkflow = generateSyncWorkflowRunnable(connectionUpdaterInput);
        cancellableSyncWorkflow.run();
      } catch (final CanceledFailure cf) {
        // When a scope is cancelled temporal will thow a CanceledFailure as you can see here:
        // https://github.com/temporalio/sdk-java/blob/master/temporal-sdk/src/main/java/io/temporal/workflow/CancellationScope.java#L72
        // The naming is very misleading, it is not a failure but the expected behavior...
      }

      if (workflowState.isDeleted()) {
        deleteConnectionBeforeTerminatingTheWorkflow();
        return;
      }

      if (workflowState.isCancelledForReset()) {
        reportCancelledAndContinueWith(true, connectionUpdaterInput);
      }

      if (workflowState.isCancelled()) {
        reportCancelledAndContinueWith(false, connectionUpdaterInput);
      }

    } catch (final Exception e) {
      log.error("The connection update workflow has failed, will create a new attempt.", e);
      reportFailure(connectionUpdaterInput, null);
      prepareForNextRunAndContinueAsNew(connectionUpdaterInput);
    }
  }

  private CancellationScope generateSyncWorkflowRunnable(ConnectionUpdaterInput connectionUpdaterInput) {
    return Workflow.newCancellationScope(() -> {
      connectionId = connectionUpdaterInput.getConnectionId();

      if (connectionUpdaterInput.getWorkflowState() != null) {
        workflowState = connectionUpdaterInput.getWorkflowState();
      }

      workflowState.setResetConnection(connectionUpdaterInput.isResetConnection());

      Duration timeToWait = getTimeToWait(connectionUpdaterInput.getConnectionId());

      Workflow.await(timeToWait,
          () -> skipScheduling() || connectionUpdaterInput.isFromFailure());

      val needToProcessSync = !workflowState.isUpdated() && !workflowState.isDeleted();

      if (needToProcessSync) {
        jobId = getOrCreateJobId(connectionUpdaterInput);

        attemptId = createAttemptId(jobId);

        final GeneratedJobInput jobInputs = getJobInput();

        reportJobStarting();
        StandardSyncOutput standardSyncOutput = null;
        try {
          standardSyncOutput = runChildWorkflow(jobInputs);

          workflowState.setFailed(getFailStatus(standardSyncOutput));

          if (workflowState.isFailed()) {
            reportFailure(connectionUpdaterInput, standardSyncOutput);
            prepareForNextRunAndContinueAsNew(connectionUpdaterInput);
          } else {
            reportSuccess(connectionUpdaterInput, standardSyncOutput);
            prepareForNextRunAndContinueAsNew(connectionUpdaterInput);
          }
        } catch (final ChildWorkflowFailure childWorkflowFailure) {
          if (childWorkflowFailure.getCause() instanceof CanceledFailure) {
            // do nothing, cancellation handled by cancellationScope

          } else if (childWorkflowFailure.getCause() instanceof ActivityFailure) {
            final ActivityFailure af = (ActivityFailure) childWorkflowFailure.getCause();
            failures.add(FailureHelper.failureReasonFromWorkflowAndActivity(
                childWorkflowFailure.getWorkflowType(),
                af.getActivityType(),
                af.getCause(),
                jobId,
                attemptId));
            reportFailure(connectionUpdaterInput, standardSyncOutput);
          } else {
            failures.add(
                FailureHelper.unknownOriginFailure(childWorkflowFailure.getCause(), jobId, attemptId));
            reportFailure(connectionUpdaterInput, standardSyncOutput);
          }
        }
      }
    });
  }

  private void reportSuccess(final ConnectionUpdaterInput connectionUpdaterInput, StandardSyncOutput standardSyncOutput) {
    workflowState.setSuccess(true);
    runMandatoryActivity((input) -> jobCreationAndStatusUpdateActivity.jobSuccess(input), new JobSuccessInput(
        jobId,
        attemptId,
        standardSyncOutput));

    resetNewConnectionInput(connectionUpdaterInput);
  }

  private void reportFailure(final ConnectionUpdaterInput connectionUpdaterInput, StandardSyncOutput standardSyncOutput) {
    runMandatoryActivity((input) -> jobCreationAndStatusUpdateActivity.attemptFailure(input), new AttemptFailureInput(
        jobId,
        attemptId,
        standardSyncOutput,
        FailureHelper.failureSummary(failures, partialSuccess)));

    final int maxAttempt = configFetchActivity.getMaxAttempt().getMaxAttempt();
    final int attemptNumber = connectionUpdaterInput.getAttemptNumber();

    if (maxAttempt > attemptNumber) {
      if (workflowState.isResetConnection()) {
        workflowState.setContinueAsReset(true);
      }
      // restart from failure
      connectionUpdaterInput.setAttemptNumber(attemptNumber + 1);
      connectionUpdaterInput.setFromFailure(true);
    } else {
      runMandatoryActivity((input) -> jobCreationAndStatusUpdateActivity.jobFailure(input), new JobFailureInput(
          connectionUpdaterInput.getJobId(),
          "Job failed after too many retries for connection " + connectionId));

      resetNewConnectionInput(connectionUpdaterInput);
    }
  }

  private void resetNewConnectionInput(final ConnectionUpdaterInput connectionUpdaterInput) {
    connectionUpdaterInput.setJobId(null);
    connectionUpdaterInput.setAttemptNumber(1);
    connectionUpdaterInput.setFromFailure(false);
  }

  @Override
  public void submitManualSync() {
    if (workflowState.isRunning()) {
      log.info("Can't schedule a manual workflow if a sync is running for connection {}", connectionId);
      return;
    }

    workflowState.setSkipScheduling(true);
  }

  @Override
  public void cancelJob() {
    if (!workflowState.isRunning()) {
      log.info("Can't cancel a non-running sync for connection {}", connectionId);
      return;
    }
    workflowState.setCancelled(true);
    cancellableSyncWorkflow.cancel();
  }

  @Override
  public void deleteConnection() {
    workflowState.setDeleted(true);
    cancelJob();
  }

  @Override
  public void connectionUpdated() {
    workflowState.setUpdated(true);
  }

  @Override
  public void resetConnection() {
    workflowState.setResetConnection(true);
    if (workflowState.isRunning()) {
      workflowState.setCancelledForReset(true);
      cancellableSyncWorkflow.cancel();
    }
  }

  @Override
  public void retryFailedActivity() {
    workflowState.setRetryFailedActivity(true);
  }

  @Override
  public void simulateFailure() {
    workflowState.setFailed(true);
  }

  @Override
  public WorkflowState getState() {
    return workflowState;
  }

  @Override
  public JobInformation getJobInformation() {
    return new JobInformation(
        jobId == null ? NON_RUNNING_JOB_ID : jobId,
        attemptId == null ? NON_RUNNING_ATTEMPT_ID : attemptId);
  }

  @Override
  public QuarantinedInformation getQuarantinedInformation() {
    return new QuarantinedInformation(
        connectionId,
        jobId == null ? NON_RUNNING_JOB_ID : jobId,
        attemptId == null ? NON_RUNNING_ATTEMPT_ID : attemptId,
        workflowState.isQuarantined());
  }

  private Boolean skipScheduling() {
    return workflowState.isSkipScheduling() || workflowState.isDeleted() || workflowState.isUpdated() || workflowState.isResetConnection();
  }

  private void prepareForNextRunAndContinueAsNew(final ConnectionUpdaterInput connectionUpdaterInput) {
    // Continue the workflow as new
    connectionUpdaterInput.setResetConnection(workflowState.isContinueAsReset());
    failures.clear();
    partialSuccess = null;
    final boolean isDeleted = workflowState.isDeleted();
    workflowState.reset();
    if (!isDeleted) {
      Workflow.continueAsNew(connectionUpdaterInput);
    }
  }

  /**
   * This is running a lambda function that takes {@param input} as an input. If the run of the lambda
   * is thowing an exception, the workflow will be in a quarantined state and can then be manual
   * un-quarantined or a retry of the failed lambda can be trigger through a signal method.
   *
   * We aimed to use this method for call of the temporal activity.
   */
  private <INPUT, OUTPUT> OUTPUT runMandatoryActivityWithOutput(Function<INPUT, OUTPUT> mapper, INPUT input) {
    try {
      return mapper.apply(input);
    } catch (Exception e) {
      log.error("Failed to run an activity for the connection " + connectionId, e);
      workflowState.setQuarantined(true);
      workflowState.setRetryFailedActivity(false);
      Workflow.await(() -> workflowState.isRetryFailedActivity());
      log.error("Retrying an activity for the connection " + connectionId, e);
      workflowState.setQuarantined(false);
      workflowState.setRetryFailedActivity(false);
      return runMandatoryActivityWithOutput(mapper, input);
    }
  }

  /**
   * Similar to runMandatoryActivityWithOutput but for methods that don't return
   */
  private <INPUT> void runMandatoryActivity(Consumer<INPUT> consumer, INPUT input) {
    runMandatoryActivityWithOutput((inputInternal) -> {
      consumer.accept(inputInternal);
      return null;
    }, input);
  }

  /**
   * Return the duration to wait. This is calculated by the configFetchActivity and return the
   * duration to wait until the next run
   *
   * This return the time to wait since the last successful run based on the schedule. If the workflow
   * is manual or disabled the time to wait will be infinite.
   */
  private Duration getTimeToWait(UUID connectionId) {
    // Scheduling
    final ScheduleRetrieverInput scheduleRetrieverInput = new ScheduleRetrieverInput(connectionId);

    final ScheduleRetrieverOutput scheduleRetrieverOutput = runMandatoryActivityWithOutput(configFetchActivity::getTimeToWait,
        scheduleRetrieverInput);

    return scheduleRetrieverOutput.getTimeToWait();
  }

  /**
   * Creates a new job if it is not present in the input. If the jobId is specified in the input of
   * the connectionManagerWorkflow, we will return it. Otherwise we will create a job and return its
   * id.
   */
  private Long getOrCreateJobId(final ConnectionUpdaterInput connectionUpdaterInput) {
    if (connectionUpdaterInput.getJobId() != null) {
      return connectionUpdaterInput.getJobId();
    }

    final JobCreationOutput jobCreationOutput =
        runMandatoryActivityWithOutput(
            jobCreationAndStatusUpdateActivity::createNewJob,
            new JobCreationInput(
                connectionUpdaterInput.getConnectionId(), workflowState.isResetConnection()));
    connectionUpdaterInput.setJobId(jobCreationOutput.getJobId());

    return jobCreationOutput.getJobId();
  }

  /**
   * Create a new attempt for a given jobId
   */
  private Integer createAttemptId(long jobId) {
    final AttemptCreationOutput attemptCreationOutput =
        runMandatoryActivityWithOutput(
            jobCreationAndStatusUpdateActivity::createNewAttempt,
            new AttemptCreationInput(
                jobId));

    return attemptCreationOutput.getAttemptId();
  }

  /**
   * Generate the input that is needed by the job. It will generate the configuration needed by the
   * job and will generate a different output if the job is a sync or a reset.
   */
  private GeneratedJobInput getJobInput() {
    final SyncInput getSyncInputActivitySyncInput = new SyncInput(
        attemptId,
        jobId,
        workflowState.isResetConnection());

    final GeneratedJobInput syncWorkflowInputs = runMandatoryActivityWithOutput(
        getSyncInputActivity::getSyncWorkflowInput,
        getSyncInputActivitySyncInput);

    return syncWorkflowInputs;
  }

  /**
   * Report the job as started in the job tracker and set it as running in the workflow internal
   * state.
   */
  private void reportJobStarting() {
    runMandatoryActivity(
        jobCreationAndStatusUpdateActivity::reportJobStart,
        new ReportJobStartInput(
            jobId));

    workflowState.setRunning(true);
  }

  /**
   * Start the child SyncWorkflow
   */
  private StandardSyncOutput runChildWorkflow(GeneratedJobInput jobInputs) {
    final SyncWorkflow childSync = Workflow.newChildWorkflowStub(SyncWorkflow.class,
        ChildWorkflowOptions.newBuilder()
            .setWorkflowId("sync_" + jobId)
            .setTaskQueue(TemporalJobType.CONNECTION_UPDATER.name())
            // This will cancel the child workflow when the parent is terminated
            .setParentClosePolicy(ParentClosePolicy.PARENT_CLOSE_POLICY_REQUEST_CANCEL)
            .build());

    return childSync.run(
        jobInputs.getJobRunConfig(),
        jobInputs.getSourceLauncherConfig(),
        jobInputs.getDestinationLauncherConfig(),
        jobInputs.getSyncInput(),
        connectionId);
  }

  /**
   * Set the internal status as failed and save the failures reasons
   */
  private boolean getFailStatus(StandardSyncOutput standardSyncOutput) {
    StandardSyncSummary standardSyncSummary = standardSyncOutput.getStandardSyncSummary();

    if (standardSyncSummary != null && standardSyncSummary.getStatus() == ReplicationStatus.FAILED) {
      failures.addAll(standardSyncOutput.getFailures());
      partialSuccess = standardSyncSummary.getTotalStats().getRecordsCommitted() > 0;
      return true;
    }
    return false;
  }

  /**
   * Delete a connection
   */
  private void deleteConnectionBeforeTerminatingTheWorkflow() {
    final ConnectionDeletionInput connectionDeletionInput = new ConnectionDeletionInput(connectionId);
    runMandatoryActivity(connectionDeletionActivity::deleteConnection, connectionDeletionInput);
  }

  /**
   * Set a job as cancel and continue to the next job if and continue as a reset if needed
   */
  private void reportCancelledAndContinueWith(boolean isReset, ConnectionUpdaterInput connectionUpdaterInput) {
    workflowState.setContinueAsReset(isReset);
    runMandatoryActivity(jobCreationAndStatusUpdateActivity::jobCancelled,
        new JobCancelledInput(
            jobId,
            attemptId,
            FailureHelper.failureSummaryForCancellation(jobId, attemptId, failures, partialSuccess)));
    resetNewConnectionInput(connectionUpdaterInput);
    prepareForNextRunAndContinueAsNew(connectionUpdaterInput);
  }

}
