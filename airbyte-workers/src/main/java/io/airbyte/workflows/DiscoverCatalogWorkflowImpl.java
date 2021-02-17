package io.airbyte.workflows;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.activities.DiscoverCatalogActivity;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.temporal.activity.ActivityOptions;
import io.temporal.common.RetryOptions;
import io.temporal.workflow.Workflow;

import java.io.IOException;
import java.time.Duration;

public class DiscoverCatalogWorkflowImpl implements DiscoverCatalogWorkflow {


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

    private final DiscoverCatalogActivity discoverCatalogActivity = Workflow.newActivityStub(DiscoverCatalogActivity.class, OPTIONS);

    @Override
    public AirbyteCatalog discoverCatalog(String dockerImage, JsonNode connectionConfig) {
        try {
            return discoverCatalogActivity.discoverCatalog(dockerImage, connectionConfig);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}
