package io.airbyte.integrations.destination.keen;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.JsonNodeFactory;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.joestelmach.natty.Parser;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.stream.Collectors;
import org.apache.commons.lang3.tuple.Pair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KeenTimestampService {

  public enum CursorType {STRING, NUMBER, UNRECOGNIZED}

  private static final Logger LOGGER = LoggerFactory.getLogger(KeenRecordsConsumer.class);

  private static final long SECONDS_FROM_EPOCH_THRESHOLD = 1_000_000_000L;

  private static final long MILLIS_FROM_EPOCH_THRESHOLD = 10_000_000_000L;

  // Map containing stream names paired with their cursor fields
  private Map<String, CursorField> streamCursorFields;
  private final Parser parser;
  private final boolean timestampInferenceEnabled;

  public KeenTimestampService(ConfiguredAirbyteCatalog catalog, boolean timestampInferenceEnabled) {
    this.streamCursorFields = new HashMap<>();
    this.parser = new Parser();
    this.timestampInferenceEnabled = timestampInferenceEnabled;

    if (timestampInferenceEnabled) {
      LOGGER.info("Initializing KeenTimestampService, finding cursor fields.");
      streamCursorFields = catalog.getStreams()
          .stream()
          .filter(stream -> stream.getCursorField().size() == 1)
          .map(s -> Pair.of(s.getStream().getName(), CursorField.fromStream(s)))
          .filter(
              pair -> pair.getRight() != null && pair.getRight().type != CursorType.UNRECOGNIZED)
          .collect(Collectors.toMap(Pair::getKey, Pair::getValue));
    }
  }

  /**
   * Tries to inject keen.timestamp field to the given message data. If it's incremental sync stream,
   * which cursor value is of type NUMBER, or STRING, this value is tried to be parsed to timestamp.
   * If this procedure fails, stream is removed from timestamp-parsable stream map, so parsing is not tried
   * for future messages in the same stream. If parsing succeeds, keen.timestamp field is put as a JSON node
   * to the message data and whole data is returned.
   * @param message AirbyteMessage containing record data
   * @return Record data together with keen.timestamp if parsing succeeds.
   */
  public JsonNode injectTimestamp(AirbyteMessage message) {
    String streamName = message.getRecord().getStream();
    CursorField cursorField = streamCursorFields.get(streamName);
    JsonNode data = message.getRecord().getData();
    if (timestampInferenceEnabled && cursorField != null) {
      try {
        String timestamp = parseTimestamp(cursorField, data);
        injectTimestamp(data, timestamp);
      } catch (Exception e) {
        // If parsing of timestamp has failed, remove stream from timestamp-parsable stream map,
        // so it won't be parsed for future messages.
        LOGGER.info("Unable to parse timestamp field: " + cursorField.name);
        streamCursorFields.remove(streamName);
        injectTimestamp(data, Instant.ofEpochMilli(message.getRecord().getEmittedAt()).toString());
      }
    }
    else {
      injectTimestamp(data, Instant.ofEpochMilli(message.getRecord().getEmittedAt()).toString());
    }
    return data;
  }

  private void injectTimestamp(JsonNode data, String timestamp) {
    ObjectNode root = ((ObjectNode) data);
    root.set("keen", JsonNodeFactory.instance.objectNode().put("timestamp", timestamp));
  }

  private String parseTimestamp(CursorField cursorField, JsonNode data) {
    return switch (cursorField.type) {
      case NUMBER -> dateFromNumber(data.get(cursorField.name).asLong());
      case STRING -> parser
          .parse(data.get(cursorField.name).asText())
          .get(0).getDates()
          .get(0)
          .toInstant()
          .toString();
      default -> throw new IllegalStateException("Unexpected value: " + cursorField.type);
    };
  }

  private String dateFromNumber(Long timestamp) {
    // if cursor value is below given threshold, assume that it's not epoch timestamp but ordered id
    if (timestamp < SECONDS_FROM_EPOCH_THRESHOLD) {
      throw new IllegalArgumentException("Number cursor field below threshold: " + timestamp);
    }
    // if cursor value is above given threshold, then assume that it's Unix timestamp in milliseconds
    if (timestamp > MILLIS_FROM_EPOCH_THRESHOLD) {
      return Instant.ofEpochMilli(timestamp).toString();
    }
    return Instant.ofEpochSecond(timestamp).toString();
  }

  public static class CursorField {

    private static final Set<String> STRING_TYPES = Set.of(
        "STRING", "CHAR", "NCHAR", "NVARCHAR", "VARCHAR", "LONGVARCHAR", "DATE",
        "TIME", "TIMESTAMP"
    );
    private static final Set<String> NUMBER_TYPES = Set.of(
        "NUMBER", "TINYINT", "SMALLINT", "INT", "INTEGER", "BIGINT", "FLOAT", "DOUBLE",
        "REAL", "NUMERIC", "DECIMAL"
    );

    private final String name;
    private final CursorType type;

    public CursorField(String name, CursorType type) {
      this.name = name;
      this.type = type;
    }

    protected static CursorField fromStream(ConfiguredAirbyteStream stream) {
      List<String> defaultCursorField = stream.getStream().getDefaultCursorField();
      if (defaultCursorField == null || defaultCursorField.size() < 1){
        return null;
      }
      String cursorField = defaultCursorField.get(0);
      JsonNode typeNode = stream.getStream().getJsonSchema()
          .get("properties").get(cursorField).get("type");
      return new CursorField(cursorField, getType(typeNode));
    }

    private static CursorType getType(JsonNode typeNode) {
      CursorType type = CursorType.UNRECOGNIZED;
      if (typeNode.isArray()) {
        for (JsonNode e : typeNode) {
          type = getType(e.asText().toUpperCase());
          if (type != CursorType.UNRECOGNIZED) {
            break;
          }
        }
        return type;
      }
      return getType(typeNode.asText().toUpperCase());
    }

    private static CursorType getType(String typeString) {
      if (STRING_TYPES.contains(typeString)) {
        return CursorType.STRING;
      }
      if (NUMBER_TYPES.contains(typeString)) {
        return CursorType.NUMBER;
      }
      return CursorType.UNRECOGNIZED;
    }

    @Override
    public boolean equals(Object o) {
      if (this == o) return true;
      if (o == null || getClass() != o.getClass()) return false;
      CursorField that = (CursorField) o;
      return Objects.equals(name, that.name) && type == that.type;
    }

    @Override
    public int hashCode() {
      return Objects.hash(name, type);
    }

  }

  public Map<String, CursorField> getStreamCursorFields() {
    return streamCursorFields;
  }

}
