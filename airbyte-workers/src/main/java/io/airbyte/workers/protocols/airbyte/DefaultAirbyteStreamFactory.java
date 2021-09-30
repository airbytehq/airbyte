/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.protocols.airbyte;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteLogMessage;
import io.airbyte.protocol.models.AirbyteMessage;
import java.io.BufferedReader;
import java.util.Optional;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Creates a stream from an input stream. The produced stream attempts to parse each line of the
 * InputStream into a AirbyteMessage. If the line cannot be parsed into a AirbyteMessage it is
 * dropped. Each record MUST be new line separated.
 *
 * <p>
 * If a line starts with a AirbyteMessage and then has other characters after it, that
 * AirbyteMessage will still be parsed. If there are multiple AirbyteMessage records on the same
 * line, only the first will be parsed.
 */
public class DefaultAirbyteStreamFactory implements AirbyteStreamFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultAirbyteStreamFactory.class);

  private final AirbyteProtocolPredicate protocolValidator;
  private final Logger logger;

  public DefaultAirbyteStreamFactory() {
    this(new AirbyteProtocolPredicate(), LOGGER);
  }

  DefaultAirbyteStreamFactory(final AirbyteProtocolPredicate protocolPredicate, final Logger logger) {
    protocolValidator = protocolPredicate;
    this.logger = logger;
  }

  @Override
  public Stream<AirbyteMessage> create(BufferedReader bufferedReader) {
    return bufferedReader
        .lines()
        .map(s -> {
          Optional<JsonNode> j = Jsons.tryDeserialize(s);
          if (j.isEmpty()) {
            // we log as info all the lines that are not valid json
            // some sources actually log their process on stdout, we
            // want to make sure this info is available in the logs.
            logger.info(s);
          }
          return j;
        })
        .filter(Optional::isPresent)
        .map(Optional::get)
        // filter invalid messages
        .filter(j -> {
          boolean res = protocolValidator.test(j);
          if (!res) {
            logger.error("Validation failed: {}", Jsons.serialize(j));
          }
          return res;
        })
        .map(j -> {
          Optional<AirbyteMessage> m = Jsons.tryObject(j, AirbyteMessage.class);
          if (m.isEmpty()) {
            logger.error("Deserialization failed: {}", Jsons.serialize(j));
          }
          return m;
        })
        .filter(Optional::isPresent)
        .map(Optional::get)
        // filter logs
        .filter(m -> {
          boolean isLog = m.getType() == AirbyteMessage.Type.LOG;
          if (isLog) {
            internalLog(m.getLog());
          }
          return !isLog;
        });
  }

  private void internalLog(AirbyteLogMessage logMessage) {
    switch (logMessage.getLevel()) {
      case FATAL, ERROR -> logger.error(logMessage.getMessage());
      case WARN -> logger.warn(logMessage.getMessage());
      case INFO -> logger.info(logMessage.getMessage());
      case DEBUG -> logger.debug(logMessage.getMessage());
      case TRACE -> logger.trace(logMessage.getMessage());
    }
  }

}
