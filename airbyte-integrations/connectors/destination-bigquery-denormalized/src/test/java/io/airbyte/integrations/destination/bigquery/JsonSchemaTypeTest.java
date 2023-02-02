/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class JsonSchemaTypeTest {

  @Test
  void fromJsonSchemaType_notPresent() {
    JsonSchemaType result = JsonSchemaType.fromJsonSchemaType("test_field_name", "not_existing_type");
    assertEquals(JsonSchemaType.STRING, result);
  }

  @Test
  void fromJsonSchemaType_getType() {
    JsonSchemaType result = JsonSchemaType.fromJsonSchemaType("test_field_name", "WellKnownTypes.json#/definitions/String");
    assertEquals(JsonSchemaType.STRING, result);
  }

}
