/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

class JsonSchemaTypeTest {

  @Test
  void fromJsonSchemaType_notPresent() {
    assertThrows(IllegalArgumentException.class, () -> JsonSchemaType.fromJsonSchemaType("not_existing_value"));
  }

  @Test
  void fromJsonSchemaType_getType() {
    JsonSchemaType result = JsonSchemaType.fromJsonSchemaType("string");
    assertEquals(JsonSchemaType.STRING, result);
  }

}
