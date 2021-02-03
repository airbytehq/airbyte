package io.airbyte.workflows;

import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.StandardGetSpecOutput;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.workers.OutputAndStatus;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;

import java.nio.file.Path;
import java.util.Optional;

@WorkflowInterface
public interface AirbyteWorkflow {

    @WorkflowMethod
    ConnectorSpecification getSpec(String dockerImage) throws Exception;
}


