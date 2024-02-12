package io.airbyte.cdk.integrations.base.operation;

public interface Operation {

    OperationType type();

    void execute() throws OperationExecutionException;
}
