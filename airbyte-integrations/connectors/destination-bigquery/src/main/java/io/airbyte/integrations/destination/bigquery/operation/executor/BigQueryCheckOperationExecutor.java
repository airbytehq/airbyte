package io.airbyte.integrations.destination.bigquery.operation.executor;

import io.airbyte.cdk.integrations.base.operation.OperationExecutionException;
import io.airbyte.cdk.integrations.base.operation.executor.OperationExecutor;
import io.airbyte.integrations.destination.bigquery.service.CheckService;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.micronaut.context.annotation.Primary;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.function.Consumer;

@Singleton
@Primary
@Named("checkOperationExecutor")
public class BigQueryCheckOperationExecutor implements OperationExecutor {

    private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryCheckOperationExecutor.class);

    private final CheckService checkService;
    private final Consumer<AirbyteMessage> outputRecordCollector;

    public BigQueryCheckOperationExecutor(final CheckService checkService,
                                          @Named("outputRecordCollector") final Consumer<AirbyteMessage> outputRecordCollector) {
        this.checkService = checkService;
        this.outputRecordCollector = outputRecordCollector;
    }

    @Override
    public AirbyteMessage execute() throws OperationExecutionException {
        LOGGER.info("Checking connection to BigQuery...");
        return new AirbyteMessage()
                .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                .withConnectionStatus(checkService.check());
    }
}
