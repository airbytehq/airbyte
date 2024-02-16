package io.airbyte.cdk.integrations.base.operation;

import io.airbyte.cdk.integrations.base.operation.executor.OperationExecutor;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.micronaut.context.annotation.Requires;
import jakarta.inject.Named;
import jakarta.inject.Singleton;

import java.util.function.Consumer;

import static io.airbyte.cdk.integrations.base.config.ConnectorConfigurationPropertySource.CONNECTOR_OPERATION;

@Singleton
@Named("checkOperation")
@Requires(property = CONNECTOR_OPERATION, value = "check")
public class DefaultCheckOperation implements Operation {

    private final Consumer<AirbyteMessage> outputRecordCollector;
    private final OperationExecutor operationExecutor;

    public DefaultCheckOperation(@Named("checkOperationExecutor") final OperationExecutor operationExecutor,
                                 @Named("outputRecordCollector") final Consumer<AirbyteMessage> outputRecordCollector) {
        this.operationExecutor = operationExecutor;
        this.outputRecordCollector = outputRecordCollector;
    }

    @Override
    public OperationType type() {
        return OperationType.CHECK;
    }

    @Override
    public void execute() throws OperationExecutionException {
        try {
            this.outputRecordCollector.accept(operationExecutor.execute());
        } catch (final Exception e) {
            this.outputRecordCollector.accept((new AirbyteMessage())
                    .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                    .withConnectionStatus(new AirbyteConnectionStatus()
                            .withStatus(AirbyteConnectionStatus.Status.FAILED)
                            .withMessage(e.getMessage())));
        }
    }
}
