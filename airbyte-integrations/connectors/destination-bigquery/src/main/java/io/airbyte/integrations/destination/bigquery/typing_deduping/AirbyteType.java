package io.airbyte.integrations.destination.bigquery.typing_deduping;

import java.util.LinkedHashMap;
import java.util.List;

public sealed interface AirbyteType permits AirbyteType.Primitive, AirbyteType.Object, AirbyteType.Array, AirbyteType.OneOf {


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

  }

  record Array(AirbyteType items) implements AirbyteType {

  }

  record OneOf(List<AirbyteType> options) implements AirbyteType {

  }
}
