package io.airbyte.integrations.destination.bigquery.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.LinkedHashMap;
import java.util.List;

public sealed interface AirbyteType permits AirbyteType.Primitive, AirbyteType.Object, AirbyteType.Array, AirbyteType.OneOf {

  /**
   * The most common call pattern is probably to use this method on the stream schema, verify that it's an {@link Object} schema, and then call
   * {@link Object#asColumns()} on it.
   * <p>
   * If the top-level schema is not an object, then we can't really do anything with it, and should probably fail the sync.
   */
  static AirbyteType fromJsonSchema(JsonNode schema) {
    // TODO
    return null;
  }

  enum Primitive implements AirbyteType {
    STRING,
    NUMBER,
    INTEGER,
    BOOLEAN,
    TIMESTAMP_WITH_TIMEZONE,
    TIMESTAMP_WITHOUT_TIMEZONE,
    TIME_WITH_TIMEZONE,
    TIME_WITHOUT_TIMEZONE,
    DATE,
    // TODO maybe this should be its own class
    UNKNOWN
  }

  /**
   * @param properties Use LinkedHashMap to preserve insertion order.
   */
  // TODO maybe we shouldn't call this thing Object, since java.lang.Object also exists?
  record Object(LinkedHashMap<String, AirbyteType> properties) implements AirbyteType {

    LinkedHashMap<String, AirbyteType> asColumns() {
      return properties.entrySet().stream()
          .collect(
              LinkedHashMap::new,
              (map, entry) -> map.put(entry.getKey(), entry.getValue()),
              LinkedHashMap::putAll);
    }
  }

  record Array(AirbyteType items) implements AirbyteType {

  }

  record OneOf(List<AirbyteType> options) implements AirbyteType {

  }
}
