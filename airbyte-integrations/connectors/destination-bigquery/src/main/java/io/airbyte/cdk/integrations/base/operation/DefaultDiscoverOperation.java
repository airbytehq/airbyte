package io.airbyte.cdk.integrations.base.operation;

import io.airbyte.cdk.integrations.base.operation.executor.OperationExecutor;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.micronaut.context.annotation.Requires;
import jakarta.inject.Named;
import jakarta.inject.Singleton;

import java.util.function.Consumer;

import static io.airbyte.cdk.integrations.base.config.ConnectorConfigurationPropertySource.CONNECTOR_OPERATION;

@Singleton
@Named("discoverOperation")
@Requires(property = CONNECTOR_OPERATION, value = "discover")
public class DefaultDiscoverOperation implements Operation {

    private final Consumer<AirbyteMessage> outputRecordCollector;
    private final OperationExecutor operationExecutor;

    public DefaultDiscoverOperation(@Named("discoverOperationExecutor") final OperationExecutor operationExecutor,
                                    @Named("outputRecordCollector") final Consumer<AirbyteMessage> outputRecordCollector) {
        this.outputRecordCollector = outputRecordCollector;
        this.operationExecutor = operationExecutor;
    }

    @Override
    public OperationType type() {
        return OperationType.DISCOVER;
    }

    @Override
    public void execute() throws OperationExecutionException {
        outputRecordCollector.accept(operationExecutor.execute());
    }
}
