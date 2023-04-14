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
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Stream;
import org.apache.logging.log4j.util.Strings;

/**
 * A simple wrapper for base-normalization logs. Reads messages off of stdin and sticks them into appropriate AirbyteMessages (log or trace), then
 * dumps those messages to stdout
 * <p>
 * does mostly the same thing as {@link io.airbyte.workers.normalization.NormalizationAirbyteStreamFactory}. That class is not actively developed, and
 * will be deleted after all destinations run normalization in-connector.
 */
public class NormalizationLogParser {

  private final List<String> dbtErrors = new ArrayList<>();

  public Stream<AirbyteMessage> create(final BufferedReader bufferedReader) {
    return bufferedReader.lines().flatMap(this::toMessages);
  }

  public List<String> getDbtErrors() {
    return dbtErrors;
  }

  private Stream<AirbyteMessage> toMessages(final String line) {
    if (Strings.isEmpty(line)) {
      return Stream.of(logMessage(Level.INFO, ""));
    }

    final Optional<JsonNode> json = Jsons.tryDeserialize(line);
    if (json.isPresent()) {
      final Optional<AirbyteMessage> message = Jsons.tryObject(json.get(), AirbyteMessage.class);
      if (message.isPresent()) {
        // This line is already an AirbyteMessage; we can just return it directly
        // (these messages come from the transform_config / transform_catalog scripts)
        return message.stream();
      } else {
        // This line is a JSON-format dbt log. We need to extract the message and wrap it in a logmessage
        // And if it's an error, we also need to collect it into dbtErrors
        JsonNode jsonLine = json.get();
        final String logLevel = (jsonLine.getNodeType() == JsonNodeType.NULL || jsonLine.get("level").isNull())
                                ? ""
                                : jsonLine.get("level").asText();
        String logMsg = jsonLine.get("msg").isNull() ? "" : jsonLine.get("msg").asText();
        Level level;
        switch (logLevel) {
          case "debug" -> level = Level.DEBUG;
          case "info" -> level = Level.INFO;
          case "warn" -> level = Level.WARN;
          case "error" -> {
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
    } else {
      // This line is not in JSON at all; we need to wrap it inside a logMessagee
      if (line.contains("[error]")) {
        // Super hacky thing - for versions of dbt that don't support json output, this is how we find their error logs
        dbtErrors.add(line);
      }
      return Stream.of(logMessage(Level.INFO, line));
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
    final Stream<AirbyteMessage> airbyteMessageStream = normalizationLogParser.create(new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8)));
    airbyteMessageStream.forEachOrdered(message -> System.out.println(Jsons.serialize(message)));

    final List<String> errors = normalizationLogParser.getDbtErrors();
    if (!errors.isEmpty()) {
      AirbyteMessage traceMessage = new AirbyteMessage()
          .withType(Type.TRACE)
          .withTrace(new AirbyteTraceMessage()
              .withType(AirbyteTraceMessage.Type.ERROR)
              .withEmittedAt((double) System.currentTimeMillis())
              .withError(new AirbyteErrorTraceMessage()
                  .withFailureType(FailureType.SYSTEM_ERROR)
                  .withMessage("Normalization failed during the dbt run. This may indicate a problem with the data itself.")
                  .withStackTrace("AirbyteDbtError: \n" + String.join("\n", errors))));
      System.out.println(Jsons.serialize(traceMessage));
    }
  }
}
