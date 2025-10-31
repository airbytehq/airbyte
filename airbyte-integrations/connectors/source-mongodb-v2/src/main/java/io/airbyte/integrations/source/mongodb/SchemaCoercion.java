/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import java.util.Iterator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Utility class for coercing data to match JSON Schema expectations.
 * Specifically handles the case where MongoDB stores single objects as objects
 * but the schema expects an array of objects.
 */
public class SchemaCoercion {

  private static final Logger LOGGER = LoggerFactory.getLogger(SchemaCoercion.class);

  /**
   * Coerces data to match the provided JSON Schema.
   * Currently handles the case where a field is an object but the schema expects an array.
   *
   * @param data The data to coerce
   * @param schema The JSON Schema to match
   * @return The coerced data
   */
  public static JsonNode coerce(final JsonNode data, final JsonNode schema) {
    if (data == null || schema == null) {
      return data;
    }

    return coerceNode(data, schema);
  }

  private static JsonNode coerceNode(final JsonNode data, final JsonNode schema) {
    if (data == null || data.isNull() || schema == null || schema.isNull()) {
      return data;
    }

    final JsonNode schemaType = schema.get("type");
    if (schemaType == null) {
      return data;
    }

    if (schemaTypeIncludes(schemaType, "object") && data.isObject()) {
      return coerceObject((ObjectNode) data, schema);
    } else if (schemaTypeIncludes(schemaType, "array")) {
      return coerceArray(data, schema);
    }

    return data;
  }

  private static JsonNode coerceObject(final ObjectNode data, final JsonNode schema) {
    final JsonNode properties = schema.get("properties");
    if (properties == null || !properties.isObject()) {
      return data;
    }

    final ObjectNode result = data.deepCopy();

    final Iterator<String> fieldNames = properties.fieldNames();
    while (fieldNames.hasNext()) {
      final String fieldName = fieldNames.next();
      final JsonNode fieldValue = result.get(fieldName);
      if (fieldValue != null) {
        final JsonNode fieldSchema = properties.get(fieldName);
        final JsonNode coercedValue = coerceNode(fieldValue, fieldSchema);
        result.set(fieldName, coercedValue);
      }
    }

    return result;
  }

  private static JsonNode coerceArray(final JsonNode data, final JsonNode schema) {
    final JsonNode items = schema.get("items");

    if (data.isObject()) {
      LOGGER.debug("Coercing object to array to match schema");
      final ArrayNode arrayNode = Jsons.arrayNode();
      arrayNode.add(data);

      if (items != null && !items.isNull()) {
        final JsonNode coercedElement = coerceNode(data, items);
        final ArrayNode result = Jsons.arrayNode();
        result.add(coercedElement);
        return result;
      }

      return arrayNode;
    }

    if (data.isArray() && items != null && !items.isNull()) {
      final ArrayNode result = Jsons.arrayNode();
      for (final JsonNode element : data) {
        result.add(coerceNode(element, items));
      }
      return result;
    }

    return data;
  }

  /**
   * Checks if a schema type includes the specified type.
   * Handles both string types and array of types.
   *
   * @param schemaType The type field from the schema (can be string or array)
   * @param type The type to check for
   * @return true if the schema type includes the specified type
   */
  private static boolean schemaTypeIncludes(final JsonNode schemaType, final String type) {
    if (schemaType.isTextual()) {
      return schemaType.asText().equals(type);
    } else if (schemaType.isArray()) {
      for (final JsonNode typeNode : schemaType) {
        if (typeNode.isTextual() && typeNode.asText().equals(type)) {
          return true;
        }
      }
    }
    return false;
  }

}
