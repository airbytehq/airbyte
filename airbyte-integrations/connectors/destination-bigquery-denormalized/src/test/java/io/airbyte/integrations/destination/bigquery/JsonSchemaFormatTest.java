/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class JsonSchemaFormatTest {

  @Test
  void fromJsonSchemaFormat_matchByFormatAndType() {
    JsonSchemaFormat result = JsonSchemaFormat.fromJsonSchemaFormat("date-time", "timestamp_with_timezone");
    assertEquals(JsonSchemaFormat.DATETIME_WITH_TZ, result);
  }

  @Test
  void fromJsonSchemaFormat_matchByFormat() {
    JsonSchemaFormat result = JsonSchemaFormat.fromJsonSchemaFormat("date", null);
    assertEquals(JsonSchemaFormat.DATE, result);
  }

  @Test
  void fromJsonSchemaFormat_notExistingFormat() {
    JsonSchemaFormat result = JsonSchemaFormat.fromJsonSchemaFormat("not_existing_format", null);
    assertNull(result);
  }

}
