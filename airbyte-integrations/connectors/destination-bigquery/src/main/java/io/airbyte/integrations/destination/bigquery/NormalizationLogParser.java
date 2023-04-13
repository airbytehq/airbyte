package io.airbyte.integrations.destination.bigquery;

/*
 * This class should probably live in a higher library
 * just putting it here for now for convenience
 * we'll need to extract it anyway when we start doing other destinations
 */

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.JsonNodeType;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteErrorTraceMessage;
import io.airbyte.protocol.models.AirbyteErrorTraceMessage.FailureType;
import io.airbyte.protocol.models.AirbyteLogMessage;
import io.airbyte.protocol.models.AirbyteLogMessage.Level;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteTraceMessage;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.Optional;
import java.util.stream.Stream;
import org.apache.logging.log4j.util.Strings;

/**
 * A simple wrapper for base-normalization logs. Reads messages off of stdin and sticks them into appropriate AirbyteMessages (log or trace), then
 * dumps those messages to stdout
 * <p>
 * does mostly the same thing as {@link io.airbyte.workers.normalization.NormalizationAirbyteStreamFactory}. That class is not actively developed,
 * and will be deleted after all destinations run normalization in-connector.
 */
public class NormalizationLogParser {

  public Stream<AirbyteMessage> create(final BufferedReader bufferedReader) {
    return bufferedReader
        .lines()
        .flatMap(this::wrap);
  }

  private Stream<AirbyteMessage> wrap(final String line) {
    if (Strings.isEmpty(line)) {
      return Stream.of(new AirbyteMessage()
          .withType(Type.LOG)
          .withLog(new AirbyteLogMessage().withLevel(Level.INFO).withMessage(line)));
    }

    final Optional<JsonNode> json = Jsons.tryDeserialize(line);
    if (json.isEmpty()) {
      final AirbyteMessage logMessage = new AirbyteMessage()
          .withType(Type.LOG)
          .withLog(new AirbyteLogMessage().withLevel(Level.INFO).withMessage(line));
      if (line.contains("[error]")) {
        AirbyteMessage traceMessage = new AirbyteMessage()
            .withType(Type.TRACE)
            .withTrace(new AirbyteTraceMessage()
                .withType(AirbyteTraceMessage.Type.ERROR)
                .withEmittedAt((double) System.currentTimeMillis())
                .withError(new AirbyteErrorTraceMessage()
                    .withFailureType(FailureType.SYSTEM_ERROR)
                    .withMessage("Normalization failed during the dbt run. This may indicate a problem with the data itself.")
                    .withStackTrace("AirbyteDbtError: \n" + line)));
        return Stream.of(logMessage, traceMessage);
      } else {
        return Stream.of(logMessage);
      }
    } else {
      final Optional<AirbyteMessage> message = Jsons.tryObject(json.get(), AirbyteMessage.class);
      if (message.isEmpty()) {
        JsonNode jsonLine = json.get();
        final String logLevel = (jsonLine.getNodeType() == JsonNodeType.NULL || jsonLine.get("level").isNull())
                                ? ""
                                : jsonLine.get("level").asText();
        String logMsg = jsonLine.get("msg").isNull() ? "" : jsonLine.get("msg").asText();
        Level level;
        Optional<AirbyteMessage> traceMessage = Optional.empty();
        switch (logLevel) {
          case "debug" -> level = Level.DEBUG;
          case "info" -> level = Level.INFO;
          case "warn" -> level = Level.WARN;
          case "error" -> {
            level = Level.ERROR;
            // TODO is this correct?
            traceMessage = Optional.of(new AirbyteMessage()
                .withType(Type.TRACE)
                .withTrace(new AirbyteTraceMessage()
                    .withType(AirbyteTraceMessage.Type.ERROR)
                    .withEmittedAt((double) System.currentTimeMillis())
                    .withError(new AirbyteErrorTraceMessage()
                        .withFailureType(FailureType.SYSTEM_ERROR)
                        .withMessage("Normalization failed during the dbt run. This may indicate a problem with the data itself.")
                        .withStackTrace("AirbyteDbtError: \n" + line))));
          }
          default -> {
            level = Level.INFO;
            logMsg = jsonLine.toPrettyString();
          }
        }
        AirbyteMessage logMessage = new AirbyteMessage().withType(Type.LOG).withLog(new AirbyteLogMessage()
            .withLevel(level)
            .withMessage(logMsg));
        return Stream.concat(
            traceMessage.stream(),
            Stream.of(logMessage));
      } else {
        return message.stream();
      }
    }
  }

  public static void main(String[] args) {
    final NormalizationLogParser normalizationLogParser = new NormalizationLogParser();
    final Stream<AirbyteMessage> airbyteMessageStream = normalizationLogParser.create(new BufferedReader(new InputStreamReader(System.in)));
    airbyteMessageStream.forEachOrdered(message -> System.out.println(Jsons.serialize(message)));
  }
}
