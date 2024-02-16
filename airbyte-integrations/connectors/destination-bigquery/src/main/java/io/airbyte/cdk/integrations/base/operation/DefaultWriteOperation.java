package io.airbyte.cdk.integrations.base.operation;

import io.airbyte.cdk.integrations.base.operation.executor.OperationExecutor;
import io.airbyte.cdk.integrations.base.util.ShutdownUtils;
import io.micronaut.context.annotation.Requires;
import jakarta.inject.Named;
import jakarta.inject.Singleton;

import java.util.concurrent.TimeUnit;

import static io.airbyte.cdk.integrations.base.config.ConnectorConfigurationPropertySource.CONNECTOR_OPERATION;

@Singleton
@Named("writeOperation")
@Requires(property = CONNECTOR_OPERATION, value = "write")
public class DefaultWriteOperation implements Operation {

    private final OperationExecutor operationExecutor;
    private final ShutdownUtils shutdownUtils;

    public DefaultWriteOperation(
            @Named("writeOperationExecutor") final OperationExecutor operationExecutor,
            final ShutdownUtils shutdownUtils) {
        this.operationExecutor = operationExecutor;
        this.shutdownUtils = shutdownUtils;
    }

    @Override
    public OperationType type() {
        return OperationType.WRITE;
    }

    @Override
    public void execute() throws OperationExecutionException {
        try {
            operationExecutor.execute();
        } finally {
            shutdownUtils.stopOrphanedThreads(
                ShutdownUtils.EXIT_HOOK,
                ShutdownUtils.INTERRUPT_THREAD_DELAY_MINUTES,
                TimeUnit.MINUTES,
                ShutdownUtils.EXIT_THREAD_DELAY_MINUTES,
                TimeUnit.MINUTES);
        }
    }
}
