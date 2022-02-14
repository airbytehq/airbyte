/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.cron;

import io.airbyte.workers.temporal.scheduling.shared.ActivityConfiguration;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.workflow.Workflow;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@WorkflowInterface
public interface CreateWorkflowWorkflow {

  Logger LOGGER = LoggerFactory.getLogger(CreateWorkflowWorkflow.class);
  String WORKFLOW_NAME = "create-workflow-workflow";

  @WorkflowMethod
  void createWorkflow(String id, String key, String cronString, String workflowName);

  class CreateWorkflowWorkflowImpl implements CreateWorkflowWorkflow {

    private final CreateWorkflowActivity createActivity =
        Workflow.newActivityStub(CreateWorkflowActivity.class, ActivityConfiguration.LONG_RUN_OPTIONS);

    @Override
    public void createWorkflow(final String id, final String key, final String cronString, final String workflowName) {
      createActivity.create(id, key, cronString, workflowName);
      // createWorkflow(id, key, cronString, workflowName);
    }

    // private static void createWorkflow(final String id, final String key, final String cronString,
    // final String workflowName) {
    // LOGGER.info("running create workflow");
    // // switch to using temporal client.
    // final ChildWorkflowOptions.Builder builder = ChildWorkflowOptions.newBuilder()
    // .setTaskQueue(workflowName)
    // .setParentClosePolicy(ParentClosePolicy.PARENT_CLOSE_POLICY_UNSPECIFIED)
    // .setCancellationType(ChildWorkflowCancellationType.ABANDON)
    // .setWorkflowId(id);
    //
    // // manual sync
    // if (cronString != null) {
    // builder.setCronSchedule(cronString);
    // }
    //
    // final BasicWorkflow basicWorkflow1 = Workflow.newChildWorkflowStub(BasicWorkflow.class,
    // builder.build());
    //// WorkflowClient.start(basicWorkflow1::run, id, rootPath);
    // Async.procedure((input, rootPath1) -> basicWorkflow1.run(input), id, key);
    // final Promise<WorkflowExecution> childExecution = Workflow.getWorkflowExecution(basicWorkflow1);
    //
    // LOGGER.info("child workflow start: starting");
    // // Wait for child to start
    // childExecution.get(); // don't understand why it doesn't start running without this.
    // LOGGER.info("child workflow start: started");
    // }

  }

  @ActivityInterface
  interface CreateWorkflowActivity {

    @ActivityMethod
    void create(final String id, final String key, final String cronString, final String workflowName);

  }

  class CreateWorkflowActivityImpl implements CreateWorkflowActivity {

    private final WorkflowClient client;

    public CreateWorkflowActivityImpl(final WorkflowClient client) {
      this.client = client;
    }

    @Override
    public void create(final String id, final String key, final String cronString, final String workflowName) {
      LOGGER.info("running create workflow");
      final WorkflowOptions.Builder builder = WorkflowOptions.newBuilder()
          .setTaskQueue(workflowName)
          .setWorkflowId(id);

      // manual sync
      if (cronString != null) {
        builder.setCronSchedule(cronString);
      }

      final BasicWorkflow basicWorkflow = client.newWorkflowStub(BasicWorkflow.class, builder.build());

      LOGGER.debug("child workflow start: starting");
      WorkflowClient.start(basicWorkflow::run, key);
      LOGGER.debug("child workflow start: started");
    }

  }

}
