/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.cron;

import io.airbyte.workers.temporal.scheduling.shared.ActivityConfiguration;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.client.WorkflowStub;
import io.temporal.workflow.Workflow;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@WorkflowInterface
public interface UpdateWorkflowWorkflow {

  Logger LOGGER = LoggerFactory.getLogger(UpdateWorkflowWorkflow.class);
  String WORKFLOW_NAME = "update-workflow-workflow";

  @WorkflowMethod
  void updateWorkflow(String id, String key, String cronString, String workflowName);

  class UpdateWorkflowWorkflowImpl implements UpdateWorkflowWorkflow {

    private final UpdateWorkflowActivity updateActivity =
        Workflow.newActivityStub(UpdateWorkflowActivity.class, ActivityConfiguration.LONG_RUN_OPTIONS);

    @Override
    public void updateWorkflow(final String id, final String key, final String cronString, final String workflowName) {
      LOGGER.info("running update workflow (outer)");
      updateActivity.update(id, key, cronString, workflowName);

    }

  }

  @ActivityInterface
  public interface UpdateWorkflowActivity {

    @ActivityMethod
    void update(final String id, final String key, final String cronString, final String workflowName);

  }

  class UpdateWorkflowActivityImpl implements UpdateWorkflowActivity {

    private final WorkflowClient client;

    public UpdateWorkflowActivityImpl(final WorkflowClient client) {
      this.client = client;
    }

    @Override
    public void update(final String id, final String key, final String cronString, final String workflowName) {
      LOGGER.debug("running update workflow (inner)");
      final WorkflowStub workflowStub = client.newUntypedWorkflowStub(id);
      // workflowStub.cancel();
      LOGGER.debug("terminating: started");
      workflowStub.terminate("update scheduler");
      LOGGER.debug("terminating: done");

      final WorkflowOptions.Builder builder = WorkflowOptions.newBuilder()
          .setTaskQueue(workflowName)
          .setWorkflowId(id);

      // manual sync
      if (cronString != null) {
        builder.setCronSchedule(cronString);
      }

      LOGGER.debug("getting stub: started");
      final BasicWorkflow basicWorkflow = client.newWorkflowStub(BasicWorkflow.class, builder.build());
      LOGGER.debug("getting stub: done");
      LOGGER.debug("running workflow: started");
      WorkflowClient.start((input, rootPath1) -> {
        return basicWorkflow.run(input);
      }, id, key);
      LOGGER.debug("running workflow: done");
    }

  }

}
