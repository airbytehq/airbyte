/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter.util;

import static io.airbyte.integrations.destination.bigquery.formatter.util.FormatterUtil.TYPE_FIELD;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;

class FormatterUtilTest {

  private final ObjectMapper mapper = new ObjectMapper();

  @Test
  void isAirbyteArray_typeIsNull() {
    JsonNode arrayNode = mapper.createArrayNode().add("one").add("two");
    boolean result = FormatterUtil.isAirbyteArray(arrayNode);
    assertFalse(result);
  }

  @Test
  void isAirbyteArray_typeFieldIsArray() {
    JsonNode arrayNode = mapper.createArrayNode().add("array");
    JsonNode typeNode = mapper.createObjectNode().set(TYPE_FIELD, arrayNode);
    boolean result = FormatterUtil.isAirbyteArray(typeNode);
    assertTrue(result);
  }

  @Test
  void isAirbyteArray_typeFieldIsNotArray() {
    JsonNode objectNode = mapper.createObjectNode().put("name", "array");
    JsonNode typeNode = mapper.createObjectNode().set(TYPE_FIELD, objectNode);
    boolean result = FormatterUtil.isAirbyteArray(typeNode);
    assertFalse(result);
  }

  @Test
  void isAirbyteArray_textIsNotArray() {
    JsonNode arrayNode = mapper.createArrayNode().add("notArrayText");
    JsonNode typeNode = mapper.createObjectNode().set(TYPE_FIELD, arrayNode);
    boolean result = FormatterUtil.isAirbyteArray(typeNode);
    assertFalse(result);
  }

}
