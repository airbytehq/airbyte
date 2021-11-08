/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.util;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.IntNode;
import com.fasterxml.jackson.databind.node.LongNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.databind.node.ValueNode;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.s3.avro.JsonFieldNameUpdater;
import io.airbyte.integrations.destination.s3.avro.JsonToAvroSchemaConverter;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Helper methods for unit tests. This is needed by multiple modules, so it is in the src directory.
 */
public class AvroRecordHelper {

  public static JsonFieldNameUpdater getFieldNameUpdater(final String streamName, final String namespace, final JsonNode streamSchema) {
    final JsonToAvroSchemaConverter schemaConverter = new JsonToAvroSchemaConverter();
    schemaConverter.getAvroSchema(streamSchema, streamName, namespace, true);
    return new JsonFieldNameUpdater(schemaConverter.getStandardizedNames());
  }

  /**
   * Convert an Airbyte JsonNode from Avro / Parquet Record to a plain one.
   * <li>Remove the airbyte id and emission timestamp fields.</li>
   * <li>Remove null fields that must exist in Parquet but does not in original Json.</li> This
   * function mutates the input Json.
   */
  public static JsonNode pruneAirbyteJson(final JsonNode input) {
    final ObjectNode output = (ObjectNode) input;

    // Remove Airbyte columns.
    output.remove(JavaBaseConstants.COLUMN_NAME_AB_ID);
    output.remove(JavaBaseConstants.COLUMN_NAME_EMITTED_AT);

    // Fields with null values does not exist in the original Json but only in Parquet.
    for (final String field : MoreIterators.toList(output.fieldNames())) {
      if (output.get(field) == null || output.get(field).isNull()) {
        output.remove(field);
      }
    }

    return output;
  }

  /**
   * Create all possible paths (jsonPointers) for json record or json schema
   */
  private static void addKeys(String currentPath, JsonNode jsonNode, Map<String, String> map, boolean jsonSchema) {
    if (jsonNode.isObject()) {
      ObjectNode objectNode = (ObjectNode) jsonNode;
      Iterator<Map.Entry<String, JsonNode>> iter = objectNode.fields();
      String pathPrefix = currentPath.isEmpty() ? "" : currentPath + "/";

      while (iter.hasNext()) {
        Map.Entry<String, JsonNode> entry = iter.next();
        addKeys(pathPrefix + entry.getKey(), entry.getValue(), map, jsonSchema);
      }
    } else if (jsonNode.isArray()) {
      ArrayNode arrayNode = (ArrayNode) jsonNode;

      for (int i = 0; i < arrayNode.size(); i++) {
        String arrayPath = currentPath + "/" + i;
        addKeys(arrayPath, arrayNode.get(i), map, jsonSchema);
      }

    } else if (jsonNode.isValueNode()) {
      ValueNode valueNode = (ValueNode) jsonNode;
      if (jsonSchema) {
        if (schemaContainsProperties(currentPath, valueNode, "format", List.of("date", "date-time", "time"))) {
          map.put("/" + currentPath, valueNode.asText());
        }
      } else {
        String value = valueNode.asText();
        if (!value.equals("null") && !value.isBlank() && !Boolean.parseBoolean(value)) {
          map.put("/" + currentPath, value);
        }
      }
    }
  }

  private static boolean schemaContainsProperties(String currentPath, ValueNode valueNode, String key, List<String> properties) {
    return currentPath.endsWith(key) && properties.contains(valueNode.asText());
  }

  public static void transformDateTimeInJson(JsonNode jsonSchema, JsonNode recordMessageData) {
    Map<String, String> map = new HashMap<>();
    Map<String, String> schemaMap = new HashMap<>();
    addKeys("", recordMessageData, map, false);
    addKeys("", jsonSchema, schemaMap, true);
    convertDateTimeInRecord(recordMessageData, map, schemaMap);
  }

  private static void convertDateTimeInRecord(JsonNode recordMessageData, Map<String, String> jsonRecordMap, Map<String, String> schemaMap) {
    schemaMap.forEach((schemaKey, format) -> {
      List<String> schemaKeys = Arrays.stream(schemaKey.split("/"))
          .filter(key -> !key.isBlank())
          .filter(key -> !key.equals("items"))
          .filter(key -> !key.equals("properties"))
          .filter(key -> !key.equals("format"))
          .collect(Collectors.toList());
      jsonRecordMap.forEach((jsonPath, jsonValue) -> {
        List<String> jsonKeys = Arrays.stream(jsonPath.split("/"))
            .filter(key -> !key.isBlank())
            .filter(key -> !key.matches("-?\\d+"))
            .collect(Collectors.toList());
        // match path of json record and json schema
        if (schemaKeys.equals(jsonKeys)) {
          int delimiter = jsonPath.lastIndexOf("/");
          String jsonPointer = jsonPath.substring(0, delimiter);
          String fieldName = jsonPath.substring(delimiter + 1);
          // numeric fieldName is valid only for ArrayNode
          if (fieldName.matches("-?\\d+")) {
            ((ArrayNode) recordMessageData.at(jsonPointer)).set(Integer.parseInt(fieldName),
                getNodeForModification(format, jsonRecordMap.get(jsonPath)));
          } else {
            ((ObjectNode) recordMessageData.at(jsonPointer)).put(fieldName,
                getNodeForModification(format, jsonRecordMap.get(jsonPath)));
          }
        }
      });
    });
  }

  private static JsonNode getNodeForModification(String format, String dateTime) {
    switch (format) {
      case "date" -> {
        return new IntNode(DateTimeUtils.getEpochDay(dateTime));
      }
      case "date-time" -> {
        return new LongNode(DateTimeUtils.getEpochMillis(dateTime));
      }
      case "time" -> {
        return new LongNode(DateTimeUtils.getMicroSeconds(dateTime));
      }
    }
    throw new RuntimeException("Failed to find necessary date-time format");
  }

}
