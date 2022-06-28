/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

import java.util.Map;
import org.junit.jupiter.api.Test;

class SnowflakeSqlNameTransformerTest {

  private static final SnowflakeSQLNameTransformer INSTANCE = new SnowflakeSQLNameTransformer();
  private static final Map<String, String> RAW_TO_NORMALIZED_IDENTIFIERS = Map.of(
      "name-space", "name_space",
      "spécial_character", "special_character",
      "99namespace", "_99namespace");

  @Test
  public void testGetIdentifier() {
    assertNull(INSTANCE.getIdentifier(null));
    assertNull(INSTANCE.convertStreamName(null));
    RAW_TO_NORMALIZED_IDENTIFIERS.forEach((raw, normalized) -> {
      assertEquals(normalized, INSTANCE.convertStreamName(raw));
      assertEquals(normalized, INSTANCE.getIdentifier(raw));
      assertEquals(normalized, INSTANCE.getNamespace(raw));
    });
  }

}
