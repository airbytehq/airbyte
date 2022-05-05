/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.db.jdbc.JdbcConstants.INTERNAL_COLUMN_NAME;
import static io.airbyte.db.jdbc.JdbcConstants.INTERNAL_COLUMN_TYPE;
import static io.airbyte.db.jdbc.JdbcConstants.INTERNAL_COLUMN_TYPE_NAME;
import static io.airbyte.db.jdbc.JdbcConstants.INTERNAL_SCHEMA_NAME;
import static io.airbyte.db.jdbc.JdbcConstants.INTERNAL_TABLE_NAME;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.DataTypeUtils;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import io.airbyte.protocol.models.JsonSchemaType;
import java.math.BigDecimal;
import java.sql.JDBCType;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.Collections;
import org.postgresql.jdbc.PgResultSetMetaData;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresSourceOperations extends JdbcSourceOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresSourceOperations.class);

  @Override
  public JsonNode rowToJson(final ResultSet queryContext) throws SQLException {
    // the first call communicates with the database. after that the result is cached.
    final ResultSetMetaData metadata = queryContext.getMetaData();
    final int columnCount = metadata.getColumnCount();
    final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());

    for (int i = 1; i <= columnCount; i++) {
      final String columnType = metadata.getColumnTypeName(i);
      // attempt to access the column. this allows us to know if it is null before we do type-specific
      // parsing. if it is null, we can move on. while awkward, this seems to be the agreed upon way of
      // checking for null values with jdbc.

      if (columnType.equalsIgnoreCase("money")) {
        // when a column is of type MONEY, getObject will throw exception
        // this is a bug that will not be fixed:
        // https://github.com/pgjdbc/pgjdbc/issues/425
        // https://github.com/pgjdbc/pgjdbc/issues/1835
        queryContext.getString(i);
      } else if (columnType.equalsIgnoreCase("bit")) {
        // getObject will fail as it tries to parse the value as boolean
        queryContext.getString(i);
      } else if (columnType.equalsIgnoreCase("numeric") || columnType.equalsIgnoreCase("decimal")) {
        // getObject will fail when the value is 'infinity'
        queryContext.getDouble(i);
      } else {
        queryContext.getObject(i);
      }

      // convert to java types that will convert into reasonable json.
      setJsonField(queryContext, i, jsonNode);
    }

    return jsonNode;
  }

  @Override
  public void setJsonField(final ResultSet resultSet, final int colIndex, final ObjectNode json) throws SQLException {
    final PgResultSetMetaData metadata = (PgResultSetMetaData) resultSet.getMetaData();
    final String columnName = metadata.getColumnName(colIndex);
    final String columnTypeName = metadata.getColumnTypeName(colIndex);
    final JDBCType columnType = safeGetJdbcType(metadata.getColumnType(colIndex));

    if (resultSet.getString(colIndex) == null) {
      json.putNull(columnName);
    } else if (columnTypeName.equalsIgnoreCase("bool") || columnTypeName.equalsIgnoreCase("boolean")) {
      putBoolean(json, columnName, resultSet, colIndex);
    } else if (columnTypeName.equalsIgnoreCase("bytea")) {
      putString(json, columnName, resultSet, colIndex);
    } else if (columnTypeName.equalsIgnoreCase("time") || columnTypeName.equalsIgnoreCase("timetz")) {
      putString(json, columnName, resultSet, colIndex);
    } else {
      // https://www.postgresql.org/docs/14/datatype.html
      switch (columnType) {
        case BOOLEAN -> putBoolean(json, columnName, resultSet, colIndex);
        case TINYINT, SMALLINT -> putShortInt(json, columnName, resultSet, colIndex);
        case INTEGER -> putInteger(json, columnName, resultSet, colIndex);
        case BIGINT -> putBigInt(json, columnName, resultSet, colIndex);
        case FLOAT, DOUBLE -> putDouble(json, columnName, resultSet, colIndex);
        case REAL -> putFloat(json, columnName, resultSet, colIndex);
        case NUMERIC, DECIMAL -> putBigDecimal(json, columnName, resultSet, colIndex);
        // BIT is a bit string in Postgres, e.g. '0100'
        case BIT, CHAR, VARCHAR, LONGVARCHAR -> putString(json, columnName, resultSet, colIndex);
        case DATE -> putDate(json, columnName, resultSet, colIndex);
        case TIME -> putTime(json, columnName, resultSet, colIndex);
        case TIMESTAMP -> putTimestamp(json, columnName, resultSet, colIndex);
        case BLOB, BINARY, VARBINARY, LONGVARBINARY -> putBinary(json, columnName, resultSet, colIndex);
        case ARRAY -> putArray(json, columnName, resultSet, colIndex);
        default -> putDefault(json, columnName, resultSet, colIndex);
      }
    }
  }

  @Override
  public JDBCType getFieldType(final JsonNode field) {
    try {
      final String typeName = field.get(INTERNAL_COLUMN_TYPE_NAME).asText();
      // Postgres boolean is mapped to JDBCType.BIT, but should be BOOLEAN
      if (typeName.equalsIgnoreCase("bool") || typeName.equalsIgnoreCase("boolean")) {
        return JDBCType.BOOLEAN;
      } else if (typeName.equalsIgnoreCase("bytea")) {
        // BYTEA is variable length binary string with hex output format by default (e.g. "\x6b707a").
        // It should not be converted to base64 binary string. So it is represented as JDBC VARCHAR.
        // https://www.postgresql.org/docs/14/datatype-binary.html
        return JDBCType.VARCHAR;
      }

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
  public JsonSchemaType getJsonType(JDBCType jdbcType) {
    return switch (jdbcType) {
      case BOOLEAN -> JsonSchemaType.BOOLEAN;
      case TINYINT, SMALLINT, INTEGER, BIGINT, FLOAT, DOUBLE, REAL, NUMERIC, DECIMAL -> JsonSchemaType.NUMBER;
      case BLOB, BINARY, VARBINARY, LONGVARBINARY -> JsonSchemaType.STRING_BASE_64;
      case ARRAY -> JsonSchemaType.ARRAY;
      default -> JsonSchemaType.STRING;
    };
  }

  protected void putBoolean(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    node.put(columnName, resultSet.getString(index).equalsIgnoreCase("t"));
  }

  protected void putBigDecimal(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) {
    final BigDecimal bigDecimal = DataTypeUtils.returnNullIfInvalid(() -> resultSet.getBigDecimal(index));
    if (bigDecimal != null) {
      node.put(columnName, bigDecimal);
    } else {
      // Special values (Infinity, -Infinity, and NaN) is default to null for now.
      // https://github.com/airbytehq/airbyte/issues/8902
      node.put(columnName, (BigDecimal) null);
    }
  }

  @Override
  protected void putDouble(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    if (resultSet.getMetaData().getColumnTypeName(index).equals("money")) {
      putMoney(node, columnName, resultSet, index);
    } else {
      super.putDouble(node, columnName, resultSet, index);
    }
  }

  private void putMoney(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    final String moneyValue = parseMoneyValue(resultSet.getString(index));
    node.put(columnName, DataTypeUtils.returnNullIfInvalid(() -> Double.valueOf(moneyValue), Double::isFinite));
  }

  /**
   * @return monetary value in numbers without the currency symbol or thousands separators.
   */
  @VisibleForTesting
  static String parseMoneyValue(final String moneyString) {
    return moneyString.replaceAll("[^\\d.-]", "");
  }

}
