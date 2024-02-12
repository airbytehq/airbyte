package io.airbyte.cdk.integrations.base.operation.executor;

import io.airbyte.cdk.integrations.base.operation.OperationExecutionException;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import jakarta.inject.Named;
import jakarta.inject.Singleton;

@Singleton
@Named("checkOperationExecutor")
public class DefaultCheckOperationExecutor implements OperationExecutor {
    @Override
    public AirbyteMessage execute() throws OperationExecutionException {
        return new AirbyteMessage()
                .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                .withConnectionStatus(new AirbyteConnectionStatus()
                        .withStatus(AirbyteConnectionStatus.Status.SUCCEEDED));
    }
}
