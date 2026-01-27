/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.clickhouse;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcConstants;
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations;
import java.sql.JDBCType;
import java.sql.Types;

/**
 * Custom source operations for ClickHouse that handles type mapping differences
 * in newer JDBC driver versions (0.6.x+).
 *
 * The ClickHouse JDBC driver 0.6.x+ returns JDBCType.OTHER for many ClickHouse-specific
 * types that don't have exact JDBC equivalents (e.g., UInt64, Int128). This class
 * maps those types to appropriate standard JDBC types based on the column type name,
 * ensuring cursor type validation works correctly for incremental syncs.
 */
public class ClickHouseSourceOperations extends JdbcSourceOperations {

  @Override
  public JDBCType getDatabaseFieldType(final JsonNode field) {
    final int columnType = field.get(JdbcConstants.INTERNAL_COLUMN_TYPE).asInt();

    // If the driver returns OTHER, look at the type name and map it appropriately
    if (columnType == Types.OTHER) {
      final String typeName = field.get(JdbcConstants.INTERNAL_COLUMN_TYPE_NAME).asText().toLowerCase();
      return mapClickHouseTypeToJdbcType(typeName);
    }

    // For standard JDBC types, use the parent implementation
    return super.getDatabaseFieldType(field);
  }

  /**
   * Maps ClickHouse-specific type names to standard JDBC types.
   * This ensures that columns with ClickHouse types can be used as cursors
   * for incremental sync.
   */
  private JDBCType mapClickHouseTypeToJdbcType(final String typeName) {
    // Integer types
    if (typeName.startsWith("int8") || typeName.startsWith("int16")) {
      return JDBCType.SMALLINT;
    }
    if (typeName.startsWith("int32") || typeName.startsWith("uint8") || typeName.startsWith("uint16")) {
      return JDBCType.INTEGER;
    }
    if (typeName.startsWith("int64") || typeName.startsWith("uint32")) {
      return JDBCType.BIGINT;
    }
    // Large integers - use NUMERIC for UInt64, Int128, Int256, UInt128, UInt256
    if (typeName.startsWith("uint64") || typeName.startsWith("int128") ||
        typeName.startsWith("int256") || typeName.startsWith("uint128") ||
        typeName.startsWith("uint256")) {
      return JDBCType.NUMERIC;
    }

    // Floating point types
    if (typeName.startsWith("float32")) {
      return JDBCType.REAL;
    }
    if (typeName.startsWith("float64")) {
      return JDBCType.DOUBLE;
    }

    // Decimal types
    if (typeName.startsWith("decimal")) {
      return JDBCType.DECIMAL;
    }

    // Date and time types
    if (typeName.equals("date") || typeName.startsWith("date32")) {
      return JDBCType.DATE;
    }
    if (typeName.startsWith("datetime64")) {
      return JDBCType.TIMESTAMP;
    }
    if (typeName.startsWith("datetime")) {
      return JDBCType.TIMESTAMP;
    }

    // String types
    if (typeName.startsWith("string") || typeName.startsWith("fixedstring")) {
      return JDBCType.VARCHAR;
    }

    // UUID type
    if (typeName.equals("uuid")) {
      return JDBCType.VARCHAR;
    }

    // Boolean type
    if (typeName.equals("bool") || typeName.equals("boolean")) {
      return JDBCType.BOOLEAN;
    }

    // Array types
    if (typeName.startsWith("array")) {
      return JDBCType.ARRAY;
    }

    // Default to VARCHAR for unknown types
    return JDBCType.VARCHAR;
  }

}
