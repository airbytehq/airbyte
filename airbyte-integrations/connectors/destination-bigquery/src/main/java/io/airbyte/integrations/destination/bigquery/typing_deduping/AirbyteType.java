package io.airbyte.integrations.destination.bigquery.typing_deduping;

import static java.util.stream.Collectors.toList;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public sealed interface AirbyteType permits AirbyteType.Primitive, AirbyteType.Object, AirbyteType.Array, AirbyteType.OneOf {

  /**
   * Some types are equivalent to a simpler type. This method returns that simpler equivalent, or `this` if it's already the simplest representation.
   * <p>
   * This is mostly useful for oneOf schemas.
   */
  AirbyteType simplify();

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
    UNKNOWN;

    public Primitive simplify() {
      // In the future, we may have parameterized types, e.g. number(precision=10, scale=2)
      // at which point there might be some real changes in here (e.g. a scale=0 number is just an integer).
      return this;
    }
  }

  /**
   * @param properties Use LinkedHashMap to preserve insertion order.
   */
  // TODO maybe we shouldn't call this thing Object, since java.lang.Object also exists?
  record Object(LinkedHashMap<String, AirbyteType> properties) implements AirbyteType {

    public Object simplify() {
      return new Object(properties.entrySet().stream()
          .collect(Collectors.toMap(
              Map.Entry::getKey,
              e -> e.getValue().simplify(),
              (a, b) -> b,
              LinkedHashMap::new)));
    }
  }

  record Array(AirbyteType items) implements AirbyteType {

    public Array simplify() {
      return new Array(items.simplify());
    }
  }

  record OneOf(List<AirbyteType> options) implements AirbyteType {

    public AirbyteType simplify() {
      if (options.isEmpty()) {
        // {oneOf: []} disallows all values. We'll assume this is an error, and just use UNKNOWN.
        return Primitive.UNKNOWN;
      } else if (options.size() == 1) {
        // {oneOf: [x]} is equivalent to x.
        return options.get(0);
      } else {
        return new OneOf(options.stream().map(AirbyteType::simplify).collect(toList()));
      }
    }
  }
}
