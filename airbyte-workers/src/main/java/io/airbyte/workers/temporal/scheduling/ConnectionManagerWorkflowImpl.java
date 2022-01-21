/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.StandardSyncSummary.ReplicationStatus;
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
import io.temporal.failure.CanceledFailure;
import io.temporal.failure.ChildWorkflowFailure;
import io.temporal.workflow.CancellationScope;
import io.temporal.workflow.ChildWorkflowOptions;
import io.temporal.workflow.Workflow;
import java.time.Duration;
import java.util.Optional;
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

  private final GenerateInputActivity getSyncInputActivity = Workflow.newActivityStub(GenerateInputActivity.class, ActivityConfiguration.OPTIONS);
  private final JobCreationAndStatusUpdateActivity jobCreationAndStatusUpdateActivity =
      Workflow.newActivityStub(JobCreationAndStatusUpdateActivity.class, ActivityConfiguration.OPTIONS);
  private final ConfigFetchActivity configFetchActivity = Workflow.newActivityStub(ConfigFetchActivity.class, ActivityConfiguration.OPTIONS);
  private final ConnectionDeletionActivity connectionDeletionActivity =
      Workflow.newActivityStub(ConnectionDeletionActivity.class, ActivityConfiguration.OPTIONS);

  private CancellationScope syncWorkflowCancellationScope;

  public ConnectionManagerWorkflowImpl() {}

  @Override
  public void run(final ConnectionUpdaterInput connectionUpdaterInput) throws RetryableException {
    try {
      if (connectionUpdaterInput.getWorkflowState() != null) {
        workflowState = connectionUpdaterInput.getWorkflowState();
      }
      try {
        syncWorkflowCancellationScope = Workflow.newCancellationScope(() -> {
          // Scheduling
          final ScheduleRetrieverInput scheduleRetrieverInput = new ScheduleRetrieverInput(
              connectionUpdaterInput.getConnectionId());
          final ScheduleRetrieverOutput scheduleRetrieverOutput = configFetchActivity.getTimeToWait(scheduleRetrieverInput);
          Workflow.await(scheduleRetrieverOutput.getTimeToWait(), () -> skipScheduling() || connectionUpdaterInput.isFromFailure());

          if (!workflowState.isUpdated() && !workflowState.isDeleted()) {
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

            jobCreationAndStatusUpdateActivity.reportJobStart(new ReportJobStartInput(
                maybeJobId.get()));

            final SyncOutput syncWorkflowInputs = getSyncInputActivity.getSyncWorkflowInput(getSyncInputActivitySyncInput);

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

              StandardSyncSummary standardSyncSummary = standardSyncOutput.get().getStandardSyncSummary();

              if (standardSyncSummary != null && standardSyncSummary.getStatus() == ReplicationStatus.FAILED) {
                workflowState.setFailed(true);
              }
            } catch (final ChildWorkflowFailure childWorkflowFailure) {
              if (!(childWorkflowFailure.getCause() instanceof CanceledFailure)) {
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

      if (workflowState.isResetConnection()) {
        connectionUpdaterInput.setResetConnection(true);
        connectionUpdaterInput.setJobId(null);
        connectionUpdaterInput.setAttemptNumber(1);
        connectionUpdaterInput.setFromFailure(false);
        connectionUpdaterInput.setAttemptId(null);
      } else {
        connectionUpdaterInput.setResetConnection(false);
      }

      if (workflowState.isUpdated()) {
        log.error("A connection configuration has changed for the connection {}. The job will be restarted",
            connectionUpdaterInput.getConnectionId());
      } else if (workflowState.isDeleted()) {
        // Stop the runs
        final ConnectionDeletionInput connectionDeletionInput = new ConnectionDeletionInput(connectionUpdaterInput.getConnectionId());
        connectionDeletionActivity.deleteConnection(connectionDeletionInput);
        return;
      } else if (workflowState.isCancelled()) {
        jobCreationAndStatusUpdateActivity.jobCancelled(new JobCancelledInput(
            maybeJobId.get()));
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
        connectionUpdaterInput.getAttemptNumber(),
        standardSyncOutput.orElse(null)));

    connectionUpdaterInput.setJobId(null);
    connectionUpdaterInput.setAttemptNumber(1);
    connectionUpdaterInput.setFromFailure(false);
  }

  private void reportFailure(final ConnectionUpdaterInput connectionUpdaterInput) {
    jobCreationAndStatusUpdateActivity.attemptFailure(new AttemptFailureInput(
        connectionUpdaterInput.getJobId(),
        connectionUpdaterInput.getAttemptNumber()));

    final int maxAttempt = configFetchActivity.getMaxAttempt().getMaxAttempt();
    final int attemptNumber = connectionUpdaterInput.getAttemptNumber();

    if (maxAttempt > attemptNumber) {
      // restart from failure
      connectionUpdaterInput.setAttemptNumber(attemptNumber + 1);
      connectionUpdaterInput.setFromFailure(true);
    } else {
      jobCreationAndStatusUpdateActivity.jobFailure(new JobFailureInput(
          connectionUpdaterInput.getJobId(),
          "Job failed after too many retries"));

      Workflow.await(Duration.ofMinutes(1), () -> skipScheduling());

      connectionUpdaterInput.setJobId(null);
      connectionUpdaterInput.setAttemptNumber(1);
      connectionUpdaterInput.setFromFailure(false);
    }
  }

  @Override
  public void submitManualSync() {
    if (workflowState.isRunning()) {
      log.info("Can't schedule a manual workflow if a sync is running for this connection");
      return;
    }

    workflowState.setSkipScheduling(true);
  }

  @Override
  public void cancelJob() {
    if (!workflowState.isRunning()) {
      log.info("Can't cancel a non-running sync");
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
    if (!workflowState.isRunning()) {
      cancelJob();
    }
    workflowState.setResetConnection(true);
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

  private Boolean skipScheduling() {
    return workflowState.isSkipScheduling() || workflowState.isDeleted() || workflowState.isUpdated() || workflowState.isResetConnection();
  }

  private void continueAsNew(final ConnectionUpdaterInput connectionUpdaterInput) {
    // Continue the workflow as new
    connectionUpdaterInput.setAttemptId(null);
    boolean isDeleted = workflowState.isDeleted();
    workflowState.reset();
    if (!isDeleted) {
      Workflow.continueAsNew(connectionUpdaterInput);
    }
  }

}
