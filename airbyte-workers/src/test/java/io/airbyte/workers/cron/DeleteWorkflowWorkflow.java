/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.cron;

import io.airbyte.workers.temporal.scheduling.shared.ActivityConfiguration;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import io.temporal.api.common.v1.WorkflowExecution;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowStub;
import io.temporal.workflow.Workflow;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@WorkflowInterface
public interface DeleteWorkflowWorkflow {

  Logger LOGGER = LoggerFactory.getLogger(DeleteWorkflowWorkflow.class);
  String WORKFLOW_NAME = "delete-workflow-workflow";

  @WorkflowMethod
  public String delete(String id);

  class DeleteWorkflowWorkflowImpl implements DeleteWorkflowWorkflow {

    private final TerminateWorkflowActivity terminateWorkflowActivity =
        Workflow.newActivityStub(TerminateWorkflowActivity.class, ActivityConfiguration.LONG_RUN_OPTIONS);

    @Override
    public String delete(final String id) {
      LOGGER.debug("running delete workflow");

      // should detect if one is running and remember its cron string.
      return terminateWorkflowActivity.terminate(id);
    }

  }

  @ActivityInterface
  interface TerminateWorkflowActivity {

    @ActivityMethod
    String terminate(final String id);

  }

  class TerminateWorkflowActivityImpl implements TerminateWorkflowActivity {

    private final WorkflowClient client;

    public TerminateWorkflowActivityImpl(final WorkflowClient client) {
      this.client = client;
    }

    @Override
    public String terminate(final String id) {

      final WorkflowExecution workflowExecution = WorkflowExecution.newBuilder()
          .setWorkflowId(id)
          .build();

      // either scheduled or a manual run.
      if (TemporalUtils.isWorkflowActive(client.getWorkflowServiceStubs(), workflowExecution)) {
        final Optional<String> scheduleIfExists = TemporalUtils.getScheduleIfExists(client.getWorkflowServiceStubs(), workflowExecution);

        final WorkflowStub workflowStub = client.newUntypedWorkflowStub(id);
        LOGGER.info("terminating: started");
        // workflowStub.cancel();
        workflowStub.terminate("update scheduler");
        LOGGER.info("terminating: done");

        // means scheduled workflow exists
        if (scheduleIfExists.isPresent()) {
          return scheduleIfExists.get();

          // means manual run is in progress.
        } else {
          return null;
        }

      } else {
        // do nothing.
        return null;
      }

    }

  }

}
