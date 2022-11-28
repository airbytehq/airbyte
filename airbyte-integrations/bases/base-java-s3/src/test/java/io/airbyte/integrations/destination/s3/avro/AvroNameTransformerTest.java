/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.avro;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

import java.util.Map;
import org.junit.jupiter.api.Test;

class AvroNameTransformerTest {

  private static final AvroNameTransformer INSTANCE = new AvroNameTransformer();
  private static final Map<String, String> RAW_TO_NORMALIZED_IDENTIFIERS = Map.of(
      "name-space", "name_space",
      "spécial_character", "special_character",
      "99namespace", "_99namespace");

  private static final Map<String, String> RAW_TO_NORMALIZED_NAMESPACES = Map.of(
      "", "",
      "name-space1.name-space2.namespace3", "name_space1.name_space2.namespace3",
      "namespace1.spécial_character", "namespace1.special_character",
      "99namespace.namespace2", "_99namespace.namespace2");

  @Test
  public void testGetIdentifier() {
    assertNull(INSTANCE.getIdentifier(null));
    assertNull(INSTANCE.convertStreamName(null));
    RAW_TO_NORMALIZED_IDENTIFIERS.forEach((raw, normalized) -> {
      assertEquals(normalized, INSTANCE.getIdentifier(raw));
      assertEquals(normalized, INSTANCE.convertStreamName(raw));
    });
  }

  @Test
  public void testGetNamespace() {
    assertNull(INSTANCE.getNamespace(null));
    RAW_TO_NORMALIZED_NAMESPACES.forEach((raw, normalized) -> {
      assertEquals(normalized, INSTANCE.getNamespace(raw));
    });
  }

}
