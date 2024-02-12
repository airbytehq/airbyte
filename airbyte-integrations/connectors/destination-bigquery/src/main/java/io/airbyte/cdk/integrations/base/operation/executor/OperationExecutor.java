package io.airbyte.cdk.integrations.base.operation.executor;

import io.airbyte.cdk.integrations.base.operation.OperationExecutionException;
import io.airbyte.protocol.models.v0.AirbyteMessage;

public interface OperationExecutor {

    AirbyteMessage execute() throws OperationExecutionException;
}
