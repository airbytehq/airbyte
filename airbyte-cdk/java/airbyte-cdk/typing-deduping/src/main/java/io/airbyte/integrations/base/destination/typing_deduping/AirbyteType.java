/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.databind.node.TextNode;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public sealed interface AirbyteType permits AirbyteProtocolType,Struct,Array,UnsupportedOneOf,Union {

  Logger LOGGER = LoggerFactory.getLogger(AirbyteType.class);

  /**
   * The most common call pattern is probably to use this method on the stream schema, verify that
   * it's an {@link Struct} schema, and then call {@link Struct#properties()} to get the columns.
   * <p>
   * If the top-level schema is not an object, then we can't really do anything with it, and should
   * probably fail the sync. (but see also {@link Union#asColumns()}).
   */
  static AirbyteType fromJsonSchema(final JsonNode schema) {
    try {
      final JsonNode topLevelType = schema.get("type");
      if (topLevelType != null) {
        if (topLevelType.isTextual()) {
          if (nodeMatches(topLevelType, "object")) {
            return getStruct(schema);
          } else if (nodeMatches(topLevelType, "array")) {
            return getArray(schema);
          }
        } else if (topLevelType.isArray()) {
          return fromArrayJsonSchema(schema, topLevelType);
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
      return AirbyteProtocolType.fromJson(schema);
    } catch (final Exception e) {
      LOGGER.error("Exception parsing JSON schema {}: {}; returning UNKNOWN.", schema, e);
      return AirbyteProtocolType.UNKNOWN;
    }
  }

  static boolean nodeMatches(final JsonNode node, final String value) {
    if (node == null || !node.isTextual()) {
      return false;
    }
    return node.equals(TextNode.valueOf(value));
  }

  private static Struct getStruct(final JsonNode schema) {
    final LinkedHashMap<String, AirbyteType> propertiesMap = new LinkedHashMap<>();
    final JsonNode properties = schema.get("properties");
    if (properties != null) {
      properties.fields().forEachRemaining(property -> {
        final String key = property.getKey();
        final JsonNode value = property.getValue();
        propertiesMap.put(key, fromJsonSchema(value));
      });
    }
    return new Struct(propertiesMap);
  }

  private static Array getArray(final JsonNode schema) {
    final JsonNode items = schema.get("items");
    if (items == null) {
      return new Array(AirbyteProtocolType.UNKNOWN);
    } else {
      return new Array(fromJsonSchema(items));
    }
  }

  private static AirbyteType fromArrayJsonSchema(final JsonNode schema, final JsonNode array) {
    final List<String> typeOptions = new ArrayList<>();
    array.elements().forEachRemaining(element -> {
      // ignore "null" type and remove duplicates
      final String type = element.asText("");
      if (!"null".equals(type) && !typeOptions.contains(type)) {
        typeOptions.add(element.asText());
      }
    });

    // we encounter an array of types that actually represents a single type rather than a Union
    if (typeOptions.size() == 1) {
      if (typeOptions.get(0).equals("object")) {
        return getStruct(schema);
      } else if (typeOptions.get(0).equals("array")) {
        return getArray(schema);
      } else {
        return AirbyteProtocolType.fromJson(getTrimmedJsonSchema(schema, typeOptions.get(0)));
      }
    }

    // Recurse into a schema that forces a specific one of each option
    final List<AirbyteType> options = typeOptions.stream().map(typeOption -> fromJsonSchema(getTrimmedJsonSchema(schema, typeOption))).toList();
    return new Union(options);
  }

  // Duplicates the JSON schema but keeps only one type
  private static JsonNode getTrimmedJsonSchema(final JsonNode schema, final String type) {
    final JsonNode schemaClone = schema.deepCopy();
    // schema is guaranteed to be an object here, because we know it has a `type` key
    ((ObjectNode) schemaClone).put("type", type);
    return schemaClone;
  }

}
