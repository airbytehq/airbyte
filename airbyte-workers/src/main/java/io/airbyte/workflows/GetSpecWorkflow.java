package io.airbyte.workflows;

import io.airbyte.protocol.models.ConnectorSpecification;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;

@WorkflowInterface
public interface GetSpecWorkflow {
    @WorkflowMethod
    ConnectorSpecification getSpec(String dockerImage);
}
