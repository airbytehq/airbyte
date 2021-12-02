/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.airbyte.workers.temporal.TemporalJobType;
import io.airbyte.workers.temporal.scheduling.activities.GetSyncInputActivity;
import io.airbyte.workers.temporal.scheduling.shared.ActivityConfiguration;
import io.airbyte.workers.temporal.sync.SyncWorkflow;
import io.temporal.api.enums.v1.ParentClosePolicy;
import io.temporal.workflow.CancellationScope;
import io.temporal.workflow.ChildWorkflowOptions;
import io.temporal.workflow.Workflow;
import java.time.Duration;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class ConnectionUpdaterWorkflowImpl implements ConnectionUpdaterWorkflow {

  private boolean isRunning = false;
  private boolean isDeleted = false;
  private boolean skipScheduling = false;
  private final GetSyncInputActivity getSyncInputActivity = Workflow.newActivityStub(GetSyncInputActivity.class, ActivityConfiguration.OPTIONS);

  private CancellationScope syncWorkflowCancellationScope = CancellationScope.current();

  public ConnectionUpdaterWorkflowImpl() {}

  @Override
  public SyncResult run(final ConnectionUpdaterInput connectionUpdaterInput) {
    // TODO: bmoric get time to wait through an activity
    final Duration timeToWait = Duration.ofMinutes(5);

    Workflow.await(timeToWait, () -> skipScheduling());

    // TODO: Fetch config (maybe store it in GCS)
    log.info("Starting child WF");

    final GetSyncInputActivity.Input getSyncInputActivityInput = new GetSyncInputActivity.Input(
        connectionUpdaterInput.getAttemptId(),
        connectionUpdaterInput.getJobId(),
        connectionUpdaterInput.getJobConfig());

    final GetSyncInputActivity.Output syncWorkflowInputs = getSyncInputActivity.getSyncWorkflowInput(getSyncInputActivityInput);

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

    syncWorkflowCancellationScope = Workflow.newCancellationScope(() -> childSync.run(null, null, null, null, null));

    if (isDeleted) {
      return new SyncResult(true);
    } else {
      // TODO: Create a new job here
      Workflow.continueAsNew(connectionUpdaterInput);
    }
    // This should not be reachable
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
