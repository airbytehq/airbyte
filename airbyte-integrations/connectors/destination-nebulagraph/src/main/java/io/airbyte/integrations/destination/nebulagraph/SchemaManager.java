/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.nebulagraph;

import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

public final class SchemaManager {

  private final NebulaGraphClient client;
  private final StatementBuilder sb;

  // Known column cache, to avoid duplicate ALTER (in-process cache is enough)
  private final Map<String, Map<String, ColumnType>> knownTagCols = new ConcurrentHashMap<>();
  private final Map<String, Map<String, ColumnType>> knownEdgeCols = new ConcurrentHashMap<>();

  public SchemaManager(NebulaGraphClient client, StatementBuilder sb) {
    this.client = client;
    this.sb = sb;
  }

  public void ensureTagExists(String tagName) {
    // CREATE TAG IF NOT EXISTS `tag`(`_airbyte_data` string, `_airbyte_ab_id` string,
    // `_airbyte_emitted_at` int, `_airbyte_loaded_at` int)
    String sql = "CREATE TAG IF NOT EXISTS " + sb.q(tagName)
        + "(`_airbyte_data` string, `_airbyte_ab_id` string, `_airbyte_emitted_at` int64, `_airbyte_loaded_at` int64)";
    try {
      client.execute(sql);
      // Seed raw four columns to cache
      seedKnownTagCols(tagName, Set.of("_airbyte_data", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_loaded_at"));
    } catch (Exception e) {
      throw new RuntimeException("ensureTagExists failed: " + tagName, e);
    }
  }

  public void ensureEdgeTypeExists(String edgeType) {
    // CREATE EDGE IF NOT EXISTS `edge_type`(`_airbyte_data` string, `_airbyte_ab_id` string,
    // `_airbyte_emitted_at` int, `_airbyte_loaded_at` int)
    String sql = "CREATE EDGE IF NOT EXISTS " + sb.q(edgeType)
        + "(`_airbyte_data` string, `_airbyte_ab_id` string, `_airbyte_emitted_at` int64, `_airbyte_loaded_at` int64)";
    try {
      client.execute(sql);
      seedKnownEdgeCols(edgeType, Set.of("_airbyte_data", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_loaded_at"));
    } catch (Exception e) {
      throw new RuntimeException("ensureEdgeTypeExists failed: " + edgeType, e);
    }
  }

  // Seed known column cache - Tag
  public void seedKnownTagCols(String tagName, Collection<String> cols) {
    if (tagName == null || cols == null || cols.isEmpty())
      return;
    Map<String, ColumnType> map = knownTagCols.computeIfAbsent(tagName, k -> new LinkedHashMap<>());
    for (String col : cols) {
      if (col != null) {
        ColumnType type = ("_airbyte_emitted_at".equals(col) || "_airbyte_loaded_at".equals(col))
            ? ColumnType.INT
            : ColumnType.STRING;
        map.putIfAbsent(col, type);
      }
    }
  }

  // Seed known column cache - Edge (with type)
  public void seedKnownEdgeCols(String edgeType, Collection<String> cols) {
    if (edgeType == null || cols == null || cols.isEmpty())
      return;
    Map<String, ColumnType> map = knownEdgeCols.computeIfAbsent(edgeType, k -> new LinkedHashMap<>());
    for (String col : cols) {
      if (col != null) {
        ColumnType type = ("_airbyte_emitted_at".equals(col) || "_airbyte_loaded_at".equals(col))
            ? ColumnType.INT
            : ColumnType.STRING;
        map.putIfAbsent(col, type);
      }
    }
  }

  public void addTagColumnsIfMissing(String tagName, Map<String, Class<?>> newCols) {
    if (newCols == null || newCols.isEmpty())
      return;
    Map<String, ColumnType> known = knownTagCols.computeIfAbsent(tagName, k -> new LinkedHashMap<>());
    // First collect columns to add/promote types, try to batch ADD for efficiency
    LinkedHashMap<String, ColumnType> toAdd = new LinkedHashMap<>();
    for (Map.Entry<String, Class<?>> entry : newCols.entrySet()) {
      String col = entry.getKey();
      if (col == null || col.isEmpty())
        continue;
      ColumnType desiredType = ColumnType.fromJavaClass(entry.getValue());
      ColumnType current = known.get(col);
      if (current != null && current.covers(desiredType))
        continue;
      ColumnType toApply = current == null ? desiredType : ColumnType.promote(current, desiredType);
      toAdd.put(col, toApply);
    }
    if (toAdd.isEmpty())
      return;

    // Try batch ADD: ALTER TAG t ADD (`c1` type1,`c2` type2)
    StringBuilder sbCols = new StringBuilder();
    boolean first = true;
    for (Map.Entry<String, ColumnType> e : toAdd.entrySet()) {
      if (!first)
        sbCols.append(",");
      sbCols.append(sb.q(e.getKey())).append(" ").append(e.getValue().ngqlType);
      first = false;
    }
    String batchSql = "ALTER TAG " + sb.q(tagName) + " ADD (" + sbCols + ")";
    try {
      client.execute(batchSql);
      for (Map.Entry<String, ColumnType> e : toAdd.entrySet()) {
        known.put(e.getKey(), e.getValue());
      }
      return;
    } catch (Exception batchErr) {
      // If the batch statement fails because of some columns already exist, fall back to per-column ADD
      // (with parentheses), and ignore the already exists error
      if (!isAlreadyExists(batchErr)) {
        // Non-already exists error directly throw
        throw new RuntimeException("addTagColumnsIfMissing batch failed: " + tagName, batchErr);
      }
    }

    // Per-column ADD with parentheses: ALTER TAG t ADD (`c` type)
    for (Map.Entry<String, ColumnType> e : toAdd.entrySet()) {
      String sql = "ALTER TAG " + sb.q(tagName) + " ADD (" + sb.q(e.getKey()) + " " + e.getValue().ngqlType + ")";
      try {
        client.execute(sql);
        known.put(e.getKey(), e.getValue());
      } catch (Exception ex) {
        if (isAlreadyExists(ex)) {
          known.put(e.getKey(), e.getValue());
        } else {
          throw new RuntimeException("addTagColumnsIfMissing failed: " + tagName + "." + e.getKey(), ex);
        }
      }
    }
  }

  /**
   * Lazy add Edge columns (type mapping: STRING/BOOL/DOUBLE/INT). Only execute ALTER for columns that
   * do not exist or need to be promoted in the cache; both successful and already exist are merged
   * into the cache.
   */
  public void addEdgeColumnsIfMissing(String edgeType, Map<String, Class<?>> newCols) {
    if (newCols == null || newCols.isEmpty())
      return;
    Map<String, ColumnType> known = knownEdgeCols.computeIfAbsent(edgeType, k -> new LinkedHashMap<>());
    LinkedHashMap<String, ColumnType> toAdd = new LinkedHashMap<>();
    for (Map.Entry<String, Class<?>> entry : newCols.entrySet()) {
      String col = entry.getKey();
      if (col == null || col.isEmpty())
        continue;
      ColumnType desired = ColumnType.fromJavaClass(entry.getValue());
      ColumnType current = known.get(col);
      if (current != null && current.covers(desired))
        continue;
      ColumnType toApply = current == null ? desired : ColumnType.promote(current, desired);
      toAdd.put(col, toApply);
    }
    if (toAdd.isEmpty())
      return;

    // Batch ADD: ALTER EDGE e ADD (`c1` type1,`c2` type2)
    StringBuilder sbCols = new StringBuilder();
    boolean first = true;
    for (Map.Entry<String, ColumnType> e : toAdd.entrySet()) {
      if (!first)
        sbCols.append(",");
      sbCols.append(sb.q(e.getKey())).append(" ").append(e.getValue().ngqlType);
      first = false;
    }
    String batchSql = "ALTER EDGE " + sb.q(edgeType) + " ADD (" + sbCols + ")";
    try {
      client.execute(batchSql);
      for (Map.Entry<String, ColumnType> e : toAdd.entrySet()) {
        known.put(e.getKey(), e.getValue());
      }
      return;
    } catch (Exception batchErr) {
      if (!isAlreadyExists(batchErr)) {
        throw new RuntimeException("addEdgeColumnsIfMissing batch failed: " + edgeType, batchErr);
      }
    }

    // Per-column ADD
    for (Map.Entry<String, ColumnType> e : toAdd.entrySet()) {
      String sql = "ALTER EDGE " + sb.q(edgeType) + " ADD (" + sb.q(e.getKey()) + " " + e.getValue().ngqlType + ")";
      try {
        client.execute(sql);
        known.put(e.getKey(), e.getValue());
      } catch (Exception ex) {
        if (isAlreadyExists(ex)) {
          known.put(e.getKey(), e.getValue());
        } else {
          throw new RuntimeException("addEdgeColumnsIfMissing failed: " + edgeType + "." + e.getKey(), ex);
        }
      }
    }
  }

  // Internal: Edge column type mapping is directly maintained by knownEdgeCols

  private boolean isAlreadyExists(Exception e) {
    String msg = String.valueOf(e.getMessage()).toLowerCase();
    return msg.contains("exist") || msg.contains("already");
  }

  enum ColumnType {

    STRING("string"),
    BOOL("bool"),
    DOUBLE("double"),
    INT("int64");

    final String ngqlType;

    ColumnType(String ngqlType) {
      this.ngqlType = ngqlType;
    }

    static ColumnType fromJavaClass(Class<?> clazz) {
      if (clazz == null) {
        return STRING;
      }
      if (Boolean.class.equals(clazz)) {
        return BOOL;
      }
      if (Number.class.isAssignableFrom(clazz)) {
        if (Double.class.equals(clazz) || Float.class.equals(clazz)) {
          return DOUBLE;
        }
        return INT;
      }
      return STRING;
    }

    boolean covers(ColumnType other) {
      return this == other;
    }

    static ColumnType promote(ColumnType existing, ColumnType incoming) {
      if (existing == STRING || incoming == STRING) {
        return STRING;
      }
      if (existing == DOUBLE || incoming == DOUBLE) {
        return DOUBLE;
      }
      if (existing == INT || incoming == INT) {
        return INT;
      }
      return BOOL;
    }

  }

}
