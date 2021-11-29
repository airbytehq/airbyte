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
  SyncResult run();

  @SignalMethod
  void updateSchedule(SchedulingInput input);

  @SignalMethod
  // Maybe query to have a return type??
  void submitManualSync();

  @SignalMethod
  void deleteConnection();

  @SignalMethod
  void readyToStart();

  @QueryMethod
  WorkflowState getState();

}
