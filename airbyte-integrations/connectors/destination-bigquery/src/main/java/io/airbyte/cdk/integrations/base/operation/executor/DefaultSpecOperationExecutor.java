package io.airbyte.cdk.integrations.base.operation.executor;

import io.airbyte.cdk.integrations.base.operation.OperationExecutionException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.micronaut.context.annotation.Requires;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.io.IOException;

import static io.airbyte.cdk.integrations.base.config.ConnectorConfigurationPropertySource.CONNECTOR_OPERATION;

@Singleton
@Named("specOperationExecutor")
@Requires(property = CONNECTOR_OPERATION, value = "spec")
public class DefaultSpecOperationExecutor implements OperationExecutor {

    @Override
    public AirbyteMessage execute() throws OperationExecutionException {
        try {
            final String resourceString = MoreResources.readResource("spec.json");
            final ConnectorSpecification connectorSpecification = Jsons.deserialize(resourceString, ConnectorSpecification.class);
            return new AirbyteMessage().withType(AirbyteMessage.Type.SPEC).withSpec(connectorSpecification);
        } catch (final IOException e) {
            throw new OperationExecutionException("Failed to retrieve specification from connector.", e);
        }
    }
}
