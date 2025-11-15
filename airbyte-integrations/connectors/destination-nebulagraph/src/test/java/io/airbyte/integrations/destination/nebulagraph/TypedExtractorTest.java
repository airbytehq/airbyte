/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.nebulagraph;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("TypedExtractor")
class TypedExtractorTest {

  @Test
  void extractTopLevelPrimitives() {
    TypedExtractor te = new TypedExtractor();
    Map<String, Object> top = new HashMap<>();
    top.put("s", "str");
    top.put("b", true);
    top.put("i", 10);
    top.put("d", 1.5);
    top.put("n", null);
    top.put("obj", Map.of("x", 1));
    top.put("arr", new int[] {1, 2});

    Map<String, Object> out = te.extractTopLevelTyped(top);

    // objects/arrays should be ignored; others preserved (numbers normalized below)
    // size should be 5: s, b, i, d, n
    assertEquals(5, out.size());
  }

  @Test
  void normalizeNumbers() {
    TypedExtractor te = new TypedExtractor();
    Map<String, Object> top = new HashMap<>();
    top.put("i", 10); // Integer -> long
    top.put("l", 10L); // Long -> long
    top.put("f", 1.2f); // Float -> double
    top.put("d", 2.5d); // Double -> double

    Map<String, Object> out = te.extractTopLevelTyped(top);

    assertEquals(10L, out.get("i"));
    assertEquals(10L, out.get("l"));
    assertEquals(1.2d, (double) out.get("f"), 0.0000001);
    assertEquals(2.5d, (double) out.get("d"), 0.0000001);
  }

}
