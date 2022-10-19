/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter.util;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;

public class FormatterUtil {

  public static final String NESTED_ARRAY_FIELD = "big_query_array";
  public static final String ARRAY_ITEMS_FIELD = "items";
  public static final String TYPE_FIELD = "type";

  public static boolean isAirbyteArray(final JsonNode jsonSchemaNode) {
    if (jsonSchemaNode == null || jsonSchemaNode.get("type") == null) {
      return false;
    }
    final JsonNode type = jsonSchemaNode.get("type");
    if (type.isArray()) {
      final ArrayNode typeNode = (ArrayNode) type;
      for (final JsonNode arrayTypeNode : typeNode) {
        if (arrayTypeNode.isTextual() && arrayTypeNode.textValue().equals("array")) {
          return true;
        }
      }
    } else if (type.isTextual()) {
      return jsonSchemaNode.asText().equals("array");
    }
    return false;
  }

}
