/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.nebulagraph;

import java.util.List;
import java.util.Map;

/**
 * Build VID from fields using a separator. Fail-fast on missing/null.
 */
public final class VidGenerator {

  public String buildVid(Map<String, Object> record, List<String> fields, String sep, int maxLen) {
    if (record == null)
      throw new IllegalArgumentException("record is null");
    if (fields == null || fields.isEmpty())
      throw new IllegalArgumentException("vid fields empty");
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < fields.size(); i++) {
      String f = fields.get(i);
      Object v = record.get(f);
      if (v == null)
        throw new IllegalArgumentException("vid field is null: " + f);
      if (i > 0)
        sb.append(sep);
      sb.append(String.valueOf(v));
    }
    if (sb.length() > maxLen) {
      throw new IllegalArgumentException("VID length exceeds FIXED_STRING(" + maxLen + ")");
    }
    return sb.toString();
  }

}
