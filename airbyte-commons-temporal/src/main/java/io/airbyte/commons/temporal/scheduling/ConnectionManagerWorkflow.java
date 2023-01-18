/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal.scheduling;

import io.airbyte.commons.temporal.scheduling.state.WorkflowState;
import io.temporal.workflow.QueryMethod;
import io.temporal.workflow.SignalMethod;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@WorkflowInterface
public interface ConnectionManagerWorkflow {

  long NON_RUNNING_JOB_ID = -1;
  int NON_RUNNING_ATTEMPT_ID = -1;

  /**
   * Workflow method to launch a {@link ConnectionManagerWorkflow}. Launches a workflow responsible
   * for scheduling syncs. This workflow will run and then continue running until deleted.
   */
  @WorkflowMethod
  void run(ConnectionUpdaterInput connectionUpdaterInput);

  /**
   * Send a signal that will bypass the waiting time and run a sync. Nothing will happen if a sync is
   * already running.
   */
  @SignalMethod
  void submitManualSync();

  /**
   * Cancel all the current executions of a sync and mark the set the status of the job as canceled.
   * Nothing will happen if a sync is not running.
   */
  @SignalMethod
  void cancelJob();

  /**
   * Cancel a running workflow and then delete the connection and finally make the workflow to stop
   * instead of continuing as new.
   */
  @SignalMethod
  void deleteConnection();

  /**
   * Signal that the connection config has been updated. If nothing was currently running, it will
   * continue the workflow as new, which will reload the config. Nothing will happend if a sync is
   * running.
   */
  @SignalMethod
  void connectionUpdated();

  @SignalMethod
  void resetConnection();

  @SignalMethod
  void resetConnectionAndSkipNextScheduling();

  /**
   * Return the current state of the workflow.
   */
  @QueryMethod
  WorkflowState getState();

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class JobInformation {

    private long jobId;
    private int attemptId;

  }

  /**
   * Return which job and attempt is currently run by the workflow.
   */
  @QueryMethod
  JobInformation getJobInformation();

}
