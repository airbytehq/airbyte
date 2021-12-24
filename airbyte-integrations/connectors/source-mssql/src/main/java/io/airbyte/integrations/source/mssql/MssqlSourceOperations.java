/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.node.ObjectNode;
import com.microsoft.sqlserver.jdbc.Geography;
import com.microsoft.sqlserver.jdbc.Geometry;
import com.microsoft.sqlserver.jdbc.SQLServerResultSetMetaData;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import java.sql.JDBCType;
import java.sql.ResultSet;
import java.sql.SQLException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MssqlSourceOperations extends JdbcSourceOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlSourceOperations.class);

  @Override
  public void setJsonField(final ResultSet resultSet, final int colIndex, final ObjectNode json)
      throws SQLException {

    final SQLServerResultSetMetaData metadata = (SQLServerResultSetMetaData) resultSet
        .getMetaData();
    final String columnName = metadata.getColumnName(colIndex);
    final String columnTypeName = metadata.getColumnTypeName(colIndex);
    final JDBCType columnType = safeGetJdbcType(metadata.getColumnType(colIndex));

    if (columnTypeName.equalsIgnoreCase("time")) {
      putString(json, columnName, resultSet, colIndex);
    } else if (columnTypeName.equalsIgnoreCase("geometry")) {
      putGeometry(json, columnName, resultSet, colIndex);
    } else if (columnTypeName.equalsIgnoreCase("geography")) {
      putGeography(json, columnName, resultSet, colIndex);
    } else {
      switch (columnType) {
        case BIT, BOOLEAN -> putBoolean(json, columnName, resultSet, colIndex);
        case TINYINT, SMALLINT -> putShortInt(json, columnName, resultSet, colIndex);
        case INTEGER -> putInteger(json, columnName, resultSet, colIndex);
        case BIGINT -> putBigInt(json, columnName, resultSet, colIndex);
        case FLOAT, DOUBLE -> putDouble(json, columnName, resultSet, colIndex);
        case REAL -> putFloat(json, columnName, resultSet, colIndex);
        case NUMERIC, DECIMAL -> putBigDecimal(json, columnName, resultSet, colIndex);
        case CHAR, NVARCHAR, VARCHAR, LONGVARCHAR -> putString(json, columnName, resultSet, colIndex);
        case DATE -> putDate(json, columnName, resultSet, colIndex);
        case TIME -> putTime(json, columnName, resultSet, colIndex);
        case TIMESTAMP -> putTimestamp(json, columnName, resultSet, colIndex);
        case BLOB, BINARY, VARBINARY, LONGVARBINARY -> putBinary(json, columnName, resultSet,
            colIndex);
        case ARRAY -> putArray(json, columnName, resultSet, colIndex);
        default -> putDefault(json, columnName, resultSet, colIndex);
      }
    }
  }

  @Override
  protected void putBinary(final ObjectNode node,
                           final String columnName,
                           final ResultSet resultSet,
                           final int index)
      throws SQLException {
    byte[] bytes = resultSet.getBytes(index);
    String value = new String(bytes);
    node.put(columnName, value);
  }

  protected void putGeometry(final ObjectNode node,
                             final String columnName,
                             final ResultSet resultSet,
                             final int index)
      throws SQLException {
    node.put(columnName, Geometry.deserialize(resultSet.getBytes(index)).toString());
  }

  protected void putGeography(final ObjectNode node,
                              final String columnName,
                              final ResultSet resultSet,
                              final int index)
      throws SQLException {
    node.put(columnName, Geography.deserialize(resultSet.getBytes(index)).toString());
  }

}
