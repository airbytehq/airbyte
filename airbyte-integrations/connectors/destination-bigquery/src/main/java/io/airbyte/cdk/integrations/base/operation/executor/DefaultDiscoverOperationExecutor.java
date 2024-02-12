package io.airbyte.cdk.integrations.base.operation.executor;

import io.airbyte.cdk.integrations.base.operation.OperationExecutionException;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import jakarta.inject.Named;
import jakarta.inject.Singleton;

@Singleton
@Named("discoverOperationExecutor")
public class DefaultDiscoverOperationExecutor implements OperationExecutor {
    @Override
    public AirbyteMessage execute() throws OperationExecutionException {
        return new AirbyteMessage().withType(AirbyteMessage.Type.CATALOG).withCatalog(new AirbyteCatalog());
    }
}
