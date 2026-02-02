/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.clickhouse;

import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_COLUMN_TYPE;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_COLUMN_TYPE_NAME;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.SourceOperations;
import io.airbyte.cdk.db.jdbc.AbstractJdbcCompatibleSourceOperations;
import io.airbyte.protocol.models.JsonSchemaType;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ClickHouseSourceOperations extends AbstractJdbcCompatibleSourceOperations<JDBCType>
    implements SourceOperations<ResultSet, JDBCType> {

  private static final Logger LOGGER = LoggerFactory.getLogger(ClickHouseSourceOperations.class);

  @Override
  public void copyToJsonField(final ResultSet resultSet, final int colIndex, final ObjectNode json) throws SQLException {
    final String columnTypeName = resultSet.getMetaData().getColumnTypeName(colIndex).toLowerCase();
    final String columnName = resultSet.getMetaData().getColumnName(colIndex);
    final int columnType = resultSet.getMetaData().getColumnType(colIndex);

    // Handle ClickHouse-specific temporal types
    if (columnTypeName.startsWith("datetime64") || columnTypeName.equals("datetime")) {
      putTimestamp(json, columnName, resultSet, colIndex);
    } else if (columnTypeName.equals("date") || columnTypeName.equals("date32")) {
      putDate(json, columnName, resultSet, colIndex);
    } else {
      // Handle standard JDBC types
      final JDBCType jdbcType;
      try {
        jdbcType = JDBCType.valueOf(columnType);
      } catch (final IllegalArgumentException e) {
        putString(json, columnName, resultSet, colIndex);
        return;
      }

      switch (jdbcType) {
        case BIT, BOOLEAN -> putBoolean(json, columnName, resultSet, colIndex);
        case TINYINT, SMALLINT -> putShortInt(json, columnName, resultSet, colIndex);
        case INTEGER -> putInteger(json, columnName, resultSet, colIndex);
        case BIGINT -> putBigInt(json, columnName, resultSet, colIndex);
        case FLOAT, REAL -> putFloat(json, columnName, resultSet, colIndex);
        case DOUBLE -> putDouble(json, columnName, resultSet, colIndex);
        case NUMERIC, DECIMAL -> putBigDecimal(json, columnName, resultSet, colIndex);
        case DATE -> putDate(json, columnName, resultSet, colIndex);
        case TIME, TIME_WITH_TIMEZONE -> putTime(json, columnName, resultSet, colIndex);
        case TIMESTAMP, TIMESTAMP_WITH_TIMEZONE -> putTimestamp(json, columnName, resultSet, colIndex);
        case BLOB, BINARY, VARBINARY, LONGVARBINARY -> putBinary(json, columnName, resultSet, colIndex);
        default -> putString(json, columnName, resultSet, colIndex);
      }
    }
  }

  @Override
  public void setCursorField(final PreparedStatement preparedStatement,
                             final int parameterIndex,
                             final JDBCType cursorFieldType,
                             final String value)
      throws SQLException {
    switch (cursorFieldType) {
      case DATE -> setDate(preparedStatement, parameterIndex, value);
      case TIME -> setTime(preparedStatement, parameterIndex, value);
      case TIMESTAMP, TIMESTAMP_WITH_TIMEZONE -> setTimestamp(preparedStatement, parameterIndex, value);
      case BOOLEAN -> setBoolean(preparedStatement, parameterIndex, value);
      case TINYINT, SMALLINT -> setShortInt(preparedStatement, parameterIndex, value);
      case INTEGER -> setInteger(preparedStatement, parameterIndex, value);
      case BIGINT -> setBigInteger(preparedStatement, parameterIndex, value);
      case FLOAT, DOUBLE -> setDouble(preparedStatement, parameterIndex, value);
      case REAL -> setReal(preparedStatement, parameterIndex, value);
      case NUMERIC, DECIMAL -> setDecimal(preparedStatement, parameterIndex, value);
      case CHAR, NCHAR, NVARCHAR, VARCHAR, LONGVARCHAR -> setString(preparedStatement, parameterIndex, value);
      case BINARY, BLOB -> setBinary(preparedStatement, parameterIndex, value);
      default -> throw new IllegalArgumentException(String.format("%s cannot be used as a cursor.", cursorFieldType));
    }
  }

  @Override
  public JDBCType getDatabaseFieldType(final JsonNode field) {
    try {
      final String typeName = field.get(INTERNAL_COLUMN_TYPE_NAME).asText().toLowerCase();
      if (typeName.startsWith("datetime64") || typeName.equals("datetime")) {
        return JDBCType.TIMESTAMP;
      } else if (typeName.equals("date") || typeName.equals("date32")) {
        return JDBCType.DATE;
      }
      return JDBCType.valueOf(field.get(INTERNAL_COLUMN_TYPE).asInt());
    } catch (final IllegalArgumentException ex) {
      LOGGER.warn("Could not convert column type: {}. Falling back to VARCHAR.", field.get(INTERNAL_COLUMN_TYPE_NAME));
      return JDBCType.VARCHAR;
    }
  }

  @Override
  public boolean isCursorType(final JDBCType type) {
    return type != null;
  }

  @Override
  public JsonSchemaType getAirbyteType(final JDBCType jdbcType) {
    return switch (jdbcType) {
      case BOOLEAN, BIT -> JsonSchemaType.BOOLEAN;
      case TINYINT, SMALLINT, INTEGER, BIGINT -> JsonSchemaType.INTEGER;
      case FLOAT, DOUBLE, REAL, NUMERIC, DECIMAL -> JsonSchemaType.NUMBER;
      case BLOB, BINARY, VARBINARY, LONGVARBINARY -> JsonSchemaType.STRING_BASE_64;
      case DATE -> JsonSchemaType.STRING_DATE;
      case TIME, TIME_WITH_TIMEZONE -> JsonSchemaType.STRING_TIME_WITHOUT_TIMEZONE;
      case TIMESTAMP, TIMESTAMP_WITH_TIMEZONE -> JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE;
      default -> JsonSchemaType.STRING;
    };
  }

}
