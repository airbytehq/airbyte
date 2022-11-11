/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import static io.airbyte.metrics.lib.ApmTraceConstants.WORKER_OPERATION_NAME;

import com.fasterxml.jackson.databind.JsonNode;
import datadog.trace.api.Trace;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.logging.MdcScope;
import io.airbyte.metrics.lib.MetricClientFactory;
import io.airbyte.metrics.lib.OssMetricsRegistry;
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
@SuppressWarnings("PMD.MoreThanOneLogger")
public class DefaultAirbyteStreamFactory implements AirbyteStreamFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultAirbyteStreamFactory.class);

  private final MdcScope.Builder containerLogMdcBuilder;
  private final AirbyteProtocolPredicate protocolValidator;
  protected final Logger logger;

  public DefaultAirbyteStreamFactory() {
    this(MdcScope.DEFAULT_BUILDER);
  }

  public DefaultAirbyteStreamFactory(final MdcScope.Builder containerLogMdcBuilder) {
    this(new AirbyteProtocolPredicate(), LOGGER, containerLogMdcBuilder);
  }

  DefaultAirbyteStreamFactory(final AirbyteProtocolPredicate protocolPredicate,
                              final Logger logger,
                              final MdcScope.Builder containerLogMdcBuilder) {
    protocolValidator = protocolPredicate;
    this.logger = logger;
    this.containerLogMdcBuilder = containerLogMdcBuilder;
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public Stream<AirbyteMessage> create(final BufferedReader bufferedReader) {
    final var metricClient = MetricClientFactory.getMetricClient();
    return bufferedReader
        .lines()
        .peek(str -> metricClient.distribution(OssMetricsRegistry.JSON_STRING_LENGTH, str.length()))
        .flatMap(this::parseJson)
        .filter(this::validate)
        .flatMap(this::toAirbyteMessage)
        .filter(this::filterLog);
  }

  protected Stream<JsonNode> parseJson(final String line) {
    final Optional<JsonNode> jsonLine = Jsons.tryDeserialize(line);
    if (jsonLine.isEmpty()) {
      // we log as info all the lines that are not valid json
      // some sources actually log their process on stdout, we
      // want to make sure this info is available in the logs.
      try (final var mdcScope = containerLogMdcBuilder.build()) {
        logger.info(line);
      }
    }
    return jsonLine.stream();
  }

  protected boolean validate(final JsonNode json) {
    final boolean res = protocolValidator.test(json);
    if (!res) {
      logger.error("Validation failed: {}", Jsons.serialize(json));
    }
    return res;
  }

  protected Stream<AirbyteMessage> toAirbyteMessage(final JsonNode json) {
    final Optional<AirbyteMessage> m = Jsons.tryObject(json, AirbyteMessage.class);
    if (m.isEmpty()) {
      logger.error("Deserialization failed: {}", Jsons.serialize(json));
    }
    return m.stream();
  }

  protected boolean filterLog(final AirbyteMessage message) {
    final boolean isLog = message.getType() == AirbyteMessage.Type.LOG;
    if (isLog) {
      try (final var mdcScope = containerLogMdcBuilder.build()) {
        internalLog(message.getLog());
      }
    }
    return !isLog;
  }

  protected void internalLog(final AirbyteLogMessage logMessage) {
    final String combinedMessage =
        logMessage.getMessage() + (logMessage.getStackTrace() != null ? (System.lineSeparator()
            + "Stack Trace: " + logMessage.getStackTrace()) : "");

    switch (logMessage.getLevel()) {
      case FATAL, ERROR -> logger.error(combinedMessage);
      case WARN -> logger.warn(combinedMessage);
      case DEBUG -> logger.debug(combinedMessage);
      case TRACE -> logger.trace(combinedMessage);
      default -> logger.info(combinedMessage);
    }
  }

}
