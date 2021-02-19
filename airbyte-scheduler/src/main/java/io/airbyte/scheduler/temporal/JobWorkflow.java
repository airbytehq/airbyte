package io.airbyte.scheduler.temporal;

import io.airbyte.scheduler.Job;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;

@WorkflowInterface
public interface JobWorkflow {
    @WorkflowMethod
    void run(Job job);
}
