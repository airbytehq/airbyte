package io.airbyte.cdk.integrations.base.operation;

import io.airbyte.cdk.integrations.base.operation.executor.OperationExecutor;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.micronaut.context.annotation.Requires;
import jakarta.inject.Named;
import jakarta.inject.Singleton;

import java.util.function.Consumer;

import static io.airbyte.cdk.integrations.base.config.ConnectorConfigurationPropertySource.CONNECTOR_OPERATION;

@Singleton
@Named("specOperation")
@Requires(property = CONNECTOR_OPERATION, value = "spec")
public class DefaultSpecOperation implements Operation{

    private final Consumer<AirbyteMessage> outputRecordCollector;
    private final OperationExecutor operationExecutor;

    public DefaultSpecOperation(@Named("specOperationExecutor") final OperationExecutor operationExecutor,
                                @Named("outputRecordCollector") final Consumer<AirbyteMessage> outputRecordCollector) {
        this.operationExecutor = operationExecutor;
        this.outputRecordCollector = outputRecordCollector;
    }

    @Override
    public OperationType type() {
        return OperationType.SPEC;
    }

    @Override
    public void execute() throws OperationExecutionException {
        outputRecordCollector.accept(operationExecutor.execute());
    }
}
