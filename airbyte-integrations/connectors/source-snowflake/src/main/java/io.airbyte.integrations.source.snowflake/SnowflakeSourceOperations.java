/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import io.airbyte.protocol.models.JsonSchemaType;
import java.math.BigDecimal;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class SnowflakeSourceOperations extends JdbcSourceOperations {

  @Override
  protected void putDouble(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) {
    try {
      final double value = resultSet.getDouble(index);
      node.put(columnName, value);
    } catch (final SQLException e) {
      node.put(columnName, (Double) null);
    }
  }

  @Override
  protected void putBigInt(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) {
    try {
      final var value = resultSet.getBigDecimal(index);
      node.put(columnName, value);
    } catch (final SQLException e) {
      node.put(columnName, (BigDecimal) null);
    }
  }

  @Override
  protected void setTimestamp(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    preparedStatement.setString(parameterIndex, value);
  }

  @Override
  public JsonSchemaType getJsonType(final JDBCType jdbcType) {
    return switch (jdbcType) {
      case BIT, BOOLEAN -> JsonSchemaType.BOOLEAN;
      case REAL, FLOAT, DOUBLE, NUMERIC, DECIMAL -> JsonSchemaType.NUMBER;
      case TINYINT, SMALLINT, INTEGER, BIGINT -> JsonSchemaType.INTEGER;
      case CHAR, NCHAR, NVARCHAR, VARCHAR, LONGVARCHAR -> JsonSchemaType.STRING;
      case DATE -> JsonSchemaType.STRING_DATE;
      case TIME -> JsonSchemaType.STRING_TIME_WITHOUT_TIMEZONE;
      case TIMESTAMP -> JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE;
      case TIMESTAMP_WITH_TIMEZONE -> JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE;
      case TIME_WITH_TIMEZONE -> JsonSchemaType.STRING_TIME_WITH_TIMEZONE;
      case BLOB, BINARY, VARBINARY, LONGVARBINARY -> JsonSchemaType.STRING_BASE_64;
      case ARRAY -> JsonSchemaType.ARRAY;
      // since column types aren't necessarily meaningful to Airbyte, liberally convert all unrecgonised
      // types to String
      default -> JsonSchemaType.STRING;
    };
  }

  @Override
  public void setJsonField(final ResultSet resultSet, final int colIndex, final ObjectNode json) throws SQLException {
    final int columnTypeInt = resultSet.getMetaData().getColumnType(colIndex);
    final String columnName = resultSet.getMetaData().getColumnName(colIndex);
    final JDBCType columnType = safeGetJdbcType(columnTypeInt);

    // https://www.cis.upenn.edu/~bcpierce/courses/629/jdkdocs/guide/jdbc/getstart/mapping.doc.html
    switch (columnType) {
      case BIT, BOOLEAN -> putBoolean(json, columnName, resultSet, colIndex);
      case TINYINT, SMALLINT -> putShortInt(json, columnName, resultSet, colIndex);
      case INTEGER -> putInteger(json, columnName, resultSet, colIndex);
      case BIGINT -> putBigInt(json, columnName, resultSet, colIndex);
      case FLOAT, DOUBLE -> putDouble(json, columnName, resultSet, colIndex);
      case REAL -> putFloat(json, columnName, resultSet, colIndex);
      case NUMERIC, DECIMAL -> putBigDecimal(json, columnName, resultSet, colIndex);
      case CHAR, VARCHAR, LONGVARCHAR -> putString(json, columnName, resultSet, colIndex);
      case DATE -> putDate(json, columnName, resultSet, colIndex);
      case TIME -> putTime(json, columnName, resultSet, colIndex);
      case TIMESTAMP -> putTimestamp(json, columnName, resultSet, colIndex);
      case TIMESTAMP_WITH_TIMEZONE -> putTimestamp(json, columnName, resultSet, colIndex);
      case BLOB, BINARY, VARBINARY, LONGVARBINARY -> putBinary(json, columnName, resultSet, colIndex);
      case ARRAY -> putArray(json, columnName, resultSet, colIndex);
      default -> putDefault(json, columnName, resultSet, colIndex);
    }
  }
}
