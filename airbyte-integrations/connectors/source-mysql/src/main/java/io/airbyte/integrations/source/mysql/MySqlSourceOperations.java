/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import com.fasterxml.jackson.databind.node.NullNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.mysql.cj.MysqlType;
import com.mysql.cj.jdbc.result.ResultSetMetaData;
import com.mysql.cj.result.Field;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.DataTypeUtils;
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
      case BIT -> {
        if (field.getLength() == 1L) {
          // BIT(1) is interpreted as boolean
          putBoolean(json, columnName, resultSet, colIndex);
        } else {
          // BIT(>1)
          putBinary(json, columnName, resultSet, colIndex);
        }
      }
      case TINYINT, TINYINT_UNSIGNED -> {
        if (field.getLength() == 1L) {
          // TINYINT(1)
          putBoolean(json, columnName, resultSet, colIndex);
        } else {
          // TINYINT(>1)
          putShortInt(json, columnName, resultSet, colIndex);
        }
      }
      case BOOLEAN -> putBoolean(json, columnName, resultSet, colIndex);
      case SMALLINT, SMALLINT_UNSIGNED, MEDIUMINT, MEDIUMINT_UNSIGNED -> putInteger(json, columnName, resultSet, colIndex);
      case INT, INT_UNSIGNED -> {
        if (field.isUnsigned()) {
          putBigInt(json, columnName, resultSet, colIndex);
        } else {
          putInteger(json, columnName, resultSet, colIndex);
        }
      }
      case BIGINT, BIGINT_UNSIGNED -> putBigInt(json, columnName, resultSet, colIndex);
      case FLOAT, FLOAT_UNSIGNED -> putFloat(json, columnName, resultSet, colIndex);
      case DOUBLE, DOUBLE_UNSIGNED -> putDouble(json, columnName, resultSet, colIndex);
      case DECIMAL, DECIMAL_UNSIGNED -> putBigDecimal(json, columnName, resultSet, colIndex);
      case DATE -> putDate(json, columnName, resultSet, colIndex);
      case DATETIME, TIMESTAMP -> putTimestamp(json, columnName, resultSet, colIndex);
      case TIME -> putTime(json, columnName, resultSet, colIndex);
      // The returned year value can either be a java.sql.Short (when yearIsDateType=false)
      // or a java.sql.Date with the date set to January 1st, at midnight (when yearIsDateType=true).
      // Currently, JsonSchemaPrimitive does not support integer, but only supports number.
      // Because the number type will be interpreted as a double in many destinations, and it is
      // weird to show a year as a double, we set yearIsDateType=true in the JDBC connection string,
      // and parse the returned year value as a string.
      // The case can be re-evaluated when JsonSchemaPrimitive supports integer.
      case YEAR -> {
        final String year = resultSet.getDate(colIndex).toString().split("-")[0];
        json.put(columnName, DataTypeUtils.returnNullIfInvalid(() -> year));
      }
      case CHAR, VARCHAR -> {
        if (field.isBinary()) {
          // when character set is binary, the returned value is binary
          putBinary(json, columnName, resultSet, colIndex);
        } else {
          putString(json, columnName, resultSet, colIndex);
        }
      }
      case TINYBLOB, BLOB, MEDIUMBLOB, LONGBLOB, BINARY, VARBINARY -> putBinary(json, columnName, resultSet, colIndex);
      case TINYTEXT, TEXT, MEDIUMTEXT, LONGTEXT, JSON, ENUM, SET -> putString(json, columnName, resultSet, colIndex);
      case GEOMETRY -> json.put(columnName, Jsons.serialize(resultSet.getObject(colIndex)));
      case NULL -> json.set(columnName, NullNode.instance);
      default -> putDefault(json, columnName, resultSet, colIndex);
    }
  }

  /**
   * MySQL boolean is equivalent to tinyint(1).
   */
  @Override
  protected void putBoolean(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    node.put(columnName, resultSet.getInt(index) == 1);
  }

  // TODO: update this method with mysql specific types
  @Override
  public void setStatementField(final PreparedStatement preparedStatement,
                                final int parameterIndex,
                                final MysqlType cursorFieldType,
                                final String value)
      throws SQLException {
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
      case DATE -> JsonSchemaPrimitive.STRING;
      case TIME -> JsonSchemaPrimitive.STRING;
      case TIMESTAMP -> JsonSchemaPrimitive.STRING;
      case BLOB, BINARY, VARBINARY -> JsonSchemaPrimitive.STRING;
      // since column types aren't necessarily meaningful to Airbyte, liberally convert all unrecgonised
      // types to String
      default -> JsonSchemaPrimitive.STRING;
    };
  }

}
