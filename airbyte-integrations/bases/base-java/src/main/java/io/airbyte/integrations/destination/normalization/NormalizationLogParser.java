/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.normalization;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.normalization.SentryExceptionHelper.ErrorMapKeys;
import io.airbyte.protocol.models.AirbyteErrorTraceMessage;
import io.airbyte.protocol.models.AirbyteErrorTraceMessage.FailureType;
import io.airbyte.protocol.models.AirbyteLogMessage;
import io.airbyte.protocol.models.AirbyteLogMessage.Level;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteTraceMessage;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Stream;
import org.apache.logging.log4j.util.Strings;

/**
 * A simple wrapper for base-normalization logs. Reads messages off of stdin and sticks them into
 * appropriate AirbyteMessages (log or trace), then dumps those messages to stdout
 * <p>
 * does mostly the same thing as
 * {@link io.airbyte.workers.normalization.NormalizationAirbyteStreamFactory}. That class is not
 * actively developed, and will be deleted after all destinations run normalization in-connector.
 * <p>
 * Aggregates all error logs and emits them as a single trace message at the end. If the underlying
 * process emits any trace messages, they are passed through immediately.
 */
public class NormalizationLogParser {

  private final List<String> dbtErrors = new ArrayList<>();

  public Stream<AirbyteMessage> create(final BufferedReader bufferedReader) {
    return bufferedReader.lines().flatMap(this::toMessages);
  }

  public List<String> getDbtErrors() {
    return dbtErrors;
  }

  @VisibleForTesting
  Stream<AirbyteMessage> toMessages(final String line) {
    if (Strings.isEmpty(line)) {
      return Stream.of(logMessage(Level.INFO, ""));
    }
    final Optional<JsonNode> json = Jsons.tryDeserialize(line);
    if (json.isPresent()) {
      return jsonToMessage(json.get());
    } else {
      return nonJsonLineToMessage(line);
    }
  }

  /**
   * Wrap the line in an AirbyteLogMessage, and do very naive dbt error log detection.
   * <p>
   * This is needed for dbt < 1.0.0, which don't support json-format logs.
   */
  private Stream<AirbyteMessage> nonJsonLineToMessage(final String line) {
    // Super hacky thing to try and detect error lines
    if (line.contains("[error]")) {
      dbtErrors.add(line);
    }
    return Stream.of(logMessage(Level.INFO, line));
  }

  /**
   * There are two cases here: Either the json is already an AirbyteMessage (and we should just emit
   * it without change), or it's dbt json log, and we need to do some extra work to convert it to a
   * log message + aggregate error logs.
   */
  private Stream<AirbyteMessage> jsonToMessage(final JsonNode jsonLine) {
    final Optional<AirbyteMessage> message = Jsons.tryObject(jsonLine, AirbyteMessage.class);
    if (message.isPresent()) {
      // This line is already an AirbyteMessage; we can just return it directly
      // (these messages come from the transform_config / transform_catalog scripts)
      return message.stream();
    } else {
      /*
       * This line is a JSON-format dbt log. We need to extract the message and wrap it in a logmessage
       * And if it's an error, we also need to collect it into dbtErrors. Example log message, formatted
       * for readability: { "code": "A001", "data": { "v": "=1.0.9" }, "invocation_id":
       * "3f9a0b9f-9623-4c25-8708-1f6ae851e738", "level": "info", "log_version": 1, "msg":
       * "Running with dbt=1.0.9", "node_info": {}, "pid": 65, "thread_name": "MainThread", "ts":
       * "2023-04-12T21:03:23.079315Z", "type": "log_line" }
       */
      final String logLevel = (jsonLine.hasNonNull("level")) ? jsonLine.get("level").asText() : "";
      String logMsg = jsonLine.hasNonNull("msg") ? jsonLine.get("msg").asText() : "";
      Level level;
      switch (logLevel) {
        case "debug" -> level = Level.DEBUG;
        case "info" -> level = Level.INFO;
        case "warn" -> level = Level.WARN;
        case "error" -> {
          // This is also not _amazing_, but we make the assumption that all error logs should be emitted in
          // the trace message
          // In practice, this seems to be a valid assumption.
          level = Level.ERROR;
          dbtErrors.add(logMsg);
        }
        default -> {
          level = Level.INFO;
          logMsg = jsonLine.toPrettyString();
        }
      }
      return Stream.of(logMessage(level, logMsg));
    }
  }

  private static AirbyteMessage logMessage(Level level, String message) {
    return new AirbyteMessage()
        .withType(Type.LOG)
        .withLog(new AirbyteLogMessage()
            .withLevel(level)
            .withMessage(message));
  }

  public static void main(String[] args) {
    final NormalizationLogParser normalizationLogParser = new NormalizationLogParser();
    final Stream<AirbyteMessage> airbyteMessageStream =
        normalizationLogParser.create(new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8)));
    airbyteMessageStream.forEachOrdered(message -> System.out.println(Jsons.serialize(message)));

    final List<String> errors = normalizationLogParser.getDbtErrors();
    final String dbtErrorStack = String.join("\n", errors);
    if (!"".equals(dbtErrorStack)) {
      final Map<ErrorMapKeys, String> errorMap = SentryExceptionHelper.getUsefulErrorMessageAndTypeFromDbtError(dbtErrorStack);
      String internalMessage = errorMap.get(ErrorMapKeys.ERROR_MAP_MESSAGE_KEY);
      AirbyteMessage traceMessage = new AirbyteMessage()
          .withType(Type.TRACE)
          .withTrace(new AirbyteTraceMessage()
              .withType(AirbyteTraceMessage.Type.ERROR)
              .withEmittedAt((double) System.currentTimeMillis())
              .withError(new AirbyteErrorTraceMessage()
                  .withFailureType(FailureType.SYSTEM_ERROR)
                  .withMessage("Normalization failed during the dbt run. This may indicate a problem with the data itself.")
                  .withStackTrace("AirbyteDbtError: \n" + dbtErrorStack)
                  .withInternalMessage(internalMessage)));
      System.out.println(Jsons.serialize(traceMessage));
    }
  }

}
