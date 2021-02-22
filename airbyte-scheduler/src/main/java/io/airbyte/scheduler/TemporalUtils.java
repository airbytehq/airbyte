package io.airbyte.scheduler;

import io.airbyte.scheduler.temporal.JobWorkflow;
import io.airbyte.scheduler.temporal.SpecWorkflow;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.serviceclient.WorkflowServiceStubsOptions;

public class TemporalUtils {
    public static final String JOB_WORKFLOW_QUEUE = "JOB_WORKFLOW_QUEUE";
    public static final String SPEC_WORKFLOW_QUEUE = "SPEC_WORKFLOW_QUEUE";

    private static final WorkflowServiceStubsOptions TEMPORAL_OPTIONS = WorkflowServiceStubsOptions.newBuilder()
            .setTarget("temporal:7233")
            .build();

    public static final WorkflowServiceStubs TEMPORAL_SERVICE = WorkflowServiceStubs.newInstance(TEMPORAL_OPTIONS);

    public static final WorkflowClient TEMPORAL_CLIENT = WorkflowClient.newInstance(TEMPORAL_SERVICE);

    private static final WorkflowOptions JOB_WORKFLOW_OPTIONS = WorkflowOptions.newBuilder()
            .setTaskQueue(JOB_WORKFLOW_QUEUE)
            .build();

    private static final WorkflowOptions SPEC_WORKFLOW_OPTIONS = WorkflowOptions.newBuilder()
            .setTaskQueue(SPEC_WORKFLOW_QUEUE)
            .build();


    public static JobWorkflow getJobWorkflow() {
      return TEMPORAL_CLIENT.newWorkflowStub(JobWorkflow.class, JOB_WORKFLOW_OPTIONS);
    }

    public static SpecWorkflow getSpecWorkflow() {
        return TEMPORAL_CLIENT.newWorkflowStub(SpecWorkflow.class, SPEC_WORKFLOW_OPTIONS);
    }
}
