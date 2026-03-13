/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.clickhouse;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.jdbc.JdbcConstants;
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations;
import java.sql.JDBCType;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Types;

/**
 * Custom source operations for ClickHouse that handles type mapping differences.
 *
 * <p>
 * The ClickHouse JDBC driver 0.9.x returns JDBCType.OTHER for large integer types that don't have
 * exact JDBC equivalents (UInt64, Int128, Int256, UInt128, UInt256). This class maps those types to
 * NUMERIC so they can be used as cursor columns for incremental sync.
 */
public class ClickHouseSourceOperations extends JdbcSourceOperations {

  @Override
  public JDBCType getDatabaseFieldType(final JsonNode field) {
    final int columnType = field.get(JdbcConstants.INTERNAL_COLUMN_TYPE).asInt();

    // If the driver returns OTHER, look at the type name and map it appropriately
    if (columnType == Types.OTHER) {
      final String typeName = field.get(JdbcConstants.INTERNAL_COLUMN_TYPE_NAME).asText();
      return mapOtherTypeToJdbcType(typeName);
    }

    // For standard JDBC types, use the parent implementation
    return super.getDatabaseFieldType(field);
  }

  /**
   * Maps ClickHouse type names to standard JDBC types when the driver returns JDBCType.OTHER. Only
   * handles types that actually return as OTHER (large integers without JDBC equivalents).
   */
  private JDBCType mapOtherTypeToJdbcType(final String rawTypeName) {
    final String typeName = rawTypeName.toLowerCase();

    // Large integers that don't have standard JDBC equivalents return as OTHER
    // UInt64 can't fit in signed BIGINT, and Int128/Int256/UInt128/UInt256 have no JDBC equivalent
    if (typeName.startsWith("uint64") || typeName.startsWith("int128") ||
        typeName.startsWith("int256") || typeName.startsWith("uint128") ||
        typeName.startsWith("uint256")) {
      return JDBCType.NUMERIC;
    }

    // Default to VARCHAR for any other types that unexpectedly return as OTHER
    return JDBCType.VARCHAR;
  }

  /**
   * Overrides copyToJsonField to work around an off-by-one bug in the ClickHouse JDBC v2 driver's
   * ArrayResultSet.next() method.
   *
   * <p>
   * The driver's ArrayResultSet.next() returns true one extra time past the end of the array,
   * causing a "No current row" SQLException when getString(2) is called on the phantom row.
   * For ARRAY columns, this override uses Array.getArray() to get a Java Object[] directly,
   * bypassing the buggy ArrayResultSet entirely. All other types delegate to the parent.
   *
   * @see <a href="https://github.com/airbytehq/airbyte/issues/61419">#61419</a>
   */
  @Override
  public void copyToJsonField(final ResultSet resultSet, final int colIndex,
      final ObjectNode json) throws SQLException {
    final int columnTypeInt = resultSet.getMetaData().getColumnType(colIndex);
    if (columnTypeInt == Types.ARRAY) {
      final String columnName = resultSet.getMetaData().getColumnName(colIndex);
      final var arrayNode = new ObjectMapper().createArrayNode();
      final Object[] elements = (Object[]) resultSet.getArray(colIndex).getArray();
      for (final Object element : elements) {
        arrayNode.add(element == null ? null : element.toString());
      }
      json.set(columnName, arrayNode);
    } else {
      super.copyToJsonField(resultSet, colIndex, json);
    }
  }

}
