package io.airbyte.workflows;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;

@WorkflowInterface
public interface DiscoverCatalogWorkflow {
    @WorkflowMethod
    AirbyteCatalog discoverCatalog(String dockerImage, JsonNode connectionConfig);
}
