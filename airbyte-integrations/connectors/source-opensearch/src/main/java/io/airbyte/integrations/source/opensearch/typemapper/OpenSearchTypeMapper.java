/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.opensearch.typemapper;

import static io.airbyte.integrations.source.opensearch.OpenSearchInclusions.KEEP_LIST;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.JsonNodeType;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.integrations.source.opensearch.UnsupportedDatatypeException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

public class OpenSearchTypeMapper {

  private static final ObjectMapper mapper = new ObjectMapper();
  /*
   * Mapping from OpenSearch to Airbyte types OpenSearch data types:
   * https://opensearch.org/docs/2.1/opensearch/supported-field-types/index/
   * types: https://docs.airbyte.com/understanding-airbyte/supported-data-types/
   *
   * In OpenSearch, there is no dedicated array data type. Any field can contain zero or more
   * values by default, however, all values in the array must be of the same data type
   */
  private static final Map<String, Object> OpenSearchToAirbyte = new HashMap<>() {


    {

      // BINARY
      put("binary", Arrays.asList("string", "array"));

      // BOOLEAN
      put("boolean", Arrays.asList("boolean", "array"));

      // String
      put("keyword", Arrays.asList("string", "array"));
      put("text", Arrays.asList("string", "array"));
      put("token_count", Arrays.asList("string", "array"));

      // Numeric
      put("long", Arrays.asList("integer", "array"));
      put("unsigned_long", Arrays.asList("integer", "array"));
      put("integer", Arrays.asList("integer", "array"));
      put("short", Arrays.asList("integer", "array"));
      put("byte", Arrays.asList("integer", "array"));
      put("double", Arrays.asList("number", "array"));
      put("float", Arrays.asList("number", "array"));
      put("half_float", Arrays.asList("number", "array"));
      put("scaled_float", Arrays.asList("number", "array"));

      // DATE
      put("date", Arrays.asList("string", "array"));

      // Autocomplete
      put("completion", Arrays.asList("string"));
      put("search_as_you_type", Arrays.asList("string"));

      // OBJECTS
      put("object", Arrays.asList("object", "array"));
      put("nested", Arrays.asList("object", "string"));
      put("join", Arrays.asList("object", "string"));

      // STRUCTURED DATA TYPES
      put("integer_range", Arrays.asList("object", "array"));
      put("float_range", Arrays.asList("object", "array"));
      put("long_range", Arrays.asList("object", "array"));
      put("double_range", Arrays.asList("object", "array"));
      put("date_range", Arrays.asList("object", "array"));
      put("ip_range", Arrays.asList("object", "array"));

      // IP
      put("ip", Arrays.asList("string", "array"));
      // Alias
      put("alias", Arrays.asList("string", "array"));


      // RANK
      put("rank_feature", "integer");
      put("rank_features", "array");

      // SPATIAL DATA TYPES (HARD TO HANDLE AS QUERYING MECHANISM IS BASED ON SHAPE, which has multiple
      // fields)
      put("geo_point", Arrays.asList("object", "array"));
      put("geo_shape", Arrays.asList("object", "array"));

    }

  };

  public static Map<String, Object> getMapper() {
    return OpenSearchToAirbyte;
  }

  /**
   * @param node JsonNode node which we want to format
   * @return JsonNode
   * @throws UnsupportedDatatypeException throws an exception if none of the types match
   */
  public static JsonNode formatJSONSchema(JsonNode node) throws UnsupportedDatatypeException {
    if (node.isObject()) {
      if (!node.has("type") || node.has("properties")) {
        ((ObjectNode) node).put("type", "object");
      } else if (node.has("type") && node.get("type").getNodeType() == JsonNodeType.STRING) {
        retainAirbyteFieldsOnly(node);

        final String nodeType = node.get("type").textValue();

        if (OpenSearchToAirbyte.containsKey(nodeType)) {
          ((ObjectNode) node).remove("type");
          ((ObjectNode) node).set("type", mapper.valueToTree(OpenSearchToAirbyte.get(nodeType)));
        } else
          throw new UnsupportedDatatypeException("Cannot map unsupported data type to Airbyte data type: " + node.get("type").textValue());
      }
      node.fields().forEachRemaining(entry -> {
        try {
          formatJSONSchema(entry.getValue());
        } catch (UnsupportedDatatypeException e) {
          throw new RuntimeException(e);
        }
      });
      if (node.path("properties").path("type").getNodeType() == JsonNodeType.STRING) {
        ((ObjectNode) node.path("properties")).remove("type");
      } else if (node.has("properties")) {
        ((ObjectNode) node).set("type", mapper.valueToTree(Arrays.asList("array", "object")));
      }
    } else if (node.isArray()) {
      ArrayNode arrayNode = (ArrayNode) node;
      Iterator<JsonNode> temp = arrayNode.elements();
      while (temp.hasNext()) {
        formatJSONSchema(temp.next());
      }
    }
    return node;
  }

  private static void retainAirbyteFieldsOnly(JsonNode jsonNode) {
    if (jsonNode instanceof ObjectNode) {
      ((ObjectNode) jsonNode).retain(KEEP_LIST);
    }
  }

}
