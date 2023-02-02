/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter.util;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.bigquery.JsonSchemaType;

public class FormatterUtil {

  public static final String NESTED_ARRAY_FIELD = "big_query_array";
  public static final String ARRAY_ITEMS_FIELD = "items";
  public static final String TYPE_FIELD = "type";
  public static final String REF_TYPE_KEY = "$ref";

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

  public static JsonNode getTypeSchemaNode(JsonSchemaType type) {
    return Jsons.deserialize("{\"$ref\" : \"" + type.getJsonSchemaType() + "\"}");
  }

  public static boolean hasNoSchemaRef(String refValue) {
    return !(JsonSchemaType.STRING.getJsonSchemaType().equals(refValue) ||
        JsonSchemaType.NUMBER.getJsonSchemaType().equals(refValue) ||
        JsonSchemaType.INTEGER.getJsonSchemaType().equals(refValue) ||
        JsonSchemaType.BOOLEAN.getJsonSchemaType().equals(refValue) ||
        JsonSchemaType.DATE.getJsonSchemaType().equals(refValue) ||
        JsonSchemaType.TIMESTAMP_WITHOUT_TIMEZONE.getJsonSchemaType().equals(refValue) ||
        JsonSchemaType.TIMESTAMP_WITH_TIMEZONE.getJsonSchemaType().equals(refValue) ||
        JsonSchemaType.TIME_WITHOUT_TIMEZONE.getJsonSchemaType().equals(refValue) ||
        JsonSchemaType.TIME_WITH_TIMEZONE.getJsonSchemaType().equals(refValue) ||
        JsonSchemaType.BINARY_DATA.getJsonSchemaType().equals(refValue));
  }

  /**
   * JsonToAvroSchemaConverter.java accept $ref with type only. This method will replace any $ref
   * which is not in WellKnownTypes with WellKnownTypes.json#/definitions/String
   */
  public static JsonNode replaceNoSchemaRef(JsonNode jsonSchema) {
    String schemaText = Jsons.serialize(jsonSchema);
    schemaText = schemaText.replaceAll("\"\\$ref\\\":"
        + "(?!.*\\s*\"WellKnownTypes\\.json#\\/definitions\\/String\")"
        + "(?!.*\\s*\"WellKnownTypes\\.json#\\/definitions\\/Number\")"
        + "(?!.*\\s*\"WellKnownTypes\\.json#\\/definitions\\/Integer\")"
        + "(?!.*\\s*\"WellKnownTypes\\.json#\\/definitions\\/Boolean\")"
        + "(?!.*\\s*\"WellKnownTypes\\.json#\\/definitions\\/Date\")"
        + "(?!.*\\s*\"WellKnownTypes\\.json#\\/definitions\\/TimestampWithoutTimezone\")"
        + "(?!.*\\s*\"WellKnownTypes\\.json#\\/definitions\\/TimestampWithTimezone\")"
        + "(?!.*\\s*\"WellKnownTypes\\.json#\\/definitions\\/TimeWithoutTimezone\")"
        + "(?!.*\\s*\"WellKnownTypes\\.json#\\/definitions\\/TimeWithTimezone\")"
        + "(?!.*\\s*\"WellKnownTypes\\.json#\\/definitions\\/BinaryData\").*\"",
        "\"\\$ref\":\"WellKnownTypes.json#/definitions/String\"");
    return Jsons.deserialize(schemaText);
  }

  /**
   * BigQuery avro file loader doesn't support DATETIME(TimestampWithoutTimezone) should be replaced
   * with TIMESTAMP(TimestampWithTimezone)
   * https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-avro#logical_types
   *
   * @param jsonSchema for replacement
   * @return JsonNode with replaced DATETIME -> TIMESTAMP
   */
  public static JsonNode replaceDateTime(final JsonNode jsonSchema) {
    final String schemaText = Jsons.serialize(jsonSchema)
        .replace("\"$ref\":\"WellKnownTypes.json#/definitions/TimestampWithoutTimezone\"",
            "\"$ref\":\"WellKnownTypes.json#/definitions/TimestampWithTimezone\"");
    return Jsons.deserialize(schemaText);
  }

}
