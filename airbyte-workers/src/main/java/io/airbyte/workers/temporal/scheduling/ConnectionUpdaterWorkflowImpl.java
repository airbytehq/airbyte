/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.airbyte.workers.temporal.sync.SyncWorkflow;
import io.temporal.workflow.ChildWorkflowCancellationType;
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

  @Override
  public SyncResult run() {
    Workflow.await(() -> canStart());

    // TODO: bmoric get time to wait through an activity
    final Duration timeToWait = Duration.ofSeconds(5);

    Workflow.await(timeToWait, () -> skipScheduling());

    // TODO: Fetch config (maybe store it in GCS)
    log.info("Starting child WF");
    Workflow.newChildWorkflowStub(SyncWorkflow.class,
        ChildWorkflowOptions.newBuilder()
            // This will cancel the child workflow when the parent is terminated
            .setCancellationType(ChildWorkflowCancellationType.TRY_CANCEL)
            .build()
    );

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
  public ManualSyncOutput submitManualSync() {
    if (isRunning) {
      log.info("Can't schedule a manual workflow is a sync is running for this connection");
      return new ManualSyncOutput(false);
    }

    isRunning = true;
    canStart = true;

    return new ManualSyncOutput(true);
  }

  @Override
  public void deleteConnection() {
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
