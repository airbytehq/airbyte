/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter.util;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;

class FormatterUtilTest {

  private final ObjectMapper mapper = new ObjectMapper();

  @Test
  void isAirbyteArray_typeIsNull() throws JsonProcessingException {
    final JsonNode arrayNode = mapper.readTree(
        """
        ["one", "two"]""");

    final boolean result = FormatterUtil.isAirbyteArray(arrayNode);
    assertFalse(result);
  }

  @Test
  void isAirbyteArray_typeFieldIsArray() throws JsonProcessingException {
    final JsonNode arrayNode = mapper.readTree("""
                                               {"type":["array"],"items":{"type":"integer"}}""");

    boolean result = FormatterUtil.isAirbyteArray(arrayNode);
    assertTrue(result);
  }

  @Test
  void isAirbyteArray_typeFieldIsNotArray() throws JsonProcessingException {
    final JsonNode objectNode = mapper.readTree("""
                                                {"type":"object"}""");
    final boolean result = FormatterUtil.isAirbyteArray(objectNode);
    assertFalse(result);
  }

  @Test
  void isAirbyteArray_textIsNotArray() throws JsonProcessingException {
    final JsonNode arrayNode = mapper.readTree("""
                                               {"type":["notArrayText"]}""");
    final boolean result = FormatterUtil.isAirbyteArray(arrayNode);
    assertFalse(result);
  }

}
