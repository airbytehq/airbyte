package io.airbyte.cdk.integrations.base.operation.executor;

import io.airbyte.cdk.integrations.base.operation.OperationExecutionException;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.micronaut.context.annotation.Requires;
import jakarta.inject.Named;
import jakarta.inject.Singleton;

import static io.airbyte.cdk.integrations.base.config.ConnectorConfigurationPropertySource.CONNECTOR_OPERATION;

@Singleton
@Named("discoverOperationExecutor")
@Requires(property = CONNECTOR_OPERATION, value = "discover")
public class DefaultDiscoverOperationExecutor implements OperationExecutor {
    @Override
    public AirbyteMessage execute() throws OperationExecutionException {
        return new AirbyteMessage().withType(AirbyteMessage.Type.CATALOG).withCatalog(new AirbyteCatalog());
    }
}
