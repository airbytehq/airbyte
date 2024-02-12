package io.airbyte.cdk.integrations.base.operation;

import io.airbyte.cdk.integrations.base.operation.executor.OperationExecutor;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import jakarta.inject.Named;
import jakarta.inject.Singleton;

import java.util.function.Consumer;

@Singleton
@Named("specOperation")
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
