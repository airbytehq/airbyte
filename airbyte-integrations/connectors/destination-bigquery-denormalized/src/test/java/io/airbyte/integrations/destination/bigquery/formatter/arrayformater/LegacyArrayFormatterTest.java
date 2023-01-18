/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter.arrayformater;

import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getExpectedSchemaArraysLegacy;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getSchemaArrays;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import org.junit.jupiter.api.Test;

public class LegacyArrayFormatterTest {

  private final LegacyArrayFormatter formatter = new LegacyArrayFormatter();
  private final ObjectMapper mapper = new ObjectMapper();

  @Test
  void surroundArraysByObjects() {
    final JsonNode schemaArrays = getSchemaArrays();
    final JsonNode expectedSchemaArrays = getExpectedSchemaArraysLegacy();

    formatter.surroundArraysByObjects(schemaArrays);
    assertEquals(expectedSchemaArrays, schemaArrays);
  }

  @Test
  void findArrays() throws JsonProcessingException {
    final JsonNode schemaArrays = getSchemaArrays();
    final List<JsonNode> expectedResult = List.of(
        mapper.readTree("""
                        {"type":["array"],"items":{"type":"integer"}}"""),
        mapper.readTree("""
                        {"type":["array"],"items":{"type":["array"],"items":{"type":"integer"}}}"""),
        mapper.readTree("""
                        {"type":["array"],"items":{"type":"integer"}}"""),
        mapper.readTree("""
                        {"type":["array"],"items":{"type":["array"],"items":{"type":["array"],"items":{"type":"integer"}}}}"""),
        mapper.readTree("""
                        {"type":["array"],"items":{"type":["array"],"items":{"type":"integer"}}}"""),
        mapper.readTree("""
                        {"type":["array"],"items":{"type":"integer"}}"""),
        mapper.readTree(
            """
            {"type":["array"],"items":{"type":["array"],"items":{"type":["array"],"items":{"type":["array"],"items":{"type":"integer"}}}}}"""),
        mapper.readTree("""
                        {"type":["array"],"items":{"type":["array"],"items":{"type":["array"],"items":{"type":"integer"}}}}"""),
        mapper.readTree("""
                        {"type":["array"],"items":{"type":["array"],"items":{"type":"integer"}}}"""),
        mapper.readTree("""
                        {"type":["array"],"items":{"type":"integer"}}"""));

    final List<JsonNode> result = formatter.findArrays(schemaArrays);

    assertEquals(expectedResult, result);
  }

  @Test
  void findArrays_null() {
    final List<JsonNode> result = formatter.findArrays(null);
    assertTrue(result.isEmpty());
  }

  @Test
  void formatArrayItems() throws JsonProcessingException {
    final JsonNode expectedArrayNode = mapper.readTree(
        """
          {"big_query_array": [["one", "two"], ["one", "two"]]}
        """);
    final List<JsonNode> arrayNodes = List.of(
        mapper.readTree("""
                        ["one", "two"]"""),
        mapper.readTree("""
                        ["one", "two"]"""));

    final JsonNode result = formatter.formatArrayItems(arrayNodes);

    assertEquals(expectedArrayNode, result);
  }

}
