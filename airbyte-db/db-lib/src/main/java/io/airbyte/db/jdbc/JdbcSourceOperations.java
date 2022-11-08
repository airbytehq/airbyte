/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

import static io.airbyte.db.jdbc.JdbcConstants.INTERNAL_COLUMN_NAME;
import static io.airbyte.db.jdbc.JdbcConstants.INTERNAL_COLUMN_TYPE;
import static io.airbyte.db.jdbc.JdbcConstants.INTERNAL_SCHEMA_NAME;
import static io.airbyte.db.jdbc.JdbcConstants.INTERNAL_TABLE_NAME;
import static io.airbyte.db.jdbc.JdbcUtils.ALLOWED_CURSOR_TYPES;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.db.SourceOperations;
import io.airbyte.protocol.models.JsonSchemaType;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Implementation of source operations with standard JDBC types.
 */
public class JdbcSourceOperations extends AbstractJdbcCompatibleSourceOperations<JDBCType> implements SourceOperations<ResultSet, JDBCType> {

  private static final Logger LOGGER = LoggerFactory.getLogger(JdbcSourceOperations.class);

  protected JDBCType safeGetJdbcType(final int columnTypeInt) {
    try {
      return JDBCType.valueOf(columnTypeInt);
    } catch (final Exception e) {
      return JDBCType.VARCHAR;
    }
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
      case BLOB, BINARY, VARBINARY, LONGVARBINARY -> putBinary(json, columnName, resultSet, colIndex);
      case ARRAY -> putArray(json, columnName, resultSet, colIndex);
      default -> putDefault(json, columnName, resultSet, colIndex);
    }
  }

  @Override
  public void setStatementField(final PreparedStatement preparedStatement,
                                final int parameterIndex,
                                final JDBCType cursorFieldType,
                                final String value)
      throws SQLException {
    switch (cursorFieldType) {

      case TIMESTAMP -> setTimestamp(preparedStatement, parameterIndex, value);
      case TIME -> setTime(preparedStatement, parameterIndex, value);
      case DATE -> setDate(preparedStatement, parameterIndex, value);
      case BIT -> setBit(preparedStatement, parameterIndex, value);
      case BOOLEAN -> setBoolean(preparedStatement, parameterIndex, value);
      case TINYINT, SMALLINT -> setShortInt(preparedStatement, parameterIndex, value);
      case INTEGER -> setInteger(preparedStatement, parameterIndex, value);
      case BIGINT -> setBigInteger(preparedStatement, parameterIndex, value);
      case FLOAT, DOUBLE -> setDouble(preparedStatement, parameterIndex, value);
      case REAL -> setReal(preparedStatement, parameterIndex, value);
      case NUMERIC, DECIMAL -> setDecimal(preparedStatement, parameterIndex, value);
      case CHAR, NCHAR, NVARCHAR, VARCHAR, LONGVARCHAR -> setString(preparedStatement, parameterIndex, value);
      case BINARY, BLOB -> setBinary(preparedStatement, parameterIndex, value);
      // since cursor are expected to be comparable, handle cursor typing strictly and error on
      // unrecognized types
      default -> throw new IllegalArgumentException(String.format("%s cannot be used as a cursor.", cursorFieldType));
    }
  }

  @Override
  public JDBCType getFieldType(final JsonNode field) {
    try {
      return JDBCType.valueOf(field.get(INTERNAL_COLUMN_TYPE).asInt());
    } catch (final IllegalArgumentException ex) {
      LOGGER.warn(String.format("Could not convert column: %s from table: %s.%s with type: %s. Casting to VARCHAR.",
          field.get(INTERNAL_COLUMN_NAME),
          field.get(INTERNAL_SCHEMA_NAME),
          field.get(INTERNAL_TABLE_NAME),
          field.get(INTERNAL_COLUMN_TYPE)));
      return JDBCType.VARCHAR;
    }
  }

  @Override
  public boolean isCursorType(JDBCType type) {
    return ALLOWED_CURSOR_TYPES.contains(type);
  }

  @Override
  public JsonSchemaType getJsonType(final JDBCType jdbcType) {
    return switch (jdbcType) {
      case BIT, BOOLEAN -> JsonSchemaType.BOOLEAN;
      case TINYINT, SMALLINT -> JsonSchemaType.INTEGER;
      case INTEGER -> JsonSchemaType.INTEGER;
      case BIGINT -> JsonSchemaType.INTEGER;
      case FLOAT, DOUBLE -> JsonSchemaType.NUMBER;
      case REAL -> JsonSchemaType.NUMBER;
      case NUMERIC, DECIMAL -> JsonSchemaType.NUMBER;
      case CHAR, NCHAR, NVARCHAR, VARCHAR, LONGVARCHAR -> JsonSchemaType.STRING;
      case DATE -> JsonSchemaType.STRING;
      case TIME -> JsonSchemaType.STRING;
      case TIMESTAMP -> JsonSchemaType.STRING;
      case BLOB, BINARY, VARBINARY, LONGVARBINARY -> JsonSchemaType.STRING_BASE_64;
      case ARRAY -> JsonSchemaType.ARRAY;
      // since column types aren't necessarily meaningful to Airbyte, liberally convert all unrecgonised
      // types to String
      default -> JsonSchemaType.STRING;
    };
  }

}
