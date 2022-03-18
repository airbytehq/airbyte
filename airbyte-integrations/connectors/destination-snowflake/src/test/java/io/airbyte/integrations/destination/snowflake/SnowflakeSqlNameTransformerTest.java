/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class SnowflakeSqlNameTransformerTest {

  private static final SnowflakeSQLNameTransformer INSTANCE = new SnowflakeSQLNameTransformer();

  @Test
  public void testGetIdentifier() {
    assertEquals("name_space", INSTANCE.getIdentifier("name-space"));
    assertEquals("special_character", INSTANCE.getIdentifier("spécial_character"));
    assertEquals("_99namespace", INSTANCE.getIdentifier("99namespace"));
  }

}
