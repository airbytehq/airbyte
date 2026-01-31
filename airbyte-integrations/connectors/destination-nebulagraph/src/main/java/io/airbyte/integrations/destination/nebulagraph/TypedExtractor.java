/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.nebulagraph;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Extract top-level primitive fields into typed map. Only STRING/INT/DOUBLE/BOOL like primitives,
 * others -> NULL (or omitted; here we omit and let writer map absent to NULL).
 */
public final class TypedExtractor {

  public Map<String, Object> extractTopLevelTyped(Map<String, Object> top) {
    Map<String, Object> out = new LinkedHashMap<>();
    if (top == null)
      return out;
    for (Map.Entry<String, Object> e : top.entrySet()) {
      Object v = e.getValue();
      if (isPrimitive(v)) {
        out.put(e.getKey(), normalizeNumber(v));
      }
    }
    return out;
  }

  public static boolean isPrimitive(Object v) {
    if (v == null)
      return true; // treat null as acceptable -> becomes NULL
    return v instanceof String || v instanceof Boolean || v instanceof Number;
  }

  private Object normalizeNumber(Object v) {
    if (!(v instanceof Number))
      return v;
    if (v instanceof Float || v instanceof Double)
      return ((Number) v).doubleValue();
    return ((Number) v).longValue();
  }

}
