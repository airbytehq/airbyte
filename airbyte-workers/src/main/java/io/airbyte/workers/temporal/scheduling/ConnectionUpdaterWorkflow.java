/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.temporal.workflow.SignalMethod;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;

@WorkflowInterface
public interface ConnectionUpdaterWorkflow {

  @WorkflowMethod
  SyncResult run();

  @SignalMethod
  void updateSchedule(SchedulingInput input);

  @SignalMethod
  ManualSyncOutput submitManualSync();

  @SignalMethod
  void deleteConnection();
}
