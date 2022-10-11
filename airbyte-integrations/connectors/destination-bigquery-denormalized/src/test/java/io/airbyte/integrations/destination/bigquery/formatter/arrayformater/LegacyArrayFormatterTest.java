/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter.arrayformater;

import static io.airbyte.integrations.destination.bigquery.formatter.util.FormatterUtil.NESTED_ARRAY_FIELD;
import static io.airbyte.integrations.destination.bigquery.formatter.util.FormatterUtil.TYPE_FIELD;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getExpectedSchemaArraysLegacy;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getSchemaArrays;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.JsonNodeType;
import java.util.List;
import org.junit.jupiter.api.Test;

public class LegacyArrayFormatterTest {

  private final LegacyArrayFormatter formatter = new LegacyArrayFormatter();

  @Test
  void surroundArraysByObjects() {
    JsonNode schemaArrays = getSchemaArrays();
    JsonNode expectedSchemaArrays = getExpectedSchemaArraysLegacy();

    formatter.surroundArraysByObjects(schemaArrays);
    assertEquals(expectedSchemaArrays, schemaArrays);
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

  @Test
  void formatArrayItems() {
    ObjectMapper mapper = new ObjectMapper();
    JsonNode arrayFirst = mapper.createArrayNode().add("one").add("two");
    JsonNode arraySecond = mapper.createArrayNode().add("one").add("two");
    List<JsonNode> arrayItems = List.of(arrayFirst, arraySecond);

    JsonNode result = formatter.formatArrayItems(arrayItems);

    assertNotNull(result);
    assertTrue(result.hasNonNull(NESTED_ARRAY_FIELD));
    assertTrue(result.get(NESTED_ARRAY_FIELD).isArray());
    assertEquals(2, result.get(NESTED_ARRAY_FIELD).size());
  }

}
