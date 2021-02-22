package io.airbyte.scheduler;

import io.airbyte.scheduler.temporal.CheckConnectionWorkflow;
import io.airbyte.scheduler.temporal.DiscoverWorkflow;
import io.airbyte.scheduler.temporal.JobWorkflow;
import io.airbyte.scheduler.temporal.SpecWorkflow;
import io.airbyte.workers.DefaultCheckConnectionWorker;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.serviceclient.WorkflowServiceStubsOptions;

public class TemporalUtils {
    public static final String JOB_WORKFLOW_QUEUE = "JOB_WORKFLOW_QUEUE";
    public static final String SPEC_WORKFLOW_QUEUE = "SPEC";
    public static final String DISCOVER_WORKFLOW_QUEUE = "DISCOVER";
    public static final String CHECK_CONNECTION_WORKFLOW_QUEUE = "CHECK_CONNECTION";

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

    private static final WorkflowOptions DISCOVER_WORKFLOW_OPTIONS = WorkflowOptions.newBuilder()
            .setTaskQueue(DISCOVER_WORKFLOW_QUEUE)
            .build();

    private static final WorkflowOptions CHECK_CONNECTION_WORKFLOW_OPTIONS = WorkflowOptions.newBuilder()
            .setTaskQueue(CHECK_CONNECTION_WORKFLOW_QUEUE)
            .build();

    public static JobWorkflow getJobWorkflow() {
      return TEMPORAL_CLIENT.newWorkflowStub(JobWorkflow.class, JOB_WORKFLOW_OPTIONS);
    }

    public static SpecWorkflow getSpecWorkflow() {
        return TEMPORAL_CLIENT.newWorkflowStub(SpecWorkflow.class, SPEC_WORKFLOW_OPTIONS);
    }

    public static DiscoverWorkflow getDiscoverWorkflow() {
        return TEMPORAL_CLIENT.newWorkflowStub(DiscoverWorkflow.class, DISCOVER_WORKFLOW_OPTIONS);
    }

    public static CheckConnectionWorkflow getCheckConnectionWorkflow() {
        return TEMPORAL_CLIENT.newWorkflowStub(CheckConnectionWorkflow.class, CHECK_CONNECTION_WORKFLOW_OPTIONS);
    }
}
