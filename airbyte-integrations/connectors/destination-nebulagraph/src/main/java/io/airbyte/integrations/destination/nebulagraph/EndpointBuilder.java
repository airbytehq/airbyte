/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.nebulagraph;

import java.util.List;
import java.util.Map;

public final class EndpointBuilder {

  public String buildSrc(Map<String, Object> record, List<String> fields, String sep, int maxLen) {
    return build(record, fields, sep, maxLen, "src");
  }

  public String buildDst(Map<String, Object> record, List<String> fields, String sep, int maxLen) {
    return build(record, fields, sep, maxLen, "dst");
  }

  public long buildRank(Map<String, Object> record, String rankField) {
    if (rankField == null || rankField.isEmpty())
      return 0L;
    Object v = record.get(rankField);
    if (v == null)
      return 0L;
    if (v instanceof Number)
      return ((Number) v).longValue();
    try {
      return Long.parseLong(String.valueOf(v));
    } catch (Exception e) {
      return 0L;
    }
  }

  private String build(Map<String, Object> record, List<String> fields, String sep, int maxLen, String kind) {
    if (record == null)
      throw new IllegalArgumentException(kind + " record is null");
    if (fields == null || fields.isEmpty())
      throw new IllegalArgumentException(kind + " fields empty");
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < fields.size(); i++) {
      String f = fields.get(i);
      Object v = record.get(f);
      if (v == null)
        throw new IllegalArgumentException(kind + " field is null: " + f);
      if (i > 0)
        sb.append(sep);
      sb.append(String.valueOf(v));
    }
    if (sb.length() > maxLen) {
      throw new IllegalArgumentException((kind.equals("src") ? "SRC" : "DST") + " length exceeds FIXED_STRING(" + maxLen + ")");
    }
    return sb.toString();
  }

}
