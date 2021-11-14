/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import com.fasterxml.jackson.databind.node.ObjectNode;
import com.mysql.cj.MysqlType;
import com.mysql.cj.jdbc.result.ResultSetMetaData;
import com.mysql.cj.result.Field;
import io.airbyte.db.SourceOperations;
import io.airbyte.db.jdbc.AbstractJdbcCompatibleSourceOperations;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class MySqlSourceOperations extends AbstractJdbcCompatibleSourceOperations<MysqlType> implements SourceOperations<ResultSet, MysqlType> {

  /**
   * @param colIndex 1-based column index.
   */
  @Override
  protected void setJsonField(final ResultSet resultSet, final int colIndex, final ObjectNode json) throws SQLException {
    final ResultSetMetaData metaData = (ResultSetMetaData) resultSet.getMetaData();
    final Field field = metaData.getFields()[colIndex - 1];
    final String columnName = field.getName();
    final MysqlType columnType = field.getMysqlType();

    // https://dev.mysql.com/doc/connector-j/8.0/en/connector-j-reference-type-conversions.html
    switch (columnType) {
      case BIT, BOOLEAN -> putBoolean(json, columnName, resultSet, colIndex);
      case YEAR -> json.put(columnName, resultSet.getDate(colIndex).toString().split("-")[0]);
      case TINYINT, SMALLINT -> putShortInt(json, columnName, resultSet, colIndex);
      case INT -> putInteger(json, columnName, resultSet, colIndex);
      case BIGINT -> putBigInt(json, columnName, resultSet, colIndex);
      case FLOAT, DOUBLE -> putDouble(json, columnName, resultSet, colIndex);
      case DECIMAL -> putNumber(json, columnName, resultSet, colIndex);
      case CHAR, VARCHAR -> putString(json, columnName, resultSet, colIndex);
      case DATE -> putDate(json, columnName, resultSet, colIndex);
      case TIME -> putTime(json, columnName, resultSet, colIndex);
      case TIMESTAMP, DATETIME -> putTimestamp(json, columnName, resultSet, colIndex);
      case BLOB, BINARY, VARBINARY -> putBinary(json, columnName, resultSet, colIndex);
      default -> putDefault(json, columnName, resultSet, colIndex);
    }
  }

  @Override
  protected void putBoolean(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    node.put(columnName, resultSet.getInt(index) == 1);
  }

  // TODO: update this method with mysql specific types
  @Override
  public void setStatementField(final PreparedStatement preparedStatement,
                                final int parameterIndex,
                                final MysqlType cursorFieldType,
                                final String value) throws SQLException {
    switch (cursorFieldType) {

      case TIMESTAMP, DATETIME -> setTimestamp(preparedStatement, parameterIndex, value);
      case YEAR -> setString(preparedStatement, parameterIndex, value);
      case TIME -> setTime(preparedStatement, parameterIndex, value);
      case DATE -> setDate(preparedStatement, parameterIndex, value);
      case BIT -> setBit(preparedStatement, parameterIndex, value);
      case BOOLEAN -> setBoolean(preparedStatement, parameterIndex, value);
      case TINYINT, SMALLINT -> setShortInt(preparedStatement, parameterIndex, value);
      case INT -> setInteger(preparedStatement, parameterIndex, value);
      case BIGINT -> setBigInteger(preparedStatement, parameterIndex, value);
      case FLOAT, DOUBLE -> setDouble(preparedStatement, parameterIndex, value);
      case DECIMAL -> setDecimal(preparedStatement, parameterIndex, value);
      case CHAR, VARCHAR -> setString(preparedStatement, parameterIndex, value);
      case BINARY, BLOB -> setBinary(preparedStatement, parameterIndex, value);
      // since cursor are expected to be comparable, handle cursor typing strictly and error on
      // unrecognized types
      default -> throw new IllegalArgumentException(String.format("%s is not supported.", cursorFieldType));
    }
  }

  // TODO: update this method with mysql specific types
  @Override
  public JsonSchemaPrimitive getType(final MysqlType mysqlType) {
    return switch (mysqlType) {
      case BIT, BOOLEAN -> JsonSchemaPrimitive.BOOLEAN;
      case YEAR -> JsonSchemaPrimitive.STRING;
      case TINYINT, SMALLINT -> JsonSchemaPrimitive.NUMBER;
      case INT -> JsonSchemaPrimitive.NUMBER;
      case BIGINT -> JsonSchemaPrimitive.NUMBER;
      case FLOAT, DOUBLE -> JsonSchemaPrimitive.NUMBER;
      case DECIMAL -> JsonSchemaPrimitive.NUMBER;
      case CHAR, VARCHAR -> JsonSchemaPrimitive.STRING;
      case DATE -> JsonSchemaPrimitive.STRING_DATE;
      case TIME -> JsonSchemaPrimitive.STRING_TIME;
      case TIMESTAMP -> JsonSchemaPrimitive.STRING_DATETIME;
      case BLOB, BINARY, VARBINARY -> JsonSchemaPrimitive.STRING;
      // since column types aren't necessarily meaningful to Airbyte, liberally convert all unrecgonised
      // types to String
      default -> JsonSchemaPrimitive.STRING;
    };
  }
}
