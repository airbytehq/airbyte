package io.airbyte.cdk.integrations.base.operation.executor;

import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.config.AirbyteConfiguredCatalog;
import io.airbyte.cdk.integrations.base.operation.OperationExecutionException;
import io.airbyte.integrations.destination.bigquery.consumer.SerializedAirbyteMessageConsumerFactory;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.micronaut.context.annotation.Requires;
import jakarta.inject.Named;
import jakarta.inject.Singleton;

import java.io.BufferedInputStream;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.Optional;

import static io.airbyte.cdk.integrations.base.config.ConnectorConfigurationPropertySource.CONNECTOR_OPERATION;

@Singleton
@Named("writeOperationExecutor")
@Requires(property = CONNECTOR_OPERATION, value = "write")
public class DefaultWriteOperationExecutor implements OperationExecutor {

    private final AirbyteConfiguredCatalog catalog;
    private final Optional<SerializedAirbyteMessageConsumerFactory> messageConsumerFactory;

    public DefaultWriteOperationExecutor(final AirbyteConfiguredCatalog catalog,
                                 final Optional<SerializedAirbyteMessageConsumerFactory> messageConsumerFactory) {
        this.catalog = catalog;
        this.messageConsumerFactory = messageConsumerFactory;
    }

    @Override
    public AirbyteMessage execute() throws OperationExecutionException {
        if (messageConsumerFactory.isPresent()) {
            SerializedAirbyteMessageConsumer consumer = null;
            try {
                consumer = messageConsumerFactory.get().createMessageConsumer(catalog.getConfiguredCatalog());
                try (final BufferedInputStream bis = new BufferedInputStream(System.in);
                     final ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
                    consumeWriteStream(consumer, bis, baos);
                }
            } catch (final Exception e) {
                throw new OperationExecutionException("Failed to write output from connector.", e);
            } finally {
                if (consumer != null) {
                    try {
                        consumer.close();
                    } catch (final Exception e) {
                    }
                }
            }
        } else {
            throw new OperationExecutionException("Failed to write output from connector.",
                    new IllegalArgumentException("Writer operation supported, but output consumer does not exist."));
        }

        return null;
    }

    public void consumeWriteStream(final SerializedAirbyteMessageConsumer consumer,
                                   final BufferedInputStream bis,
                                   final ByteArrayOutputStream baos)
            throws Exception {
        consumer.start();

        final byte[] buffer = new byte[8192]; // 8K buffer
        int bytesRead;
        boolean lastWasNewLine = false;

        while ((bytesRead = bis.read(buffer)) != -1) {
            for (int i = 0; i < bytesRead; i++) {
                final byte b = buffer[i];
                if (b == '\n' || b == '\r') {
                    if (!lastWasNewLine && baos.size() > 0) {
                        consumer.accept(baos.toString(StandardCharsets.UTF_8), baos.size());
                        baos.reset();
                    }
                    lastWasNewLine = true;
                } else {
                    baos.write(b);
                    lastWasNewLine = false;
                }
            }
        }

        // Handle last line if there's one
        if (baos.size() > 0) {
            consumer.accept(baos.toString(StandardCharsets.UTF_8), baos.size());
        }
    }
}
