package io.airbyte.commons.io;

import org.junit.jupiter.api.Test;
import org.slf4j.Logger;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;


class LogTypeMapperTest {
    @Test
    public void testDefaultLogger() {
        Logger logger = mock(Logger.class);
        String logString = "message not prefixed with a log level such as INFO";
        LogTypeMapper mapper = new LogTypeMapper(logger, l -> l::debug);

        mapper.accept(logString);
        verify(logger).debug(logString);
    }

    @Test
    public void testOverriddenLogger() {
        Logger logger = mock(Logger.class);
        String logString = "INFO message prefixed with a log level";
        LogTypeMapper mapper = new LogTypeMapper(logger, l -> l::debug);

        mapper.accept(logString);
        verify(logger).info(logString);
    }

}