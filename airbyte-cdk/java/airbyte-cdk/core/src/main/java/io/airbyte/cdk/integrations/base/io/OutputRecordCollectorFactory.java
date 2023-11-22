package io.airbyte.cdk.integrations.base.io;

import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;

public class OutputRecordCollectorFactory {

    public static final int CONNECTION_RETRY_BACKOFF_MS = Long.valueOf(TimeUnit.SECONDS.toMillis(1)).intValue();

    public static final String PLATFORM_SERVER_ENABLED = "PLATFORM_SERVER_ENABLED";
    public static final String PLATFORM_SERVER_HOST = "PLATFORM_SERVER_HOST";
    public static final String PLATFORM_SERVER_PORT = "PLATFORM_SERVER_PORT";

    private static final Logger LOGGER = LoggerFactory.getLogger(OutputRecordCollectorFactory.class);

    private static Consumer<?> INSTANCE = null;

    public static <T> Consumer<T> getOutputRecordCollector() {
        if (INSTANCE == null) {
            INSTANCE = createOutputRecordCollector();
        }

        return (Consumer<T>)INSTANCE;
    }

    private static <T> Consumer<T> createOutputRecordCollector() {
        final boolean socketOutputEnabled = Boolean.TRUE.equals(Boolean.valueOf(System.getenv(PLATFORM_SERVER_ENABLED)));
        if (socketOutputEnabled) {
            LOGGER.info("Using socket-based output record collector.");
            final SocketOutputRecordCollector<T> socketOutputRecordCollector =
                    new SocketOutputRecordCollector<>(System.getenv(PLATFORM_SERVER_HOST),
                            Integer.parseInt(System.getenv(PLATFORM_SERVER_PORT)), CONNECTION_RETRY_BACKOFF_MS);
            socketOutputRecordCollector.connect();
            return socketOutputRecordCollector;
        } else {
            LOGGER.info("Using default (stdout) output record collector.");
            return System.out::println;
        }
    }
}
