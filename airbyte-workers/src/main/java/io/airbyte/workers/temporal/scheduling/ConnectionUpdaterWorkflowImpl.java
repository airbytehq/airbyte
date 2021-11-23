package io.airbyte.workers.temporal.scheduling;

import io.temporal.workflow.Workflow;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class ConnectionUpdaterWorkflowImpl implements ConnectionUpdaterWorkflow {

  private boolean canStart = false;
  private boolean isRunning = false;

  @Override public SyncResult run() {
    Workflow.await(() -> canStart);
    return null;
  }

  @Override public void updateSchedule(final SchedulingInput input) {
    canStart = true;
  }

  @Override public ManualSyncOutput submitManualSync() {
    if (isRunning) {
      log.info("Can't schedule a manual workflow is a sync is running for this connection");
      return new ManualSyncOutput(false);
    }

    isRunning = true;
    canStart = true;

    return new ManualSyncOutput(true);
  }

  private Boolean canStart() {
    return canStart;
  }
}
