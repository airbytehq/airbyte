/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.util;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.s3.avro.JsonFieldNameUpdater;
import io.airbyte.integrations.destination.s3.avro.JsonToAvroSchemaConverter;
import java.util.Arrays;
import java.util.Iterator;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * Helper methods for unit tests. This is needed by multiple modules, so it is in the src directory.
 */
public class AvroRecordHelper {

  public static JsonFieldNameUpdater getFieldNameUpdater(final String streamName, final String namespace, final JsonNode streamSchema) {
    final JsonToAvroSchemaConverter schemaConverter = new JsonToAvroSchemaConverter();
    schemaConverter.getAvroSchema(streamSchema, streamName, namespace, true, true);
    return new JsonFieldNameUpdater(schemaConverter.getStandardizedNames());
  }

  /**
   * Convert an Airbyte JsonNode from Avro / Parquet Record to a plain one.
   * <ul>
   * <li>Remove the airbyte id and emission timestamp fields.</li>
   * <li>Remove null fields that must exist in Parquet but does not in original Json. This function
   * mutates the input Json.</li>
   * </ul>
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

  public static void obtainPaths(String currentPath, JsonNode jsonNode, Map<JsonNode, String> jsonNodePathMap) {
    if (jsonNode.isObject()) {
      ObjectNode objectNode = (ObjectNode) jsonNode;
      Iterator<Map.Entry<String, JsonNode>> iter = objectNode.fields();
      String pathPrefix = currentPath.isEmpty() ? "" : currentPath + "/";
      String[] pathFieldsArray = currentPath.split("/");
      String parent = Arrays.stream(pathFieldsArray)
          .filter(x -> !x.equals("items"))
          .filter(x -> !x.equals("properties"))
          .filter(x -> !x.equals(pathFieldsArray[pathFieldsArray.length - 1]))
          .collect(Collectors.joining("."));
      if (!parent.isEmpty()) {
        jsonNodePathMap.put(jsonNode, parent);
      }
      while (iter.hasNext()) {
        Map.Entry<String, JsonNode> entry = iter.next();
        obtainPaths(pathPrefix + entry.getKey(), entry.getValue(), jsonNodePathMap);
      }
    } else if (jsonNode.isArray()) {
      ArrayNode arrayNode = (ArrayNode) jsonNode;

      for (int i = 0; i < arrayNode.size(); i++) {
        String arrayPath = currentPath + "/" + i;
        obtainPaths(arrayPath, arrayNode.get(i), jsonNodePathMap);
      }
    }
  }

}
