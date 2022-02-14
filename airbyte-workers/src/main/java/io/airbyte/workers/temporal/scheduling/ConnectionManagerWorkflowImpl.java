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

  // todo (cgardens) - what are the various meanings of different states of the input? when is job id
  // null? attempt id? etc.
  @Override
  public void run(final ConnectionUpdaterInput connectionUpdaterInput) throws RetryableException {
    // todo (cgardens) - how should we think about member fields in this class? they seem risky for
    // anything that isn't truly final. connection id is effectively final, but some of these others
    // seem easy to make a mistake on.
    connectionId = connectionUpdaterInput.getConnectionId();
    try {
      // todo (cgardens) - when is workflow state null?
      if (connectionUpdaterInput.getWorkflowState() != null) {
        workflowState = connectionUpdaterInput.getWorkflowState();
      }
      try {
        syncWorkflowCancellationScope = Workflow.newCancellationScope(() -> {
          // todo (cgardens) - move schedule retrieval logic into its own method for readability.
          // Scheduling
          final ScheduleRetrieverInput scheduleRetrieverInput = new ScheduleRetrieverInput(
              connectionUpdaterInput.getConnectionId());

          workflowState.setResetConnection(connectionUpdaterInput.isResetConnection());

          final ScheduleRetrieverOutput scheduleRetrieverOutput = configFetchActivity.getTimeToWait(scheduleRetrieverInput);

          // wait until time to run or interrupted by an event.
          Workflow.await(scheduleRetrieverOutput.getTimeToWait(), () -> skipScheduling() || connectionUpdaterInput.isFromFailure());

          // once we are here it means it is either time ro run or an event was triggered.
          // todo (cgardens) can we model this more clearly?
          if (!workflowState.isUpdated() && !workflowState.isDeleted()) {
            // todo (cgardens) - when is connectionUpdaterInput.getJobId() null?
            // todo (cgardens) - why is job id and attempt id a member field as opposed to a final local
            // variable?
            // todo (cgardens) - what is the benefit of having job and attempt creation is separate activities?
            // todo (cgardens) - move all job and attempt creation into its own method for readability.
            // Job and attempt creation
            maybeJobId = Optional.ofNullable(connectionUpdaterInput.getJobId()).or(() -> {
              final JobCreationOutput jobCreationOutput = jobCreationAndStatusUpdateActivity.createNewJob(new JobCreationInput(
                  connectionUpdaterInput.getConnectionId(), workflowState.isResetConnection()));
              connectionUpdaterInput.setJobId(jobCreationOutput.getJobId());
              return Optional.ofNullable(jobCreationOutput.getJobId());
            });

            maybeAttemptId = Optional.ofNullable(connectionUpdaterInput.getAttemptId()).or(() -> maybeJobId.map(jobId -> {
              final AttemptCreationOutput attemptCreationOutput = jobCreationAndStatusUpdateActivity.createNewAttempt(new AttemptCreationInput(
                  jobId));
              connectionUpdaterInput.setAttemptId(attemptCreationOutput.getAttemptId());
              return attemptCreationOutput.getAttemptId();
            }));

            // Sync workflow
            final SyncInput getSyncInputActivitySyncInput = new SyncInput(
                maybeAttemptId.get(),
                maybeJobId.get(),
                workflowState.isResetConnection());

            // todo (cgardens) - sets the Job / Attempt to running? Should this be part of creating the job and
            // attempt too? What state is the attempt in before this activitiy runs?
            // todo (cgardens) - why is this interleaved with the sync input workflow? should declaring sync
            // input happen after this?
            jobCreationAndStatusUpdateActivity.reportJobStart(new ReportJobStartInput(maybeJobId.get()));

            final SyncOutput syncWorkflowInputs = getSyncInputActivity.getSyncWorkflowInput(getSyncInputActivitySyncInput);

            // todo (cgardens) - what does this do?
            workflowState.setRunning(true);

            // todo (cgardens) - move sync workflow logic into its own method for readability.
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

              // if the current workflow was a reset, it is now safe to switch it back to "normal".
              if (workflowState.isResetConnection()) {
                workflowState.setResetConnection(false);
              }

              if (standardSyncSummary != null && standardSyncSummary.getStatus() == ReplicationStatus.FAILED) {
                // todo (cgardens) - why are failures a member field as opposed to a local variable? seems like it
                // is just asking for us to make a mistake when resetting it.
                failures.addAll(standardSyncOutput.get().getFailures());
                // todo (cgardens) - why is it a member field?
                partialSuccess = standardSyncSummary.getTotalStats().getRecordsCommitted() > 0;
                workflowState.setFailed(true);
              }
            } catch (final ChildWorkflowFailure childWorkflowFailure) {
              if (childWorkflowFailure.getCause() instanceof CanceledFailure) {
                // do nothing, cancellation handled by cancellationScope
                // todo (cgardens) - what does this ^ mean?

              } else if (childWorkflowFailure.getCause() instanceof ActivityFailure) {
                // todo (cgardens) - what is this?
                final ActivityFailure af = (ActivityFailure) childWorkflowFailure.getCause();
                failures.add(FailureHelper.failureReasonFromWorkflowAndActivity(
                    childWorkflowFailure.getWorkflowType(),
                    af.getActivityType(),
                    af.getCause(),
                    maybeJobId.get(),
                    maybeAttemptId.get()));
                throw childWorkflowFailure;
              } else {
                failures.add(FailureHelper.unknownOriginFailure(childWorkflowFailure.getCause(), maybeJobId.get(), maybeAttemptId.get()));
                throw childWorkflowFailure;
              }
            }
          }
        });
        syncWorkflowCancellationScope.run();
      } catch (final CanceledFailure cf) {
        /*
         * When a scope is cancelled temporal will throw a CanceledFailure. The naming is very misleading,
         * it is not a failure but the expected behavior, so we catch and do nothing with it.
         *
         * https://github.com/temporalio/sdk-java/blob/master/temporal-sdk/src/main/java/io/temporal/
         * workflow/CancellationScope.java#L72
         */
      }

      // todo (cgardens) - i don't understand how the second pargraph of this comment is working.
      /*
       * workflowState.isCancelledForReset() means that the current run is being cancelled, because the
       * user has requested a reset. This segment of code, creates the input for the next run, marking it
       * as a reset. It then also restores the value of isCancelledForReset (because the next run is the
       * actual reset).
       *
       * When cancelling a reset, we ensure that the next workflow won't be a reset. We are using a
       * specific workflow state for that, this makes the set of the fact that we are going to continue as
       * a reset testable.
       */
      if (workflowState.isCancelledForReset()) {
        workflowState.setContinueAsReset(true);
        connectionUpdaterInput.setJobId(null);
        connectionUpdaterInput.setAttemptNumber(1);
        connectionUpdaterInput.setFromFailure(false);
        connectionUpdaterInput.setAttemptId(null);
      } else {
        workflowState.setContinueAsReset(false);
      }

      // todo (cgardens) - we need make the top-level flow control clearer. this could effective be an
      // else if in the conditional on line 106, but it so far away it is hard understand how this fits
      // into the flow of events.
      // todo (cgardens) - what happens to workflowState.isUpdated() && workflowState.isRunning()?
      // todo (cgardens) - IMPORTANT - what happens when any event is triggered while it IS running? does
      // it get cancelled? something else
      if (workflowState.isUpdated() && !workflowState.isRunning()) {
        log.error("A connection configuration has changed for the connection {} when no sync was running. The job will be restarted",
            connectionUpdaterInput.getConnectionId());
      } else if (workflowState.isDeleted()) {
        // Stop the runs
        final ConnectionDeletionInput connectionDeletionInput = new ConnectionDeletionInput(connectionUpdaterInput.getConnectionId());
        connectionDeletionActivity.deleteConnection(connectionDeletionInput);
        return;
        // todo (cgardens) - do we need a separate state for cancelledForReset? isn't that just a form of
        // cancelled?
      } else if (workflowState.isCancelled() || workflowState.isCancelledForReset()) {
        jobCreationAndStatusUpdateActivity.jobCancelled(new JobCancelledInput(
            maybeJobId.get(),
            maybeAttemptId.get(),
            FailureHelper.failureSummaryForCancellation(maybeJobId.get(), maybeAttemptId.get(), failures, partialSuccess)));
        resetNewConnectionInput(connectionUpdaterInput);
        // todo (cgardens) - don't we always want to report if we can? see state machine. even if we get
        // cancelled, should we report it? does it make sense to have a single report activity?
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
    jobCreationAndStatusUpdateActivity.jobSuccess(new JobSuccessInput(
        maybeJobId.get(),
        maybeAttemptId.get(),
        standardSyncOutput.orElse(null)));

    resetNewConnectionInput(connectionUpdaterInput);
  }

  private void reportFailure(final ConnectionUpdaterInput connectionUpdaterInput) {
    jobCreationAndStatusUpdateActivity.attemptFailure(new AttemptFailureInput(
        connectionUpdaterInput.getJobId(),
        connectionUpdaterInput.getAttemptId(),
        standardSyncOutput.orElse(null),
        FailureHelper.failureSummary(failures, partialSuccess)));

    final int maxAttempt = configFetchActivity.getMaxAttempt().getMaxAttempt();
    final int attemptNumber = connectionUpdaterInput.getAttemptNumber();

    // todo (cgardens) - why is the previous run responsible for this? can the create job / attempt
    // activity do it? will that make it easier to recover?
    if (maxAttempt > attemptNumber) {
      // restart from failure
      connectionUpdaterInput.setAttemptNumber(attemptNumber + 1);
      connectionUpdaterInput.setFromFailure(true);
    } else {
      jobCreationAndStatusUpdateActivity.jobFailure(new JobFailureInput(
          connectionUpdaterInput.getJobId(),
          "Job failed after too many retries for connection " + connectionId));

      // todo (cgardens) - what is the magic number wait for?
      Workflow.await(Duration.ofMinutes(1), () -> skipScheduling());

      resetNewConnectionInput(connectionUpdaterInput);
    }
  }

  private void resetNewConnectionInput(final ConnectionUpdaterInput connectionUpdaterInput) {
    connectionUpdaterInput.setJobId(null);
    connectionUpdaterInput.setAttemptNumber(1); // todo (cgardens) - why?
    connectionUpdaterInput.setFromFailure(false);
  }

  @Override
  public void submitManualSync() {
    if (workflowState.isRunning()) {
      log.info("Can't schedule a manual workflow if a sync is running for connection {}", connectionId);
      return;
    }

    // todo (cgardens) - what happens if it goes into running in between line 313 and here?
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
    // todo (cgardens) - do we actually need to set setResetConnection(true);? doesn't
    // setCancelledForReset(true); do it at the end of the workflow?
    workflowState.setResetConnection(true);
    if (workflowState.isRunning()) {
      workflowState.setCancelledForReset(true);
      syncWorkflowCancellationScope.cancel();
    }
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

  // todo (cgardens) - i'm confused by the name of the method. it is called skipScheduling but then
  // skipScheduling is only one piece of the conditional. the skip scheduling concept needs to be
  // clarified. the method name probably also needs to be updated.
  private Boolean skipScheduling() {
    return workflowState.isSkipScheduling() || workflowState.isDeleted() || workflowState.isUpdated() || workflowState.isResetConnection();
  }

  // todo (cgardens) - this method name could use some love. kinda unclear what is is doing.
  // especially the mutations of connectionUpdaterInput are hard to follow.
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

}
