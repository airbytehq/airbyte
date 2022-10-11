/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter.arrayformater;

import static io.airbyte.integrations.destination.bigquery.formatter.util.FormatterUtil.NESTED_ARRAY_FIELD;
import static io.airbyte.integrations.destination.bigquery.formatter.util.FormatterUtil.TYPE_FIELD;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getExpectedSchemaArrays;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getSchemaArrays;
import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.JsonNodeType;
import java.util.List;
import org.junit.jupiter.api.Test;

class DefaultArrayFormatterTest {

  private final DefaultArrayFormatter formatter = new DefaultArrayFormatter();
  private final ObjectMapper mapper = new ObjectMapper();

  @Test
  void surroundArraysByObjects() {
    JsonNode schemaArrays = getSchemaArrays();
    JsonNode expectedSchemaArrays = getExpectedSchemaArrays();
    formatter.surroundArraysByObjects(schemaArrays);
    assertEquals(expectedSchemaArrays, schemaArrays);
  }

  @Test
  void formatArrayItems() {
    JsonNode arrayFirst = mapper.createArrayNode().add("one").add("two");
    JsonNode arraySecond = mapper.createArrayNode().add("one").add("two");
    List<JsonNode> arrayItems = List.of(arrayFirst, arraySecond);

    JsonNode result = formatter.formatArrayItems(arrayItems);

    assertNotNull(result);
    assertTrue(result.isArray());
    assertEquals(2, result.size());
    assertTrue(result.get(0).hasNonNull(NESTED_ARRAY_FIELD));
    assertTrue(result.get(1).hasNonNull(NESTED_ARRAY_FIELD));
    assertTrue(result.get(0).get(NESTED_ARRAY_FIELD).isArray());
    assertTrue(result.get(1).get(NESTED_ARRAY_FIELD).isArray());
  }

  @Test
  void formatArrayItems_notArray() {
    JsonNode objectNode = mapper.createObjectNode().put("name", "value");

    JsonNode result = formatter.formatArrayItems(List.of(objectNode));

    assertNotNull(result);
    assertEquals(objectNode, result.get(0));
  }

  @Test
  void findArrays() {
    JsonNode schemaArrays = getSchemaArrays();

    List<JsonNode> result = formatter.findArrays(schemaArrays);

    assertNotNull(result);
    assertFalse(result.isEmpty());
    assertEquals(10, result.size());
    result.forEach(node -> {
      assertTrue(node.has(TYPE_FIELD));
      assertEquals(JsonNodeType.ARRAY, node.get(TYPE_FIELD).getNodeType());
    });
  }

  @Test
  void findArrays_null() {
    List<JsonNode> result = formatter.findArrays(null);
    assertTrue(result.isEmpty());
  }

}
