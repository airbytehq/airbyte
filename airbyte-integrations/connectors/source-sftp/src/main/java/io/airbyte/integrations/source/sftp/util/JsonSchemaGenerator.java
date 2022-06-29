/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sftp.util;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.JsonNodeType;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.util.Iterator;
import java.util.Map.Entry;

public class JsonSchemaGenerator {

  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

  /**
   * Process jsonNodes to transform it to json schema
   * <p>
   *
   * @param jsonNode the jsonNode to process
   * @return a {@link JsonNode} the json schema
   * @throws JsonProcessingException Checked exception used to signal fatal problems with mapping of
   *         content, distinct from low-level I/O problems (signaled using simple IOExceptions)
   */
  public static JsonNode getJsonSchema(JsonNode jsonNode) throws JsonProcessingException {
    JsonNode properties = createProperty(jsonNode);
    ObjectNode objectNode = OBJECT_MAPPER.createObjectNode();
    objectNode.put("type", "object");
    objectNode.set("properties", properties);
    ObjectMapper jacksonObjectMapper = new ObjectMapper();
    return jacksonObjectMapper
        .readTree(cleanUp(jacksonObjectMapper
            .writerWithDefaultPrettyPrinter()
            .writeValueAsString(objectNode)));
  }

  private static ObjectNode createProperty(JsonNode jsonData) {
    ObjectNode propObject = OBJECT_MAPPER.createObjectNode();
    Iterator<Entry<String, JsonNode>> fieldsIterator = jsonData.fields();
    while (fieldsIterator.hasNext()) {
      Entry<String, JsonNode> field = fieldsIterator.next();
      String fieldName = field.getKey();
      JsonNode fieldValue = field.getValue();
      JsonNodeType fieldType = fieldValue.getNodeType();

      ObjectNode property = processJsonField(fieldValue, fieldType, fieldName);
      if (!property.isEmpty()) {
        propObject.set(fieldName, property);
      }
    }
    return propObject;
  }

  private static ObjectNode processJsonField(JsonNode fieldValue, JsonNodeType fieldType, String fieldName) {
    ObjectNode property = OBJECT_MAPPER.createObjectNode();
    switch (fieldType) {
      case ARRAY -> {
        property.put("type", "[\"null\", \"array\"]");
        if (fieldValue.isEmpty()) {
          break;
        }
        JsonNodeType typeOfArrayElements = fieldValue.get(0).getNodeType();
        property.set("items", processJsonField(fieldValue.get(0), typeOfArrayElements, fieldName));
      }
      case BOOLEAN -> property.put("type", "[\"null\", \"boolean\"]");
      case NUMBER -> property.put("type", "[\"null\", \"number\"]");
      case OBJECT -> {
        property.put("type", "[\"null\", \"object\"]");
        property.set("properties", createProperty(fieldValue));
      }
      case STRING -> property.put("type", "[\"null\", \"string\"]");
      case NULL -> property.put("type", "[\"null\", \"string\"]");
      default -> {}
    }
    return property;
  }

  private static String cleanUp(String input) {
    return input
        .replace("\\", "")
        .replace("\"[", "[")
        .replace("]\"", "]");
  }

}
