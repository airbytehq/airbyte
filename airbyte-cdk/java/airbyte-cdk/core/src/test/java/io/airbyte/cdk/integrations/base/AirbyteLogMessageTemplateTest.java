/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.base;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteLogMessage;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.core.LoggerContext;
import org.apache.logging.log4j.core.appender.OutputStreamAppender;
import org.apache.logging.log4j.core.config.Configuration;
import org.apache.logging.log4j.core.config.Configurator;
import org.apache.logging.log4j.core.config.LoggerConfig;
import org.apache.logging.log4j.spi.ExtendedLogger;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.junit.platform.commons.util.StringUtils;

public class AirbyteLogMessageTemplateTest {

  public static final String OUTPUT_STREAM_APPENDER = "OutputStreamAppender";
  public static final String CONSOLE_JSON_APPENDER = "ConsoleJSONAppender";
  private LoggerContext loggerContext;
  private LoggerConfig rootLoggerConfig;
  private ExtendedLogger logger;
  private OutputStreamAppender outputStreamAppender;
  private ByteArrayOutputStream outputContent;

  void getLogger() {
    // We are creating a log appender with the same output pattern
    // as the console json appender defined in this project's log4j2.xml file.
    // We then attach this log appender with the LOGGER instance so that we can validate the logs
    // produced by code and assert that it matches the expected format.
    loggerContext = Configurator.initialize(null, "log4j2.xml");

    final Configuration configuration = loggerContext.getConfiguration();
    rootLoggerConfig = configuration.getLoggerConfig("");

    outputContent = new ByteArrayOutputStream();
    outputStreamAppender = OutputStreamAppender.createAppender(
        rootLoggerConfig.getAppenders().get(CONSOLE_JSON_APPENDER).getLayout(),
        null, outputContent, OUTPUT_STREAM_APPENDER, false, true);
    outputStreamAppender.start();

    rootLoggerConfig.addAppender(outputStreamAppender, Level.ALL, null);
    logger = loggerContext.getLogger(AirbyteLogMessageTemplateTest.class);
  }

  @AfterEach
  void closeLogger() {
    outputStreamAppender.stop();
    rootLoggerConfig.removeAppender(OUTPUT_STREAM_APPENDER);
    loggerContext.close();
  }

  @Test
  public void testAirbyteLogMessageFormat() throws java.io.IOException {
    getLogger();
    logger.info("hello");

    outputContent.flush();
    final String logMessage = outputContent.toString(StandardCharsets.UTF_8);
    final AirbyteMessage airbyteMessage = validateLogIsAirbyteMessage(logMessage);
    final AirbyteLogMessage airbyteLogMessage = validateAirbyteMessageIsLog(airbyteMessage);

    final String connectorLogMessage = airbyteLogMessage.getMessage();
    // validate that the message inside AirbyteLogMessage matches the pattern.
    // pattern to check for is: LOG_LEVEL className(methodName):LineNumber logMessage
    final String connectorLogMessageRegex =
        String.format("^INFO %s [\\w+.]*.AirbyteLogMessageTemplateTest\\(testAirbyteLogMessageFormat\\):\\d+ hello$",
            Pattern.compile(Thread.currentThread().getName()));
    final Pattern pattern = Pattern.compile(connectorLogMessageRegex);

    final Matcher matcher = pattern.matcher(connectorLogMessage);
    assertTrue(matcher.matches(), connectorLogMessage);
  }

  private AirbyteMessage validateLogIsAirbyteMessage(final String logMessage) {
    final Optional<JsonNode> jsonLine = Jsons.tryDeserialize(logMessage);
    assertFalse(jsonLine.isEmpty());

    final Optional<AirbyteMessage> m = Jsons.tryObject(jsonLine.get(), AirbyteMessage.class);
    assertFalse(m.isEmpty());
    return m.get();
  }

  private AirbyteLogMessage validateAirbyteMessageIsLog(final AirbyteMessage airbyteMessage) {
    assertEquals(Type.LOG, airbyteMessage.getType());
    assertNotNull(airbyteMessage.getLog());
    assertFalse(StringUtils.isBlank(airbyteMessage.getLog().getMessage()));
    return airbyteMessage.getLog();
  }

  @ParameterizedTest
  @ValueSource(ints = {2, 100, 9000})
  public void testAirbyteLogMessageLength(int stringRepetitions) throws java.io.IOException {
    getLogger();
    final StringBuilder sb = new StringBuilder();
    for (int i = 0; i < stringRepetitions; i++) {
      sb.append("abcd");
    }
    logger.info(sb.toString(), new RuntimeException("aaaaa bbbbbb ccccccc dddddd"));
    outputContent.flush();
    final String logMessage = outputContent.toString(StandardCharsets.UTF_8);

    final AirbyteMessage airbyteMessage = validateLogIsAirbyteMessage(logMessage);
    final AirbyteLogMessage airbyteLogMessage = validateAirbyteMessageIsLog(airbyteMessage);
    final String connectorLogMessage = airbyteLogMessage.getMessage();

    // #30781 - message length is capped at 16,000 charcters.
    int j = connectorLogMessage.length();
    assertFalse(connectorLogMessage.length() > 16_001);
    assertTrue(logMessage.length() < 32768);
  }

}
