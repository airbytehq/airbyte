/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.airbyte.workers.temporal.TemporalJobType;
import io.airbyte.workers.temporal.exception.NonRetryableException;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity.ScheduleRetrieverInput;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivity;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivity.SyncInput;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivity.SyncOutput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationActivity;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationActivity.AttemptCreationInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationActivity.AttemptCreationOutput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationActivity.JobCreationInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationActivity.JobCreationOutput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationActivity.JobSuccessInput;
import io.airbyte.workers.temporal.scheduling.shared.ActivityConfiguration;
import io.airbyte.workers.temporal.sync.SyncWorkflow;
import io.temporal.api.enums.v1.ParentClosePolicy;
import io.temporal.workflow.CancellationScope;
import io.temporal.workflow.ChildWorkflowOptions;
import io.temporal.workflow.Workflow;
import java.util.Optional;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class ConnectionUpdaterWorkflowImpl implements ConnectionUpdaterWorkflow {

  private boolean isRunning = false;
  private boolean isDeleted = false;
  private boolean skipScheduling = false;

  private final GenerateInputActivity getSyncInputActivity = Workflow.newActivityStub(GenerateInputActivity.class, ActivityConfiguration.OPTIONS);
  private final JobCreationActivity jobCreationActivity = Workflow.newActivityStub(JobCreationActivity.class, ActivityConfiguration.OPTIONS);
  private final ConfigFetchActivity configFetchActivity = Workflow.newActivityStub(ConfigFetchActivity.class, ActivityConfiguration.OPTIONS);

  private final CancellationScope syncWorkflowCancellationScope = CancellationScope.current();

  public ConnectionUpdaterWorkflowImpl() {}

  @Override
  public SyncResult run(final ConnectionUpdaterInput connectionUpdaterInput) throws NonRetryableException {
    try {

      final Optional<Long> maybeJobId = connectionUpdaterInput.getJobId().or(() -> {
        final JobCreationOutput jobCreationOutput = jobCreationActivity.createNewJob(new JobCreationInput(
            connectionUpdaterInput.getConnectionId()));

        return Optional.ofNullable(jobCreationOutput.getJobId());
      });

      final Optional<Integer> maybeAttemptId = connectionUpdaterInput.getAttemptId().or(() -> maybeJobId.map(jobId -> {
        final AttemptCreationOutput attemptCreationOutput = jobCreationActivity.createNewAttempt(new AttemptCreationInput(
            jobId));
        return attemptCreationOutput.getAttemptId();
      }));

      final ConfigFetchActivity.ScheduleRetrieverInput scheduleRetrieverInput = new ScheduleRetrieverInput(
          connectionUpdaterInput.getConnectionId());

      final ConfigFetchActivity.ScheduleRetrieverOutput scheduleRetrieverOutput = configFetchActivity.getPeriodicity(scheduleRetrieverInput);

      Workflow.await(scheduleRetrieverOutput.getPeriodicity(), () -> skipScheduling() || connectionUpdaterInput.isFromFailure());

      // TODO: Fetch config (maybe store it in GCS)
      log.info("Starting child WF");

      final SyncInput getSyncInputActivitySyncInput = new SyncInput(
          maybeAttemptId.get(),
          maybeJobId.get(),
          connectionUpdaterInput.getJobConfig());

      final SyncOutput syncWorkflowInputs = getSyncInputActivity.getSyncWorkflowInput(getSyncInputActivitySyncInput);

      final SyncWorkflow childSync = Workflow.newChildWorkflowStub(SyncWorkflow.class,
          ChildWorkflowOptions.newBuilder()
              .setWorkflowId("sync_" + connectionUpdaterInput.getJobId())
              .setTaskQueue(TemporalJobType.SYNC.name())
              // This will cancel the child workflow when the parent is terminated
              .setParentClosePolicy(ParentClosePolicy.PARENT_CLOSE_POLICY_TERMINATE)
              .build());

      final UUID connectionId = connectionUpdaterInput.getConnectionId();

      log.error("Running for: " + connectionId);
      childSync.run(
          syncWorkflowInputs.getJobRunConfig(),
          syncWorkflowInputs.getSourceLauncherConfig(),
          syncWorkflowInputs.getDestinationLauncherConfig(),
          syncWorkflowInputs.getSyncInput(),
          connectionId);

      if (isDeleted) {
        return new SyncResult(true);
      } else {
        jobCreationActivity.jobSuccess(new JobSuccessInput(
            Long.parseLong(syncWorkflowInputs.getJobRunConfig().getJobId()),
            syncWorkflowInputs.getJobRunConfig().getAttemptId().intValue()));

        connectionUpdaterInput.setJobId(Optional.empty());
        connectionUpdaterInput.setFromFailure(false);
      }
    } catch (final Exception e) {
      // TODO: Do we need to stop retrying at some points
      log.error("The connection update workflow has failed, will create a new attempt.", e);

      connectionUpdaterInput.setFromFailure(true);
    } finally {
      connectionUpdaterInput.setAttemptId(Optional.empty());
      Workflow.continueAsNew(connectionUpdaterInput);
    }
    // This should not be reachable as we always continue as new even if there is a failure
    return null;
  }

  @Override
  public void updateSchedule(final SchedulingInput input) {

  }

  @Override
  public void submitManualSync() {
    if (isRunning) {
      log.info("Can't schedule a manual workflow if a sync is running for this connection");
      return;
    }

    isRunning = true;
  }

  @Override
  public void skipWaitForScheduling() {
    skipScheduling = true;
  }

  @Override
  public void deleteConnection() {
    syncWorkflowCancellationScope.cancel("The parent workflow got deleted");
    isDeleted = true;
  }

  @Override
  public WorkflowState getState() {
    return new WorkflowState(
        isRunning,
        isDeleted,
        skipScheduling);
  }

  private Boolean skipScheduling() {
    return skipScheduling;
  }

}
