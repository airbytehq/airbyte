/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.airbyte.workers.temporal.scheduling.state.WorkflowState;
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
  void run(ConnectionUpdaterInput connectionUpdaterInput);

  @SignalMethod
  void submitManualSync();

  @SignalMethod
  void cancelJob();

  @SignalMethod
  void deleteConnection();

  @SignalMethod
  void connectionUpdated();

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
