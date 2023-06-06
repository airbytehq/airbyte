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
    DATE
  }

  /**
   * @param properties Use LinkedHashMap to preserve insertion order.
   */
  record Object(LinkedHashMap<String, AirbyteType> properties) implements AirbyteType {

  }

  record Array(AirbyteType items) implements AirbyteType {

  }

  record OneOf(List<AirbyteType> options) implements AirbyteType {

  }
}
