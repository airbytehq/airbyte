/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.airbyte.config.StandardSyncInput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
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

  private boolean canStart;
  private boolean isRunning = false;
  private boolean isDeleted = false;
  private final boolean skipScheduling = false;
  CancellationScope syncWorkflowCancellationScope = CancellationScope.current();

  public ConnectionUpdaterWorkflowImpl() {
    canStart = false;
  }

  public ConnectionUpdaterWorkflowImpl(final ConnectionUpdaterWorkflowConfig connectionUpdaterWorkflowConfig) {
    canStart = !connectionUpdaterWorkflowConfig.isFirstStart();
  }

  @Override
  public SyncResult run(final ConnectionUpdaterInput connectionUpdaterInput) {
    // Workflow.await(() -> canStart());

    // TODO: bmoric get time to wait through an activity
    final Duration timeToWait = Duration.ofSeconds(5);

    Workflow.await(timeToWait, () -> skipScheduling());

    // TODO: Fetch config (maybe store it in GCS)
    log.info("Starting child WF");

    final SyncWorkflow childSync = Workflow.newChildWorkflowStub(SyncWorkflow.class,
        ChildWorkflowOptions.newBuilder()
            .setWorkflowId("sync_" + connectionUpdaterInput.getConnectionId())
            // This will cancel the child workflow when the parent is terminated
            .setParentClosePolicy(ParentClosePolicy.PARENT_CLOSE_POLICY_ABANDON)
            .build());

    final JobRunConfig jobRunConfig = new JobRunConfig();
    final IntegrationLauncherConfig sourceLauncherConfig = new IntegrationLauncherConfig();
    final IntegrationLauncherConfig destinationLauncherConfig = new IntegrationLauncherConfig();
    final StandardSyncInput syncInput = new StandardSyncInput();
    final UUID connectionId = connectionUpdaterInput.getConnectionId();

    log.error("Running for: " + connectionId);
    childSync.run(jobRunConfig, sourceLauncherConfig, destinationLauncherConfig, syncInput, connectionId);

    syncWorkflowCancellationScope = Workflow.newCancellationScope(() -> childSync.run(null, null, null, null, null));

    if (isDeleted) {
      return new SyncResult(true);
    } else {
      canStart = true;
      Workflow.continueAsNew(connectionUpdaterInput);
    }
    // This should not be reachable
    return null;
  }

  @Override
  public void updateSchedule(final SchedulingInput input) {
    canStart = true;
  }

  @Override
  public void submitManualSync() {
    if (isRunning) {
      log.info("Can't schedule a manual workflow if a sync is running for this connection");
      return;
    }

    isRunning = true;
    canStart = true;
  }

  @Override
  public void deleteConnection() {
    syncWorkflowCancellationScope.cancel("The parent workflow got deleted");
    canStart = false;
    isDeleted = true;
  }

  @Override
  public void readyToStart() {
    canStart = true;
  }

  @Override
  public WorkflowState getState() {
    return new WorkflowState(
        canStart,
        isRunning,
        isDeleted,
        skipScheduling);
  }

  private Boolean canStart() {
    return canStart;
  }

  private Boolean skipScheduling() {
    return skipScheduling;
  }

}
