/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.pervasive;

import static io.airbyte.cdk.db.DataTypeUtils.TIMESTAMPTZ_FORMATTER;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.DataTypeUtils;
import io.airbyte.cdk.db.jdbc.DateTimeConverter;
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations;
import java.sql.Date;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Time;
import java.sql.Timestamp;
import java.text.ParseException;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.OffsetDateTime;
import java.time.OffsetTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeParseException;
import com.fasterxml.jackson.databind.JsonNode;
import java.sql.JDBCType;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_COLUMN_TYPE;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// import static com.pervasive.jdbc.v2;

// Teradata only supports native java.sql types when creating prepared statements and returning from
// resultSet
public class PervasiveSourceOperations extends JdbcSourceOperations {
  private static final Logger LOGGER = LoggerFactory.getLogger(PervasiveSourceOperations.class);

  @Override
  public JDBCType getDatabaseFieldType(final JsonNode field) {
    final int type = field.get(INTERNAL_COLUMN_TYPE).asInt();
    return switch (type) {
      case 7, 16 -> JDBCType.BOOLEAN;
      case 1, 14, 15 -> JDBCType.INTEGER;
      case 2, 5, 6, 8, 9, 17, 18, 19, 28, 29, 31 -> JDBCType.FLOAT;
      case 0, 11, 21, 25, 26, 27 -> JDBCType.VARCHAR;
      case 3 -> JDBCType.DATE;
      case 4 -> JDBCType.TIME;
      case 20, 30 -> JDBCType.TIMESTAMP;
      default -> JDBCType.VARCHAR;
    };
  }

  @Override
  public void copyToJsonField(final ResultSet resultSet, final int colIndex, final ObjectNode json)
      throws SQLException {
    final String columnName = resultSet.getMetaData().getColumnName(colIndex);
    String columnTypeName = resultSet.getMetaData().getColumnTypeName(colIndex);
    if (columnTypeName == null) {
      columnTypeName = "";
    }
    switch (columnTypeName) {
      case "autotimestamp" -> putTimestamp(json, columnName, resultSet, colIndex);
      case "money" -> putInteger(json, columnName, resultSet, colIndex);
      case "bfloat4" -> putFloat(json, columnName, resultSet, colIndex);
      case "nchar" -> putString(json, columnName, resultSet, colIndex);
      case "bfloat8" -> putFloat(json, columnName, resultSet, colIndex);
      case "nlongvarchar" -> putString(json, columnName, resultSet, colIndex);
      case "bigidentity" -> putString(json, columnName, resultSet, colIndex);
      case "numeric" -> putInteger(json, columnName, resultSet, colIndex);
      case "bigint" -> putInteger(json, columnName, resultSet, colIndex);
      case "nvarchar" -> putString(json, columnName, resultSet, colIndex);
      case "binary" -> putBoolean(json, columnName, resultSet, colIndex);
      case "real" -> putFloat(json, columnName, resultSet, colIndex);
      case "bit" -> putBoolean(json, columnName, resultSet, colIndex);
      case "smallidentity" -> putInteger(json, columnName, resultSet, colIndex);
      case "char" -> putString(json, columnName, resultSet, colIndex);
      case "smallint" -> putInteger(json, columnName, resultSet, colIndex);
      case "currency" -> putFloat(json, columnName, resultSet, colIndex);
      case "time" -> putTime(json, columnName, resultSet, colIndex);
      case "date" -> putDate(json, columnName, resultSet, colIndex);
      case "timestamp" -> putTimestamp(json, columnName, resultSet, colIndex);
      case "datetime" -> putTimestamp(json, columnName, resultSet, colIndex);
      case "timestamp2" -> putTimestamp(json, columnName, resultSet, colIndex);
      case "decimal" -> putFloat(json, columnName, resultSet, colIndex);
      case "tinyint" -> putInteger(json, columnName, resultSet, colIndex);
      case "double" -> putFloat(json, columnName, resultSet, colIndex);
      case "ubigint" -> putInteger(json, columnName, resultSet, colIndex);
      case "identity" -> putInteger(json, columnName, resultSet, colIndex);
      case "uinteger" -> putInteger(json, columnName, resultSet, colIndex);
      case "integer" -> putInteger(json, columnName, resultSet, colIndex);
      case "usmallint" -> putInteger(json, columnName, resultSet, colIndex);
      case "longvarbinary" -> putString(json, columnName, resultSet, colIndex);
      case "utinyint" -> putInteger(json, columnName, resultSet, colIndex);
      case "longvarchar" -> putString(json, columnName, resultSet, colIndex);
      case "varchar" -> putString(json, columnName, resultSet, colIndex);
      default -> putString(json, columnName, resultSet, colIndex);
    }
  }

  @Override
  protected void putString(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    final String result = resultSet.getString(index);
    if (result != null){
      node.put(columnName, result.trim());
    } else {
      node.put(columnName, result);
    }
  }

}
