/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.temporal.workflow.QueryMethod;
import io.temporal.workflow.SignalMethod;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@WorkflowInterface
public interface ConnectionUpdaterWorkflow {

  @WorkflowMethod
  WorkflowState run(ConnectionUpdaterInput connectionUpdaterInput);

  @SignalMethod
  void submitManualSync();

  @SignalMethod
  void cancelJob();

  @SignalMethod
  void deleteConnection();

  @SignalMethod
  void connectionUpdated();

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class WorkflowState {

    private boolean isRunning;
    private boolean isDeleted;
    private boolean skipScheduling;
    private boolean isUpdated;

  }

  @QueryMethod
  WorkflowState getState();

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class JobInformation {

    private long jobId;
    private int attemptId;

  }

  @QueryMethod
  JobInformation getJobInformation();

}
