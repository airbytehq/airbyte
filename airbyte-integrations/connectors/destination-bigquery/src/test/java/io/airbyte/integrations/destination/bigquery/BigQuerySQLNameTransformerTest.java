/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static org.junit.jupiter.api.Assertions.*;

import java.util.Map;
import org.junit.jupiter.api.Test;

class BigQuerySQLNameTransformerTest {

  private static final BigQuerySQLNameTransformer INSTANCE = new BigQuerySQLNameTransformer();
  private static final Map<String, String> RAW_TO_NORMALIZED_IDENTIFIERS = Map.of(
      "name-space", "name_space",
      "spécial_character", "special_character",
      "99namespace", "_99namespace",
      "*_namespace", "__namespace",
      "_namespace", "_namespace");

  private static final Map<String, String> RAW_TO_NORMALIZED_NAMESPACES = Map.of(
      "name-space", "name_space",
      "spécial_character", "special_character",
      // dataset name is allowed to start with a number
      "99namespace", "99namespace",
      // dataset name starting with an underscore is hidden, so we prepend a letter
      "*_namespace", "n__namespace",
      "_namespace", "n_namespace");

  @Test
  public void testGetIdentifier() {
    RAW_TO_NORMALIZED_IDENTIFIERS.forEach((raw, normalized) -> {
      assertEquals(normalized, INSTANCE.getIdentifier(raw));
      assertEquals(normalized, INSTANCE.convertStreamName(raw));
    });
  }

  @Test
  public void testGetNamespace() {
    RAW_TO_NORMALIZED_NAMESPACES.forEach((raw, normalized) -> {
      assertEquals(normalized, INSTANCE.getNamespace(raw));
    });
  }

}
