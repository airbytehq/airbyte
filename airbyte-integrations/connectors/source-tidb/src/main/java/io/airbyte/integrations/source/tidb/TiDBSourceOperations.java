/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.tidb;

import static com.mysql.cj.MysqlType.*;
import static io.airbyte.db.jdbc.JdbcConstants.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.NullNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.mysql.cj.MysqlType;
import com.mysql.cj.jdbc.result.ResultSetMetaData;
import com.mysql.cj.result.Field;
import io.airbyte.db.DataTypeUtils;
import io.airbyte.db.SourceOperations;
import io.airbyte.db.jdbc.AbstractJdbcCompatibleSourceOperations;
import io.airbyte.protocol.models.JsonSchemaType;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TiDBSourceOperations extends AbstractJdbcCompatibleSourceOperations<MysqlType> implements SourceOperations<ResultSet, MysqlType> {

  private static final Logger LOGGER = LoggerFactory.getLogger(TiDBSourceOperations.class);
  private static final Set<MysqlType> ALLOWED_CURSOR_TYPES = Set.of(TINYINT, TINYINT_UNSIGNED, SMALLINT,
      SMALLINT_UNSIGNED, MEDIUMINT, MEDIUMINT_UNSIGNED, INT, INT_UNSIGNED, BIGINT, BIGINT_UNSIGNED, FLOAT,
      FLOAT_UNSIGNED, DOUBLE, DOUBLE_UNSIGNED, DECIMAL, DECIMAL_UNSIGNED, DATE, DATETIME, TIMESTAMP, TIME,
      YEAR, VARCHAR, TINYTEXT, TEXT, MEDIUMTEXT, LONGTEXT);

  @Override
  public void copyToJsonField(final ResultSet resultSet, final int colIndex, final ObjectNode json) throws SQLException {
    final ResultSetMetaData metaData = (ResultSetMetaData) resultSet.getMetaData();
    final Field field = metaData.getFields()[colIndex - 1];
    final String columnName = field.getName();
    final MysqlType columnType = field.getMysqlType();

    switch (columnType) {
      case BIT -> {
        if (field.getLength() == 1L) {
          // BIT(1) is boolean
          putBoolean(json, columnName, resultSet, colIndex);
        } else {
          putBinary(json, columnName, resultSet, colIndex);
        }
      }
      case BOOLEAN -> putBoolean(json, columnName, resultSet, colIndex);
      case TINYINT, TINYINT_UNSIGNED -> {
        if (field.getLength() == 1L) {
          // TINYINT(1) is boolean
          putBoolean(json, columnName, resultSet, colIndex);
        } else {
          putShortInt(json, columnName, resultSet, colIndex);
        }
      }
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
      case TINYBLOB, BLOB, MEDIUMBLOB, LONGBLOB, BINARY, VARBINARY, GEOMETRY -> putBinary(json, columnName, resultSet, colIndex);
      case TINYTEXT, TEXT, MEDIUMTEXT, LONGTEXT, JSON, ENUM, SET -> putString(json, columnName, resultSet, colIndex);
      case NULL -> json.set(columnName, NullNode.instance);
      default -> putDefault(json, columnName, resultSet, colIndex);
    }
  }

  @Override
  public void setCursorField(final PreparedStatement preparedStatement, final int parameterIndex, final MysqlType cursorFieldType, final String value)
      throws SQLException {
    switch (cursorFieldType) {
      case BIT -> setBit(preparedStatement, parameterIndex, value);
      case BOOLEAN -> setBoolean(preparedStatement, parameterIndex, value);
      case TINYINT, TINYINT_UNSIGNED, SMALLINT, SMALLINT_UNSIGNED, MEDIUMINT, MEDIUMINT_UNSIGNED -> setInteger(preparedStatement, parameterIndex,
          value);
      case INT, INT_UNSIGNED, BIGINT, BIGINT_UNSIGNED -> setBigInteger(preparedStatement, parameterIndex, value);
      case FLOAT, FLOAT_UNSIGNED, DOUBLE, DOUBLE_UNSIGNED -> setDouble(preparedStatement, parameterIndex, value);
      case DECIMAL, DECIMAL_UNSIGNED -> setDecimal(preparedStatement, parameterIndex, value);
      case DATE -> setDate(preparedStatement, parameterIndex, value);
      case DATETIME, TIMESTAMP -> setTimestamp(preparedStatement, parameterIndex, value);
      case TIME -> setTime(preparedStatement, parameterIndex, value);
      case YEAR, CHAR, VARCHAR, TINYTEXT, TEXT, MEDIUMTEXT, LONGTEXT, ENUM, SET -> setString(preparedStatement, parameterIndex, value);
      case TINYBLOB, BLOB, MEDIUMBLOB, LONGBLOB, BINARY, VARBINARY -> setBinary(preparedStatement, parameterIndex, value);
      // since cursor are expected to be comparable, handle cursor typing strictly and error on
      // unrecognized types
      default -> throw new IllegalArgumentException(String.format("%s cannot be used as a cursor.", cursorFieldType));
    }
  }

  @Override
  public MysqlType getDatabaseFieldType(final JsonNode field) {
    try {
      final MysqlType literalType = MysqlType.getByName(field.get(INTERNAL_COLUMN_TYPE_NAME).asText());
      final int columnSize = field.get(INTERNAL_COLUMN_SIZE).asInt();

      switch (literalType) {
        // BIT(1) and TINYINT(1) are interpreted as boolean
        case BIT, TINYINT, TINYINT_UNSIGNED -> {
          if (columnSize == 1) {
            return MysqlType.BOOLEAN;
          }
        }
        // When CHAR[N] and VARCHAR[N] columns have binary character set, the returned
        // types are BINARY[N] and VARBINARY[N], respectively. So we don't need to
        // convert them here. This is verified in MySqlSourceDatatypeTest.
      }

      return literalType;
    } catch (final IllegalArgumentException ex) {
      LOGGER.warn(String.format("Could not convert column: %s from table: %s.%s with type: %s (type name: %s). Casting to VARCHAR.",
          field.get(INTERNAL_COLUMN_NAME),
          field.get(INTERNAL_SCHEMA_NAME),
          field.get(INTERNAL_TABLE_NAME),
          field.get(INTERNAL_COLUMN_TYPE),
          field.get(INTERNAL_COLUMN_TYPE_NAME)));
      return MysqlType.VARCHAR;
    }
  }

  @Override
  public boolean isCursorType(final MysqlType type) {
    return ALLOWED_CURSOR_TYPES.contains(type);
  }

  @Override
  public JsonSchemaType getAirbyteType(final MysqlType mysqlType) {
    return switch (mysqlType) {
      case
      // TINYINT(1) is boolean, but it should have been converted to MysqlType.BOOLEAN in {@link
      // getFieldType}
      TINYINT, TINYINT_UNSIGNED, SMALLINT, SMALLINT_UNSIGNED, INT, MEDIUMINT, MEDIUMINT_UNSIGNED, INT_UNSIGNED, BIGINT, BIGINT_UNSIGNED -> JsonSchemaType.INTEGER;
      case FLOAT, FLOAT_UNSIGNED, DOUBLE, DOUBLE_UNSIGNED, DECIMAL, DECIMAL_UNSIGNED -> JsonSchemaType.NUMBER;
      case BOOLEAN -> JsonSchemaType.BOOLEAN;
      case NULL -> JsonSchemaType.NULL;
      // BIT(1) is boolean, but it should have been converted to MysqlType.BOOLEAN in {@link getFieldType}
      case BIT, TINYBLOB, BLOB, MEDIUMBLOB, LONGBLOB, BINARY, VARBINARY, GEOMETRY -> JsonSchemaType.STRING_BASE_64;
      default -> JsonSchemaType.STRING;
    };
  }

}
