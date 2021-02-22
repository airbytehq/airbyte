package io.airbyte.scheduler.temporal;

import io.airbyte.config.JobOutput;
import io.airbyte.scheduler.Job;
import io.airbyte.workers.OutputAndStatus;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;

@WorkflowInterface
public interface JobWorkflow {
    @WorkflowMethod
    OutputAndStatus<JobOutput> run(Job job);
}
