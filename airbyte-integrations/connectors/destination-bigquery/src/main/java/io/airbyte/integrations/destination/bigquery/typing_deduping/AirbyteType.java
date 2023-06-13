package io.airbyte.integrations.destination.bigquery.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.AirbyteProtocolType;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Array;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.OneOf;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Struct;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.UnsupportedOneOf;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public sealed interface AirbyteType permits Array, OneOf, Struct, UnsupportedOneOf, AirbyteProtocolType {

  /**
   * The most common call pattern is probably to use this method on the stream schema, verify that it's an {@link Struct} schema, and then call
   * {@link Struct#properties()} to get the columns.
   * <p>
   * If the top-level schema is not an object, then we can't really do anything with it, and should probably fail the sync. (but see also
   * {@link OneOf#asColumns()}).
   */
  static AirbyteType fromJsonSchema(final JsonNode schema) {
    // TODO

    final JsonNode topLevelType = schema.get("type");
    if (nodeMatchesType(topLevelType, "object")) {
      final LinkedHashMap<String, AirbyteType> propertiesMap = new LinkedHashMap<>();
      final JsonNode properties = schema.get("properties");
      properties.fields().forEachRemaining(property -> {
        final String key = property.getKey();
        final JsonNode value = property.getValue();
        final JsonNode type = value.get("type");
        final JsonNode airbyteType = value.get("airbyte_type");
        // Treat simple types from narrower to wider scope type: boolean < integer < number < string
        if (nodeMatchesType(type, "boolean")) {
          propertiesMap.put(key, AirbyteProtocolType.BOOLEAN);
        } else if (nodeMatchesType(airbyteType, "big_integer")) {
          propertiesMap.put(key, AirbyteProtocolType.INTEGER);
        } else if (nodeMatchesType(type, "number")) {
          propertiesMap.put(key, AirbyteProtocolType.NUMBER);
        } else if (nodeMatchesType(type, "string")) {
          final JsonNode format = value.get("format");
          if (nodeMatchesType(format, "date-time")) {
            if (airbyteType == null || nodeMatchesType(airbyteType, "timestamp_with_timezone")) {
              propertiesMap.put(key, AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);
            } else if (nodeMatchesType(airbyteType, "timestamp_without_timezone")) {
              propertiesMap.put(key, AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE);
            }
          } else if (nodeMatchesType(format, "date")) {
            propertiesMap.put(key, AirbyteProtocolType.DATE);
          } else if (nodeMatchesType(format, "time")) {
            if (nodeMatchesType(airbyteType, "time_with_timezone")) {
              propertiesMap.put(key, AirbyteProtocolType.TIME_WITH_TIMEZONE);
            } else if (nodeMatchesType(airbyteType, "time_without_timezone")) {
              propertiesMap.put(key, AirbyteProtocolType.TIME_WITHOUT_TIMEZONE);
            }
          } else {
            propertiesMap.put(key, AirbyteProtocolType.STRING);
          }
        } else {
          // TODO add more types
          propertiesMap.put(key, AirbyteProtocolType.UNKNOWN);
        }
      });
      return new Struct(propertiesMap);
    } else if (nodeMatchesType(topLevelType, "array")) {
      // TODO parse items
    } else {
      // TODO handle oneOf, etc.
    }

    return new Struct(new LinkedHashMap<>());
  }

  // Map from a type to what other types should take precedence over it if present
  Map<String, List> EXCLUDED_TYPES_MAP = ImmutableMap.of(
      // Give priority to wider scope types
      "number", ImmutableList.of("string"),
      // TODO fix bigint and long
      "boolean", ImmutableList.of("string", "number", "bigint", "long")
  );

  // String node matches the type, or array node contains the type
  private static boolean nodeMatchesType(final JsonNode node, final String type) {
    if (node == null) {
      return false;
    } else if (node.isTextual()) {
      return node.toString().equals(type);
    } else if (node.isArray()) {
      final List<String> excludedOtherTypes = EXCLUDED_TYPES_MAP.get(type);
      boolean foundExcludedTypes = false;
      boolean foundType = false;
      for (final JsonNode itemNode : node) {
        if (excludedOtherTypes != null && excludedOtherTypes.contains(itemNode.toString())) {
          foundExcludedTypes = true;
          break; // no need to continue
        }
        if (itemNode.toString().equals(type)) {
          foundType = true;
        }
      }
      return foundType && !foundExcludedTypes;
    }
    return false;
  }

  enum AirbyteProtocolType implements AirbyteType {
    STRING,
    NUMBER,
    INTEGER,
    BOOLEAN,
    TIMESTAMP_WITH_TIMEZONE,
    TIMESTAMP_WITHOUT_TIMEZONE,
    TIME_WITH_TIMEZONE,
    TIME_WITHOUT_TIMEZONE,
    DATE,
    UNKNOWN
  }

  /**
   * @param properties Use LinkedHashMap to preserve insertion order.
   */
  // TODO maybe we shouldn't call this thing Object, since java.lang.Object also exists?
  record Struct(LinkedHashMap<String, AirbyteType> properties) implements AirbyteType {

  }

  record Array(AirbyteType items) implements AirbyteType {

  }

  /**
   * Represents a {oneOf: [...]} schema.
   * <p>
   * This is purely a legacy type that we should eventually delete. See also {@link OneOf}.
   */
  record UnsupportedOneOf(List<AirbyteType> options) implements AirbyteType {

  }

  /**
   * Represents a {type: [a, b, ...]} schema. This is theoretically equivalent to {oneOf: [{type: a}, {type: b}, ...]} but legacy normalization only
   * handles the {type: [...]} schemas.
   * <p>
   * Eventually we should:
   * <ol>
   *   <li>Announce a breaking change to handle both oneOf styles the same</li>
   *   <li>Test against some number of API sources to verify that they won't break badly</li>
   *   <li>Update {@link AirbyteType#fromJsonSchema(JsonNode)} to parse both styles into SupportedOneOf</li>
   *   <li>Delete UnsupportedOneOf</li>
   *  </ol>
   */
  record OneOf(List<AirbyteType> options) implements AirbyteType {

    /**
     * This is a hack to handle weird schemas like {type: [object, string]}. If a stream's top-level schema looks like this, we still want to be able
     * to extract the object properties (i.e. treat it as though the string option didn't exist).
     *
     * @throws IllegalArgumentException if we cannot extract columns from this schema
     */
    public LinkedHashMap<String, AirbyteType> asColumns() {
      final long numObjectOptions = options.stream().filter(o -> o instanceof Struct).count();
      if (numObjectOptions > 1) {
        throw new IllegalArgumentException("Can't extract columns from a schema with multiple object options");
      }

      return (options.stream().filter(o -> o instanceof Struct).findFirst())
          .map(o -> ((Struct) o).properties())
          .orElseThrow(() -> new IllegalArgumentException("Can't extract columns from a schema with no object options"));
    }
  }
}
