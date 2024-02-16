package io.airbyte.cdk.integrations.base.operation.executor;

import io.airbyte.cdk.integrations.base.operation.OperationExecutionException;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.micronaut.context.annotation.Requires;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Optional;
import java.util.function.Consumer;

import static io.airbyte.cdk.integrations.base.config.ConnectorConfigurationPropertySource.CONNECTOR_OPERATION;

@Singleton
@Named("readOperationExecutor")
@Requires(property = CONNECTOR_OPERATION, value = "read")
public class DefaultReadOperationExecutor implements OperationExecutor {

    private static final Logger LOGGER = LoggerFactory.getLogger(DefaultReadOperationExecutor.class);

    private final Optional<AutoCloseableIterator<AirbyteMessage>> messageIterator;
    private final Consumer<AirbyteMessage> outputRecordCollector;

    public DefaultReadOperationExecutor(final Optional<AutoCloseableIterator<AirbyteMessage>> messageIterator,
                                        @Named("outputRecordCollector") Consumer<AirbyteMessage> outputRecordCollector) {
        this.messageIterator = messageIterator;
        this.outputRecordCollector = outputRecordCollector;
    }

    @Override
    public AirbyteMessage execute() throws OperationExecutionException {
        if (messageIterator.isPresent()) {
            final AutoCloseableIterator<AirbyteMessage> iterator = messageIterator.get();
            try (iterator) {
                iterator.getAirbyteStream().ifPresent(s -> LOGGER.debug("Producing messages for stream {}...", s));
                iterator.forEachRemaining(outputRecordCollector);
                iterator.getAirbyteStream().ifPresent(s -> LOGGER.debug("Finished producing messages for stream {}..."));
            } catch (final Exception e) {
                throw new OperationExecutionException("Failed to read from connector.", e);
            }
        } else {
            throw new OperationExecutionException("Failed to read from connector.",
                    new IllegalArgumentException("Read operation supported, but message iterator does not exist."));
        }
        return null;
    }
}
