/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.Array;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.OneOf;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.Struct;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.UnsupportedOneOf;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public sealed interface AirbyteType permits Array,OneOf,Struct,UnsupportedOneOf,AirbyteProtocolType {

  Logger LOGGER = LoggerFactory.getLogger(AirbyteTypeUtils.class);

  /**
   * The most common call pattern is probably to use this method on the stream schema, verify that
   * it's an {@link Struct} schema, and then call {@link Struct#properties()} to get the columns.
   * <p>
   * If the top-level schema is not an object, then we can't really do anything with it, and should
   * probably fail the sync. (but see also {@link OneOf#asColumns()}).
   */
  static AirbyteType fromJsonSchema(final JsonNode schema) {
    final JsonNode topLevelType = schema.get("type");
    if (topLevelType != null) {
      if (topLevelType.isTextual()) {
        if (AirbyteTypeUtils.nodeIsType(topLevelType, "object")) {
          return getStruct(schema);
        } else if (AirbyteTypeUtils.nodeIsType(topLevelType, "array")) {
          final JsonNode items = schema.get("items");
          return new Array(fromJsonSchema(items));
        }
      } else if (topLevelType.isArray()) {
        final List<JsonNode> elements = new ArrayList<>();
        topLevelType.elements().forEachRemaining(element -> {
          // ignore "null" type
          if (!element.asText("").equals("null")) {
            elements.add(element);
          }
        });

        // we encounter an array of types that actually represents a single type rather than a OneOf
        if (elements.size() == 1) {
          if (elements.get(0).asText("").equals("object")) {
            return getStruct(schema);
          } else if (elements.get(0).asText("").equals("array")) {
            final JsonNode items = schema.get("items");
            return new Array(fromJsonSchema(items));
          } else {
            return AirbyteTypeUtils.getAirbyteProtocolType(schema);
          }
        }

        final List<AirbyteType> typeOptions = elements.stream().map(AirbyteType::fromJsonSchema).toList();
        return new OneOf(typeOptions);
      }
    } else if (schema.hasNonNull("oneOf")) {
      final List<AirbyteType> options = new ArrayList<>();
      schema.get("oneOf").elements().forEachRemaining(element -> options.add(fromJsonSchema(element)));
      return new UnsupportedOneOf(options);
    } else if (schema.hasNonNull("properties")) {
      // The schema has neither type nor oneof, but it does have properties. Assume we're looking at a
      // struct.
      // This is for backwards-compatibility with legacy normalization.
      return getStruct(schema);
    }
    return AirbyteTypeUtils.getAirbyteProtocolType(schema);
  }

  private static Struct getStruct(final JsonNode schema) {
    final LinkedHashMap<String, AirbyteType> propertiesMap = new LinkedHashMap<>();
    final JsonNode properties = schema.get("properties");
    properties.fields().forEachRemaining(property -> {
      final String key = property.getKey();
      final JsonNode value = property.getValue();
      propertiesMap.put(key, fromJsonSchema(value));
    });
    return new Struct(propertiesMap);
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
    UNKNOWN;

    public static AirbyteProtocolType matches(final String type) {
      try {
        return AirbyteProtocolType.valueOf(type.toUpperCase());
      } catch (final IllegalArgumentException e) {
        LOGGER.error(String.format("Could not find matching AirbyteProtocolType for \"%s\": %s", type, e));
        return UNKNOWN;
      }
    }

  }

  /**
   * @param properties Use LinkedHashMap to preserve insertion order.
   */
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
   * Represents a {type: [a, b, ...]} schema. This is theoretically equivalent to {oneOf: [{type: a},
   * {type: b}, ...]} but legacy normalization only handles the {type: [...]} schemas.
   * <p>
   * Eventually we should:
   * <ol>
   * <li>Announce a breaking change to handle both oneOf styles the same</li>
   * <li>Test against some number of API sources to verify that they won't break badly</li>
   * <li>Update {@link AirbyteType#fromJsonSchema(JsonNode)} to parse both styles into
   * SupportedOneOf</li>
   * <li>Delete UnsupportedOneOf</li>
   * </ol>
   */
  record OneOf(List<AirbyteType> options) implements AirbyteType {

    /**
     * This is a hack to handle weird schemas like {type: [object, string]}. If a stream's top-level
     * schema looks like this, we still want to be able to extract the object properties (i.e. treat it
     * as though the string option didn't exist).
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
