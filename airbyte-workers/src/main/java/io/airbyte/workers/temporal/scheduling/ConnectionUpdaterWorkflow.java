/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.temporal.workflow.QueryMethod;
import io.temporal.workflow.SignalMethod;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;

@WorkflowInterface
public interface ConnectionUpdaterWorkflow {

  @WorkflowMethod
  SyncResult run(ConnectionUpdaterInput connectionUpdaterInput);

  @SignalMethod
  void updateSchedule(SchedulingInput input);

  @SignalMethod
  void submitManualSync();

  @SignalMethod
  void skipWaitForScheduling();

  @SignalMethod
  void deleteConnection();

  @QueryMethod
  WorkflowState getState();

}
