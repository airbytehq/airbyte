/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import org.junit.jupiter.api.Test;

class SchemaCoercionTest {

  @Test
  void testCoerceObjectToArray() {
    final String schemaJson = """
                              {
                                "type": "object",
                                "properties": {
                                  "assetItemCharacterstics": {
                                    "type": "array",
                                    "items": {
                                      "type": "object",
                                      "properties": {
                                        "chID": {"type": "string"},
                                        "chName": {"type": "string"},
                                        "valueDetail": {"type": "string"}
                                      }
                                    }
                                  }
                                }
                              }
                              """;

    final String dataJson = """
                            {
                              "assetItemCharacterstics": {
                                "chID": "123-456-789",
                                "chName": "name",
                                "valueDetail": "[9999]"
                              }
                            }
                            """;

    final JsonNode schema = Jsons.deserialize(schemaJson);
    final JsonNode data = Jsons.deserialize(dataJson);

    final JsonNode result = SchemaCoercion.coerce(data, schema);

    assertTrue(result.get("assetItemCharacterstics").isArray());
    assertEquals(1, result.get("assetItemCharacterstics").size());
    assertEquals("123-456-789", result.get("assetItemCharacterstics").get(0).get("chID").asText());
    assertEquals("name", result.get("assetItemCharacterstics").get(0).get("chName").asText());
    assertEquals("[9999]", result.get("assetItemCharacterstics").get(0).get("valueDetail").asText());
  }

  @Test
  void testCoerceArrayRemainsArray() {
    final String schemaJson = """
                              {
                                "type": "object",
                                "properties": {
                                  "items": {
                                    "type": "array",
                                    "items": {"type": "object"}
                                  }
                                }
                              }
                              """;

    final String dataJson = """
                            {
                              "items": [
                                {"id": "1"},
                                {"id": "2"}
                              ]
                            }
                            """;

    final JsonNode schema = Jsons.deserialize(schemaJson);
    final JsonNode data = Jsons.deserialize(dataJson);

    final JsonNode result = SchemaCoercion.coerce(data, schema);

    assertTrue(result.get("items").isArray());
    assertEquals(2, result.get("items").size());
    assertEquals("1", result.get("items").get(0).get("id").asText());
    assertEquals("2", result.get("items").get(1).get("id").asText());
  }

  @Test
  void testCoerceNestedObjectToArray() {
    final String schemaJson = """
                              {
                                "type": "object",
                                "properties": {
                                  "parent": {
                                    "type": "object",
                                    "properties": {
                                      "children": {
                                        "type": "array",
                                        "items": {"type": "object"}
                                      }
                                    }
                                  }
                                }
                              }
                              """;

    final String dataJson = """
                            {
                              "parent": {
                                "children": {
                                  "name": "single-child"
                                }
                              }
                            }
                            """;

    final JsonNode schema = Jsons.deserialize(schemaJson);
    final JsonNode data = Jsons.deserialize(dataJson);

    final JsonNode result = SchemaCoercion.coerce(data, schema);

    assertTrue(result.get("parent").get("children").isArray());
    assertEquals(1, result.get("parent").get("children").size());
    assertEquals("single-child", result.get("parent").get("children").get(0).get("name").asText());
  }

  @Test
  void testCoerceWithUnionType() {
    final String schemaJson = """
                              {
                                "type": "object",
                                "properties": {
                                  "field": {
                                    "type": ["null", "array"],
                                    "items": {"type": "object"}
                                  }
                                }
                              }
                              """;

    final String dataJson = """
                            {
                              "field": {
                                "value": "test"
                              }
                            }
                            """;

    final JsonNode schema = Jsons.deserialize(schemaJson);
    final JsonNode data = Jsons.deserialize(dataJson);

    final JsonNode result = SchemaCoercion.coerce(data, schema);

    assertTrue(result.get("field").isArray());
    assertEquals(1, result.get("field").size());
    assertEquals("test", result.get("field").get(0).get("value").asText());
  }

  @Test
  void testCoerceWithNullData() {
    final String schemaJson = """
                              {
                                "type": "object",
                                "properties": {
                                  "field": {
                                    "type": "array"
                                  }
                                }
                              }
                              """;

    final JsonNode schema = Jsons.deserialize(schemaJson);
    final JsonNode data = null;

    final JsonNode result = SchemaCoercion.coerce(data, schema);

    assertEquals(null, result);
  }

  @Test
  void testCoerceWithNullSchema() {
    final String dataJson = """
                            {
                              "field": {
                                "value": "test"
                              }
                            }
                            """;

    final JsonNode schema = null;
    final JsonNode data = Jsons.deserialize(dataJson);

    final JsonNode result = SchemaCoercion.coerce(data, schema);

    assertEquals(data, result);
  }

  @Test
  void testCoerceDoesNotModifyOriginal() {
    final String schemaJson = """
                              {
                                "type": "object",
                                "properties": {
                                  "field": {
                                    "type": "array"
                                  }
                                }
                              }
                              """;

    final String dataJson = """
                            {
                              "field": {
                                "value": "test"
                              }
                            }
                            """;

    final JsonNode schema = Jsons.deserialize(schemaJson);
    final ObjectNode data = (ObjectNode) Jsons.deserialize(dataJson);

    final JsonNode result = SchemaCoercion.coerce(data, schema);

    assertTrue(data.get("field").isObject());
    assertTrue(result.get("field").isArray());
  }

  @Test
  void testCoerceWithMissingProperty() {
    final String schemaJson = """
                              {
                                "type": "object",
                                "properties": {
                                  "field1": {
                                    "type": "array"
                                  },
                                  "field2": {
                                    "type": "string"
                                  }
                                }
                              }
                              """;

    final String dataJson = """
                            {
                              "field2": "value"
                            }
                            """;

    final JsonNode schema = Jsons.deserialize(schemaJson);
    final JsonNode data = Jsons.deserialize(dataJson);

    final JsonNode result = SchemaCoercion.coerce(data, schema);

    assertEquals("value", result.get("field2").asText());
    assertEquals(null, result.get("field1"));
  }

  @Test
  void testCoerceArrayWithoutItemsSchema() {
    final String schemaJson = """
                              {
                                "type": "object",
                                "properties": {
                                  "field": {
                                    "type": "array"
                                  }
                                }
                              }
                              """;

    final String dataJson = """
                            {
                              "field": {
                                "value": "test"
                              }
                            }
                            """;

    final JsonNode schema = Jsons.deserialize(schemaJson);
    final JsonNode data = Jsons.deserialize(dataJson);

    final JsonNode result = SchemaCoercion.coerce(data, schema);

    assertTrue(result.get("field").isArray());
    assertEquals(1, result.get("field").size());
    assertEquals("test", result.get("field").get(0).get("value").asText());
  }

}
