/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import static io.airbyte.metrics.lib.ApmTraceConstants.WORKER_OPERATION_NAME;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import datadog.trace.api.Trace;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.logging.MdcScope;
import io.airbyte.metrics.lib.MetricClientFactory;
import io.airbyte.metrics.lib.OssMetricsRegistry;
import io.airbyte.protocol.models.AirbyteLogMessage;
import io.airbyte.protocol.models.AirbyteMessage;
import java.io.BufferedReader;
import java.lang.reflect.InvocationTargetException;
import java.nio.charset.StandardCharsets;
import java.text.CharacterIterator;
import java.text.StringCharacterIterator;
import java.util.Optional;
import java.util.stream.Stream;
import org.joda.time.DateTime;
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
  private final double MAX_SIZE_RATIO = 0.8;

  private final MdcScope.Builder containerLogMdcBuilder;
  private final AirbyteProtocolPredicate protocolValidator;
  protected final Logger logger;
  private final long maxMemory;
  private final Optional<Class<? extends RuntimeException>> exceptionClass;

  public DefaultAirbyteStreamFactory() {
    this(MdcScope.DEFAULT_BUILDER);
  }

  public DefaultAirbyteStreamFactory(final MdcScope.Builder containerLogMdcBuilder) {
    this(new AirbyteProtocolPredicate(), LOGGER, containerLogMdcBuilder, Optional.empty());
  }

  /**
   * Create a default airbyte stream, if a `messageSizeExceptionClass` is not empty, the message size
   * will be checked and if it more than the available memory * MAX_SIZE_RATIO the sync will be failed
   * by throwing the exception provided. The exception must have a constructor that accept a string.
   */
  DefaultAirbyteStreamFactory(final AirbyteProtocolPredicate protocolPredicate,
                              final Logger logger,
                              final MdcScope.Builder containerLogMdcBuilder,
                              final Optional<Class<? extends RuntimeException>> messageSizeExceptionClass) {
    protocolValidator = protocolPredicate;
    this.logger = logger;
    this.containerLogMdcBuilder = containerLogMdcBuilder;
    this.exceptionClass = messageSizeExceptionClass;
    this.maxMemory = Runtime.getRuntime().maxMemory();
  }

  @VisibleForTesting
  DefaultAirbyteStreamFactory(final AirbyteProtocolPredicate protocolPredicate,
                              final Logger logger,
                              final MdcScope.Builder containerLogMdcBuilder,
                              final Optional<Class<? extends RuntimeException>> messageSizeExceptionClass,
                              final long maxMemory) {
    protocolValidator = protocolPredicate;
    this.logger = logger;
    this.containerLogMdcBuilder = containerLogMdcBuilder;
    this.exceptionClass = messageSizeExceptionClass;
    this.maxMemory = maxMemory;
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public Stream<AirbyteMessage> create(final BufferedReader bufferedReader) {
    final var metricClient = MetricClientFactory.getMetricClient();
    return bufferedReader
        .lines()
        .peek(str -> metricClient.distribution(OssMetricsRegistry.JSON_STRING_LENGTH, str.getBytes(StandardCharsets.UTF_8).length))
        .peek(str -> {
          if (exceptionClass.isPresent()) {
            final long messageSize = str.getBytes(StandardCharsets.UTF_8).length;
            if (messageSize > maxMemory * MAX_SIZE_RATIO) {
              try {
                final String errorMessage = String.format(
                    "Airbyte has received a message at %s UTC which is larger than %s (size: %s). The sync has been failed to prevent running out of memory.",
                    DateTime.now(),
                    humanReadableByteCountSI(maxMemory),
                    humanReadableByteCountSI(messageSize));
                throw exceptionClass.get().getConstructor(String.class).newInstance(errorMessage);
              } catch (final InstantiationException | IllegalAccessException | InvocationTargetException | NoSuchMethodException e) {
                throw new RuntimeException(e);
              }
            }
          }
        })
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

  // Human-readable byte size from
  // https://stackoverflow.com/questions/3758606/how-can-i-convert-byte-size-into-a-human-readable-format-in-java
  @SuppressWarnings("PMD.AvoidReassigningParameters")
  private String humanReadableByteCountSI(long bytes) {
    if (-1000 < bytes && bytes < 1000) {
      return bytes + " B";
    }
    final CharacterIterator ci = new StringCharacterIterator("kMGTPE");
    while (bytes <= -999_950 || bytes >= 999_950) {
      bytes /= 1000;
      ci.next();
    }
    return String.format("%.1f %cB", bytes / 1000.0, ci.current());
  }

}
