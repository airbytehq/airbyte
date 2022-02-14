/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.cron;

import io.temporal.api.enums.v1.ParentClosePolicy;
import io.temporal.workflow.ChildWorkflowCancellationType;
import io.temporal.workflow.ChildWorkflowOptions;
import io.temporal.workflow.Workflow;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@WorkflowInterface
public interface ManualWorkflowWorkflow {

  Logger LOGGER = LoggerFactory.getLogger(ManualWorkflowWorkflow.class);
  String WORKFLOW_NAME = "manual-workflow";

  @WorkflowMethod
  public void manual(String id, String key, String workflowName);

  class ManualWorkflowWorkflowImpl implements ManualWorkflowWorkflow {

    @Override
    public void manual(final String id, final String key, final String workflowName) {
      LOGGER.info("running update workflow (outer)");

      final ChildWorkflowOptions.Builder deleteWorkflowOptionsBuilder = ChildWorkflowOptions.newBuilder()
          .setTaskQueue(DeleteWorkflowWorkflow.WORKFLOW_NAME)
          .setParentClosePolicy(ParentClosePolicy.PARENT_CLOSE_POLICY_TERMINATE)
          .setCancellationType(ChildWorkflowCancellationType.WAIT_CANCELLATION_COMPLETED);
      final DeleteWorkflowWorkflow deleteWorkflowWorkflow =
          Workflow.newChildWorkflowStub(DeleteWorkflowWorkflow.class, deleteWorkflowOptionsBuilder.build());
      // todo (cgardens) - need to update the logic here. should be that if there is something running we
      // can determine if is actually running or
      // waiting to run. if it is waiting, then we terminate and do a manual. if it is running, do
      // nothing.
      final String originalCronSchedule = deleteWorkflowWorkflow.delete(id); // null if there was none.

      final ChildWorkflowOptions.Builder createWorkflowOptionsBuilder = ChildWorkflowOptions.newBuilder()
          .setTaskQueue(CreateWorkflowWorkflow.WORKFLOW_NAME)
          .setParentClosePolicy(ParentClosePolicy.PARENT_CLOSE_POLICY_TERMINATE)
          .setCancellationType(ChildWorkflowCancellationType.WAIT_CANCELLATION_COMPLETED);
      // .setWorkflowId(id);
      final CreateWorkflowWorkflow createWorkflowWorkflow =
          Workflow.newChildWorkflowStub(CreateWorkflowWorkflow.class, createWorkflowOptionsBuilder.build());

      // run now
      createWorkflowWorkflow.createWorkflow(id, key + "-manual", null, workflowName);

      // restore workflow (if always manual do nothing)
      if (originalCronSchedule != null) {
        createWorkflowWorkflow.createWorkflow(id, key, originalCronSchedule, workflowName);
      }
      // else nothing to restore.
    }

  }

}
