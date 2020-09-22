package io.airbyte.commons.io;

import org.slf4j.Logger;
import org.slf4j.event.Level;

import java.util.AbstractMap;
import java.util.Map;
import java.util.function.Consumer;
import java.util.function.Function;

public class LogTypeMapper implements Consumer<String> {
    private static final Map<Level, Function<Logger, Consumer<String>>> LEVEL_TO_CONSUMER_FACTORY = Map.ofEntries(
            new AbstractMap.SimpleEntry<>(Level.ERROR, logger -> logger::error),
            new AbstractMap.SimpleEntry<>(Level.WARN, logger -> logger::warn),
            new AbstractMap.SimpleEntry<>(Level.INFO, logger -> logger::info),
            new AbstractMap.SimpleEntry<>(Level.DEBUG, logger -> logger::debug),
            new AbstractMap.SimpleEntry<>(Level.TRACE, logger -> logger::trace)
    );

    private final Logger logger;
    private final Function<Logger, Consumer<String>> defaultLogConsumerFactory;

    public LogTypeMapper(Logger logger, Function<Logger, Consumer<String>> defaultLogConsumerFactory) {
        this.logger = logger;
        this.defaultLogConsumerFactory = defaultLogConsumerFactory;
    }

    @Override
    public void accept(String message) {
        getConsumer(message).accept(message);
    }

    private Consumer<String> getConsumer(String message) {
        for (Level level : LEVEL_TO_CONSUMER_FACTORY.keySet()) {
            if(message.startsWith(level.toString())) {
                return LEVEL_TO_CONSUMER_FACTORY.get(level).apply(logger);
            }
        }

        return defaultLogConsumerFactory.apply(logger);
    }
}
