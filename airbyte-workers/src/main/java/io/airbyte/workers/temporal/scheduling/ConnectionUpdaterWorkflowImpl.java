/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.airbyte.workers.temporal.sync.SyncWorkflow;
import io.temporal.api.enums.v1.ParentClosePolicy;
import io.temporal.workflow.CancellationScope;
import io.temporal.workflow.ChildWorkflowOptions;
import io.temporal.workflow.Workflow;
import java.time.Duration;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class ConnectionUpdaterWorkflowImpl implements ConnectionUpdaterWorkflow {

  private boolean canStart = false;
  private boolean isRunning = false;
  private boolean isDeleted = false;
  private final boolean skipScheduling = false;
  // private Optional<SyncWorkflow> childSync = Optional.empty();
  CancellationScope syncWorkflowCancellationScope = CancellationScope.current();

  @Override
  public SyncResult run() {
    Workflow.await(() -> canStart());

    // TODO: bmoric get time to wait through an activity
    final Duration timeToWait = Duration.ofSeconds(5);

    Workflow.await(timeToWait, () -> skipScheduling());

    // TODO: Fetch config (maybe store it in GCS)
    log.info("Starting child WF");

    final SyncWorkflow childSync = Workflow.newChildWorkflowStub(SyncWorkflow.class,
        ChildWorkflowOptions.newBuilder()
            // This will cancel the child workflow when the parent is terminated
            .setParentClosePolicy(ParentClosePolicy.PARENT_CLOSE_POLICY_ABANDON)
            .build());

    syncWorkflowCancellationScope = Workflow.newCancellationScope(() -> childSync.run(null, null, null, null, null));

    if (isDeleted) {
      return new SyncResult(true);
    } else {
      Workflow.continueAsNew();
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
      log.info("Can't schedule a manual workflow is a sync is running for this connection");
      // return new ManualSyncOutput(false);
    }

    isRunning = true;
    canStart = true;

    // return new ManualSyncOutput(true);
  }

  @Override
  public void deleteConnection() {
    syncWorkflowCancellationScope.cancel("The parent workflow got deleted");
    canStart = false;
    isDeleted = true;
  }

  private Boolean canStart() {
    return canStart;
  }

  private Boolean skipScheduling() {
    return skipScheduling;
  }

}
