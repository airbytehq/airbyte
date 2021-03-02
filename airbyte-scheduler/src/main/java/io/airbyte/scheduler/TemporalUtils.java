package io.airbyte.scheduler;

import io.temporal.client.WorkflowClient;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.serviceclient.WorkflowServiceStubsOptions;

public class TemporalUtils {
    private static final WorkflowServiceStubsOptions TEMPORAL_OPTIONS = WorkflowServiceStubsOptions.newBuilder()
            .setTarget("temporal:7233")
            .build();

    public static final WorkflowServiceStubs TEMPORAL_SERVICE = WorkflowServiceStubs.newInstance(TEMPORAL_OPTIONS);

    public static final WorkflowClient TEMPORAL_CLIENT = WorkflowClient.newInstance(TEMPORAL_SERVICE);
}
