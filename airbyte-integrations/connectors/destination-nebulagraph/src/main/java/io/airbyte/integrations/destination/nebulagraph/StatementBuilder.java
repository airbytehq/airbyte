/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.nebulagraph;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Identifier and literal escaping + small helpers.
 */
public final class StatementBuilder {

  public String q(String ident) {
    if (ident == null)
      throw new IllegalArgumentException("ident is null");
    String escaped = ident.replace("`", "``");
    return "`" + escaped + "`";
  }

  public String qs(String literal) {
    if (literal == null)
      return "NULL";
    String s = literal
        .replace("\\", "\\\\")
        .replace("\"", "\\\"")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t");
    return '"' + s + '"';
  }

  public String joinCols(List<String> cols) {
    return cols.stream().map(this::q).collect(Collectors.joining(","));
  }

  // Generic raw+typed batch INSERT (provided by caller with column headers and aligned value strings)
  public String buildInsertVertexValues(String tag, List<String> cols, List<String> vidAndValueTuples) {
    if (tag == null || tag.isEmpty())
      throw new IllegalArgumentException("tag empty");
    if (cols == null || cols.isEmpty())
      throw new IllegalArgumentException("cols empty");
    if (vidAndValueTuples == null || vidAndValueTuples.isEmpty())
      throw new IllegalArgumentException("rows empty");
    StringBuilder sql = new StringBuilder();
    // Add a space between tag identifier and column list to align with Nebula examples: INSERT VERTEX
    // tag (col,...)
    sql.append("INSERT VERTEX ").append(q(tag)).append(" (").append(joinCols(cols)).append(")\nVALUES\n");
    sql.append(String.join(",\n  ", vidAndValueTuples)).append(";");
    return sql.toString();
  }

  // Generic raw+typed batch INSERT EDGE (provided by caller with column headers and aligned value
  // strings)
  public String buildInsertEdgeValues(String edgeType, List<String> cols, List<String> endpointsAndValueTuples) {
    if (edgeType == null || edgeType.isEmpty())
      throw new IllegalArgumentException("edgeType empty");
    if (cols == null || cols.isEmpty())
      throw new IllegalArgumentException("cols empty");
    if (endpointsAndValueTuples == null || endpointsAndValueTuples.isEmpty())
      throw new IllegalArgumentException("rows empty");
    StringBuilder sql = new StringBuilder();
    // Add a space between edge type and column list for consistency with Nebula syntax
    sql.append("INSERT EDGE ").append(q(edgeType)).append(" (").append(joinCols(cols)).append(")\nVALUES\n");
    sql.append(String.join(",\n  ", endpointsAndValueTuples)).append(";");
    return sql.toString();
  }

  // Vertex row-level UPSERT
  public String buildUpsertVertex(String tag, String vid, List<String> cols, List<Object> values) {
    if (tag == null || tag.isEmpty())
      throw new IllegalArgumentException("tag empty");
    if (vid == null)
      throw new IllegalArgumentException("vid is null");
    if (cols == null || values == null || cols.size() != values.size()) {
      throw new IllegalArgumentException("cols/values size mismatch");
    }
    StringBuilder set = new StringBuilder();
    for (int i = 0; i < cols.size(); i++) {
      if (i > 0)
        set.append(",");
      set.append(q(cols.get(i))).append("=").append(formatValue(values.get(i)));
    }
    StringBuilder sql = new StringBuilder();
    sql.append("UPSERT VERTEX ON ").append(q(tag)).append(" ").append(qs(vid)).append("\nSET ").append(set).append(";");
    return sql.toString();
  }

  // Edge row-level UPSERT
  public String buildUpsertEdge(String edgeType, String src, String dst, long rank, List<String> cols, List<Object> values) {
    if (edgeType == null || edgeType.isEmpty())
      throw new IllegalArgumentException("edgeType empty");
    if (src == null || dst == null)
      throw new IllegalArgumentException("src/dst is null");
    if (cols == null || values == null || cols.size() != values.size()) {
      throw new IllegalArgumentException("cols/values size mismatch");
    }
    StringBuilder set = new StringBuilder();
    for (int i = 0; i < cols.size(); i++) {
      if (i > 0)
        set.append(",");
      set.append(q(cols.get(i))).append("=").append(formatValue(values.get(i)));
    }
    StringBuilder sql = new StringBuilder();
    sql.append("UPSERT EDGE ON ").append(q(edgeType)).append(" ")
        .append(qs(src)).append("->").append(qs(dst)).append("@").append(rank)
        .append("\nSET ").append(set).append(";");
    return sql.toString();
  }

  // Format a row object value as a values list (in column order), and return the vid:"(v1,v2,...)"
  // fragment
  public String formatVidAndValues(String vid, List<Object> values) {
    if (vid == null)
      throw new IllegalArgumentException("vid is null");
    List<String> vs = new ArrayList<>(values.size());
    for (Object v : values) {
      vs.add(formatValue(v));
    }
    return qs(vid) + ":(" + String.join(",", vs) + ")";
  }

  // Format a row object value as a values list, and return the "src"->"dst"@rank:(v1,v2,...) fragment
  public String formatEdgeEndpointsAndValues(String src, String dst, long rank, List<Object> values) {
    if (src == null)
      throw new IllegalArgumentException("src is null");
    if (dst == null)
      throw new IllegalArgumentException("dst is null");
    List<String> vs = new ArrayList<>(values.size());
    for (Object v : values) {
      vs.add(formatValue(v));
    }
    return qs(src) + "->" + qs(dst) + "@" + rank + ":(" + String.join(",", vs) + ")";
  }

  private String formatValue(Object v) {
    if (v == null)
      return "NULL";
    if (v instanceof Boolean)
      return ((Boolean) v) ? "true" : "false";
    if (v instanceof Number)
      return v.toString();
    // Other strings are escaped
    return qs(String.valueOf(v));
  }

}
