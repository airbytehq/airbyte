package io.airbyte.integrations.base;

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
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.core.LoggerContext;
import org.apache.logging.log4j.core.appender.OutputStreamAppender;
import org.apache.logging.log4j.core.config.Configuration;
import org.apache.logging.log4j.core.config.LoggerConfig;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.platform.commons.util.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
public class AirbyteLogMessageTemplateTest {
  private static final ByteArrayOutputStream outputContent = new ByteArrayOutputStream();
  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteLogMessageTemplateTest.class);
  private static OutputStreamAppender outputStreamAppender;
  private static LoggerConfig rootLoggerConfig;

  // LOG_LEVEL className(methodName):LineNumber logMessage
  private final String connectorLogMessageRegex = "^INFO [\\w+.]*.AirbyteLogMessageTemplateTest\\(testAirbyteLogMessageFormat\\):\\d+ hello$";
  private final Pattern pattern = Pattern.compile(connectorLogMessageRegex);

  @BeforeAll
  static void init() {
    // we are creating a log appender with the same output pattern
    // as the console appender defined in this project's log4j2.xml file.
    // this log appender stores logs in an output stream,
    // so that we can check after tests and validate formats.
    final LoggerContext loggerContext = (LoggerContext) LogManager.getContext(false);
    final Configuration configuration = loggerContext.getConfiguration();

    rootLoggerConfig = configuration.getLoggerConfig("");

    outputStreamAppender = OutputStreamAppender.createAppender(
        rootLoggerConfig.getAppenders().get("ConsoleJSONAppender").getLayout(),
        null, outputContent, "OutputStreamAppender", false, true);

    outputStreamAppender.start();
    rootLoggerConfig.addAppender(outputStreamAppender, Level.ALL, null);
  }

  @BeforeEach
  void setup() {
    outputContent.reset();
  }

  @AfterAll
  static void cleanUp() {
    outputStreamAppender.stop();
    rootLoggerConfig.removeAppender("OutputStreamAppender");
  }
  @Test
  public void testAirbyteLogMessageFormat() throws java.io.IOException {
    LOGGER.info("hello");
    outputContent.flush();

    final String logMessage = outputContent.toString();
    final AirbyteMessage airbyteMessage = validateLogIsAirbyteMessage(logMessage);
    validateAirbyteMessageIsLog(airbyteMessage);
  }

  private AirbyteMessage validateLogIsAirbyteMessage(final String logMessage) {
    final Optional<JsonNode> jsonLine = Jsons.tryDeserialize(logMessage);
    assertFalse(jsonLine.isEmpty());

    final Optional<AirbyteMessage> m = Jsons.tryObject(jsonLine.get(), AirbyteMessage.class);
    assertFalse(m.isEmpty());
    return m.get();
  }

  private AirbyteLogMessage validateAirbyteMessageIsLog(final AirbyteMessage airbyteMessage) {
    assertEquals(Type.LOG,airbyteMessage.getType());
    assertNotNull(airbyteMessage.getLog());

    final String logMessage  = airbyteMessage.getLog().getMessage();
    assertFalse(StringUtils.isBlank(logMessage));

    final Matcher matcher = pattern.matcher(logMessage);
    assertTrue(matcher.matches(), logMessage);

    return airbyteMessage.getLog();
  }
}
