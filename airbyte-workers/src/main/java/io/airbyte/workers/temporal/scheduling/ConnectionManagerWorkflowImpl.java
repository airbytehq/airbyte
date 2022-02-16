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
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivity.SyncInput;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivity.SyncOutput;
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
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.function.Consumer;
import java.util.function.Function;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class ConnectionManagerWorkflowImpl implements ConnectionManagerWorkflow {

  public long NON_RUNNING_JOB_ID;
  public int NON_RUNNING_ATTEMPT_ID;

  private WorkflowState workflowState = new WorkflowState(UUID.randomUUID(), new NoopStateListener());

  Optional<Long> maybeJobId = Optional.empty();
  Optional<Integer> maybeAttemptId = Optional.empty();

  Optional<StandardSyncOutput> standardSyncOutput = Optional.empty();
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

  private CancellationScope syncWorkflowCancellationScope;

  private UUID connectionId;

  public ConnectionManagerWorkflowImpl() {}

  @Override
  public void run(final ConnectionUpdaterInput connectionUpdaterInput) throws RetryableException {
    connectionId = connectionUpdaterInput.getConnectionId();
    try {
      if (connectionUpdaterInput.getWorkflowState() != null) {
        workflowState = connectionUpdaterInput.getWorkflowState();
      }
      try {
        syncWorkflowCancellationScope = Workflow.newCancellationScope(() -> {
          // Scheduling
          final ScheduleRetrieverInput scheduleRetrieverInput = new ScheduleRetrieverInput(
              connectionUpdaterInput.getConnectionId());

          workflowState.setResetConnection(connectionUpdaterInput.isResetConnection());

          final ScheduleRetrieverOutput scheduleRetrieverOutput = configFetchActivity.getTimeToWait(scheduleRetrieverInput);
          Workflow.await(scheduleRetrieverOutput.getTimeToWait(),
              () -> skipScheduling() || connectionUpdaterInput.isFromFailure());
          if (!workflowState.isUpdated() && !workflowState.isDeleted()) {
            maybeJobId = Optional.ofNullable(connectionUpdaterInput.getJobId()).or(() -> {
              final JobCreationOutput jobCreationOutput =
                  runMandatoryActivityWithOutput(
                      (input) -> jobCreationAndStatusUpdateActivity.createNewJob(input),
                      new JobCreationInput(
                          connectionUpdaterInput.getConnectionId(), workflowState.isResetConnection()));
              connectionUpdaterInput.setJobId(jobCreationOutput.getJobId());
              return Optional.ofNullable(jobCreationOutput.getJobId());
            });

            maybeAttemptId = Optional.ofNullable(connectionUpdaterInput.getAttemptId()).or(() -> maybeJobId.map(jobId -> {
              final AttemptCreationOutput attemptCreationOutput =
                  runMandatoryActivityWithOutput(
                      (input) -> jobCreationAndStatusUpdateActivity.createNewAttempt(input),
                      new AttemptCreationInput(
                          jobId));
              connectionUpdaterInput.setAttemptId(attemptCreationOutput.getAttemptId());
              return attemptCreationOutput.getAttemptId();
            }));

            // Sync workflow
            final SyncInput getSyncInputActivitySyncInput = new SyncInput(
                maybeAttemptId.get(),
                maybeJobId.get(),
                workflowState.isResetConnection());

            runMandatoryActivity(
                (input) -> jobCreationAndStatusUpdateActivity.reportJobStart(input),
                new ReportJobStartInput(
                    maybeJobId.get()));

            final SyncOutput syncWorkflowInputs = runMandatoryActivityWithOutput(
                (input) -> getSyncInputActivity.getSyncWorkflowInput(input),
                getSyncInputActivitySyncInput);

            workflowState.setRunning(true);

            final SyncWorkflow childSync = Workflow.newChildWorkflowStub(SyncWorkflow.class,
                ChildWorkflowOptions.newBuilder()
                    .setWorkflowId("sync_" + maybeJobId.get())
                    .setTaskQueue(TemporalJobType.CONNECTION_UPDATER.name())
                    // This will cancel the child workflow when the parent is terminated
                    .setParentClosePolicy(ParentClosePolicy.PARENT_CLOSE_POLICY_TERMINATE)
                    .build());

            final UUID connectionId = connectionUpdaterInput.getConnectionId();

            try {
              standardSyncOutput = Optional.ofNullable(childSync.run(
                  syncWorkflowInputs.getJobRunConfig(),
                  syncWorkflowInputs.getSourceLauncherConfig(),
                  syncWorkflowInputs.getDestinationLauncherConfig(),
                  syncWorkflowInputs.getSyncInput(),
                  connectionId));

              final StandardSyncSummary standardSyncSummary = standardSyncOutput.get().getStandardSyncSummary();

              if (workflowState.isResetConnection()) {
                workflowState.setResetConnection(false);
              }

              if (standardSyncSummary != null && standardSyncSummary.getStatus() == ReplicationStatus.FAILED) {
                failures.addAll(standardSyncOutput.get().getFailures());
                partialSuccess = standardSyncSummary.getTotalStats().getRecordsCommitted() > 0;
                workflowState.setFailed(true);
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
                    maybeJobId.get(),
                    maybeAttemptId.get()));
                throw childWorkflowFailure;
              } else {
                failures.add(
                    FailureHelper.unknownOriginFailure(childWorkflowFailure.getCause(), maybeJobId.get(), maybeAttemptId.get()));
                throw childWorkflowFailure;
              }
            }
          }
        });
        syncWorkflowCancellationScope.run();
      } catch (final CanceledFailure cf) {
        // When a scope is cancelled temporal will thow a CanceledFailure as you can see here:
        // https://github.com/temporalio/sdk-java/blob/master/temporal-sdk/src/main/java/io/temporal/workflow/CancellationScope.java#L72
        // The naming is very misleading, it is not a failure but the expected behavior...
      }

      // The workflow state will be updated to true if a reset happened while a job was running.
      // We need to propagate that to the new run that will be continued as new.
      // When cancelling a reset, we endure that the next workflow won't be a reset.
      // We are using a specific workflow state for that, this makes the set of the fact that we are going
      // to continue as a reset testable.
      if (workflowState.isCancelledForReset()) {
        workflowState.setContinueAsReset(true);
        connectionUpdaterInput.setJobId(null);
        connectionUpdaterInput.setAttemptNumber(1);
        connectionUpdaterInput.setFromFailure(false);
        connectionUpdaterInput.setAttemptId(null);
      } else {
        workflowState.setContinueAsReset(false);
      }

      if (workflowState.isUpdated() && !workflowState.isRunning()) {
        log.error("A connection configuration has changed for the connection {} when no sync was running. The job will be restarted",
            connectionUpdaterInput.getConnectionId());
      } else if (workflowState.isDeleted()) {
        // Stop the runs
        final ConnectionDeletionInput connectionDeletionInput = new ConnectionDeletionInput(connectionUpdaterInput.getConnectionId());
        runMandatoryActivity((input) -> connectionDeletionActivity.deleteConnection(input), connectionDeletionInput);
        return;
      } else if (workflowState.isCancelled() || workflowState.isCancelledForReset()) {
        runMandatoryActivity((input) -> jobCreationAndStatusUpdateActivity.jobCancelled(input),
            new JobCancelledInput(
                maybeJobId.get(),
                maybeAttemptId.get(),
                FailureHelper.failureSummaryForCancellation(maybeJobId.get(), maybeAttemptId.get(), failures, partialSuccess)));
        resetNewConnectionInput(connectionUpdaterInput);
      } else if (workflowState.isFailed()) {
        reportFailure(connectionUpdaterInput);
      } else {
        // report success
        reportSuccess(connectionUpdaterInput);
      }
      continueAsNew(connectionUpdaterInput);
    } catch (final Exception e) {
      log.error("The connection update workflow has failed, will create a new attempt.", e);

      reportFailure(connectionUpdaterInput);
      continueAsNew(connectionUpdaterInput);
    }
  }

  private void reportSuccess(final ConnectionUpdaterInput connectionUpdaterInput) {
    workflowState.setSuccess(true);
    runMandatoryActivity((input) -> jobCreationAndStatusUpdateActivity.jobSuccess(input), new JobSuccessInput(
        maybeJobId.get(),
        maybeAttemptId.get(),
        standardSyncOutput.orElse(null)));

    resetNewConnectionInput(connectionUpdaterInput);
  }

  private void reportFailure(final ConnectionUpdaterInput connectionUpdaterInput) {
    runMandatoryActivity((input) -> jobCreationAndStatusUpdateActivity.attemptFailure(input), new AttemptFailureInput(
        connectionUpdaterInput.getJobId(),
        connectionUpdaterInput.getAttemptId(),
        standardSyncOutput.orElse(null),
        FailureHelper.failureSummary(failures, partialSuccess)));

    final int maxAttempt = configFetchActivity.getMaxAttempt().getMaxAttempt();
    final int attemptNumber = connectionUpdaterInput.getAttemptNumber();

    if (maxAttempt > attemptNumber) {
      // restart from failure
      connectionUpdaterInput.setAttemptNumber(attemptNumber + 1);
      connectionUpdaterInput.setFromFailure(true);
    } else {
      runMandatoryActivity((input) -> jobCreationAndStatusUpdateActivity.jobFailure(input), new JobFailureInput(
          connectionUpdaterInput.getJobId(),
          "Job failed after too many retries for connection " + connectionId));

      Workflow.await(Duration.ofMinutes(1), () -> skipScheduling());

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
    syncWorkflowCancellationScope.cancel();
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
      syncWorkflowCancellationScope.cancel();
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
        maybeJobId.orElse(NON_RUNNING_JOB_ID),
        maybeAttemptId.orElse(NON_RUNNING_ATTEMPT_ID));
  }

  @Override
  public QuarantinedInformation getQuarantinedInformation() {
    return new QuarantinedInformation(
        connectionId,
        maybeJobId.orElse(NON_RUNNING_JOB_ID),
        maybeAttemptId.orElse(NON_RUNNING_ATTEMPT_ID),
        workflowState.isQuarantined());
  }

  private Boolean skipScheduling() {
    return workflowState.isSkipScheduling() || workflowState.isDeleted() || workflowState.isUpdated() || workflowState.isResetConnection();
  }

  private void continueAsNew(final ConnectionUpdaterInput connectionUpdaterInput) {
    // Continue the workflow as new
    connectionUpdaterInput.setAttemptId(null);
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

}
