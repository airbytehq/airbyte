package io.airbyte.workflows;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.activities.DiscoverCatalogActivity;
import io.airbyte.activities.GetSpecActivity;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.StandardGetSpecOutput;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.workers.OutputAndStatus;
import io.temporal.activity.ActivityOptions;
import io.temporal.common.RetryOptions;
import io.temporal.workflow.Workflow;

import java.io.IOException;
import java.nio.file.Path;
import java.time.Duration;
import java.util.Optional;

public class AirbyteWorkflowImpl implements AirbyteWorkflow {
    public static final String AIRBYTE_WORKFLOW_QUEUE = "AIRBYTE_WORKFLOW_QUEUE";

    private static final RetryOptions RETRY_OPTIONS = RetryOptions.newBuilder()
            .setInitialInterval(Duration.ofSeconds(1))
//            .setMaximumInterval(Duration.ofSeconds(100))
//            .setBackoffCoefficient(2)
            .setMaximumAttempts(2)
            .build();

    private static final ActivityOptions OPTIONS = ActivityOptions.newBuilder()
            .setStartToCloseTimeout(Duration.ofMinutes(30))
//            .setScheduleToCloseTimeout(Duration.ofMinutes(30))
//            .setScheduleToStartTimeout(Duration.ofMinutes(30))
//            .setHeartbeatTimeout(Duration.ofMinutes(30))
            .setRetryOptions(RETRY_OPTIONS)
            .build();

    // activities should NOT BE STATIC - you get some really weird errors if you do
    private final GetSpecActivity getSpecActivity = Workflow.newActivityStub(GetSpecActivity.class, OPTIONS);
    private final DiscoverCatalogActivity discoverCatalogActivity = Workflow.newActivityStub(DiscoverCatalogActivity.class, OPTIONS);

    @Override
    public ConnectorSpecification getSpec(String dockerImage) {
        try {
            return getSpecActivity.getSpec(dockerImage);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public AirbyteCatalog discoverCatalog(String dockerImage, JsonNode connectionConfig) {
        try {
            return discoverCatalogActivity.discoverCatalog(dockerImage, connectionConfig);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}
