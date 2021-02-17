package io.airbyte.workflows;

import io.airbyte.activities.GetSpecActivity;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.temporal.activity.ActivityOptions;
import io.temporal.common.RetryOptions;
import io.temporal.workflow.Workflow;

import java.time.Duration;

public class GetSpecWorkflowImpl implements GetSpecWorkflow {
    private static final RetryOptions RETRY_OPTIONS = RetryOptions.newBuilder()
            .setInitialInterval(Duration.ofSeconds(1))
            // .setMaximumInterval(Duration.ofSeconds(100))
            // .setBackoffCoefficient(2)
            .setMaximumAttempts(2)
            .build();

    private static final ActivityOptions OPTIONS = ActivityOptions.newBuilder()
            .setStartToCloseTimeout(Duration.ofMinutes(30))
            // .setScheduleToCloseTimeout(Duration.ofMinutes(30))
            // .setScheduleToStartTimeout(Duration.ofMinutes(30))
            // .setHeartbeatTimeout(Duration.ofMinutes(30))
            .setRetryOptions(RETRY_OPTIONS)
            .build();

    private final GetSpecActivity getSpecActivity = Workflow.newActivityStub(GetSpecActivity.class, OPTIONS);

    @Override
    public ConnectorSpecification getSpec(String dockerImage) {
        try {
            return getSpecActivity.getSpec(dockerImage);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
