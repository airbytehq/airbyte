/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.elasticsearch.typemapper;

import static io.airbyte.integrations.source.elasticsearch.ElasticsearchInclusions.KEEP_LIST;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.JsonNodeType;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.integrations.source.elasticsearch.UnsupportedDatatypeException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

public class ElasticsearchTypeMapper {

  private static final ObjectMapper mapper = new ObjectMapper();
  /*
   * Mapping from elasticsearch to Airbyte types Elasticsearch data types:
   * https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-types.html Airbyte data
   * types: https://docs.airbyte.com/understanding-airbyte/supported-data-types/
   *
   * In Elasticsearch, there is no dedicated array data type. Any field can contain zero or more
   * values by default, however, all values in the array must be of the same data type
   */
  private static final Map<String, Object> ElasticSearchToAirbyte = new HashMap<>() {

    {

      // BINARY
      put("binary", Arrays.asList("string", "array"));

      // BOOLEAN
      put("boolean", Arrays.asList("boolean", "array"));

      // KEYWORD FAMILY
      put("keyword", Arrays.asList("string", "array", "number", "integer"));
      put("constant_keyword", Arrays.asList("string", "array", "number", "integer"));
      put("wildcard", Arrays.asList("string", "array", "number", "integer"));

      // NUMBERS
      put("long", Arrays.asList("integer", "array"));
      put("unsigned_long", Arrays.asList("integer", "array"));
      put("integer", Arrays.asList("integer", "array"));
      put("short", Arrays.asList("integer", "array"));
      put("byte", Arrays.asList("integer", "array"));
      put("double", Arrays.asList("number", "array"));
      put("float", Arrays.asList("number", "array"));
      put("half_float", Arrays.asList("number", "array"));
      put("scaled_float", Arrays.asList("number", "array"));

      // ALIAS
      /* Writes to alias field not supported by ES. Can be safely ignored */

      // DATES
      put("date", Arrays.asList("string", "array"));
      put("date_nanos", Arrays.asList("number", "array"));

      // OBJECTS AND RELATIONAL TYPES
      put("object", Arrays.asList("object", "array"));
      put("flattened", Arrays.asList("object", "array"));
      put("nested", Arrays.asList("object", "string"));
      put("join", Arrays.asList("object", "string"));

      // STRUCTURED DATA TYPES
      put("integer_range", Arrays.asList("object", "array"));
      put("float_range", Arrays.asList("object", "array"));
      put("long_range", Arrays.asList("object", "array"));
      put("double_range", Arrays.asList("object", "array"));
      put("date_range", Arrays.asList("object", "array"));
      put("ip_range", Arrays.asList("object", "array"));
      put("ip", Arrays.asList("string", "array"));
      put("version", Arrays.asList("string", "array"));
      put("murmur3", Arrays.asList("object", "array"));

      // AGGREGATE METRIC FIELD TYPES
      put("aggregate_metric_double", Arrays.asList("object", "array"));
      put("histogram", Arrays.asList("object", "array"));

      // TEXT SEARCH TYPES
      put("text", Arrays.asList("string", "array"));
      put("alias", Arrays.asList("string", "array"));
      put("search_as_you_type", Arrays.asList("string", "array"));
      put("token_count", Arrays.asList("integer", "array"));

      // DOCUMENT RANKING
      put("dense_vector", "array");
      // put("rank_feature", "integer"); THEY ARE PUTTING OBJECTS HERE AS WELL????

      // SPATIAL DATA TYPES (HARD TO HANDLE AS QUERYING MECHANISM IS BASED ON SHAPE, which has multiple
      // fields)
      put("geo_point", Arrays.asList("object", "array"));
      put("geo_shape", Arrays.asList("object", "array"));
      put("shape", Arrays.asList("object", "array"));
      put("point", Arrays.asList("object", "array"));
    }

  };

  public static Map<String, Object> getMapper() {
    return ElasticSearchToAirbyte;
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

        if (ElasticSearchToAirbyte.containsKey(nodeType)) {
          ((ObjectNode) node).remove("type");
          ((ObjectNode) node).set("type", mapper.valueToTree(ElasticSearchToAirbyte.get(nodeType)));
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
