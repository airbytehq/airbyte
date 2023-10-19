/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake;

import static io.airbyte.cdk.db.jdbc.DateTimeConverter.putJavaSQLTime;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_COLUMN_NAME;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_COLUMN_TYPE;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_COLUMN_TYPE_NAME;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_SCHEMA_NAME;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_TABLE_NAME;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.jdbc.AbstractJdbcCompatibleSourceOperations;
import io.airbyte.cdk.db.jdbc.DateTimeConverter;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.JsonSchemaType;
import java.math.BigDecimal;
import java.sql.Date;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.LocalDate;
import net.snowflake.client.jdbc.SnowflakeType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeSourceOperations extends AbstractJdbcCompatibleSourceOperations<SnowflakeType> {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeSourceOperations.class);
  public static final String SQL_DIALECT = "snowflake";

  public boolean isCursorType(final SnowflakeType type) {
    return SnowflakeDataSourceUtils.ALLOWED_CURSOR_TYPES.contains(type);
  }

  public void setCursorField(final PreparedStatement preparedStatement,
                             final int parameterIndex,
                             final SnowflakeType cursorFieldType,
                             final String value)
      throws SQLException {
    switch (cursorFieldType) {
      case BOOLEAN -> setBoolean(preparedStatement, parameterIndex, value);
      case INTEGER -> setInteger(preparedStatement, parameterIndex, value);
      case REAL -> setDouble(preparedStatement, parameterIndex, value);
      case FIXED -> setDecimal(preparedStatement, parameterIndex, value);
      case DATE -> setDate(preparedStatement, parameterIndex, value);
      case TIMESTAMP_LTZ, TIMESTAMP_TZ, TIMESTAMP -> setTimestampWithTimezone(preparedStatement, parameterIndex, value);
      case TIMESTAMP_NTZ -> setTimestamp(preparedStatement, parameterIndex, value);
      case TEXT -> setString(preparedStatement, parameterIndex, value);
      case BINARY -> setBinary(preparedStatement, parameterIndex, value);
      // since cursor are expected to be comparable, handle cursor typing strictly and error on
      // unrecognized types
      default -> throw new IllegalArgumentException(String.format("%s cannot be used as a cursor.", cursorFieldType));
    }
  }

  @Override
  protected void putDouble(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) {
    try {
      final double value = resultSet.getDouble(index);
      node.put(columnName, value);
    } catch (final SQLException e) {
      node.put(columnName, (Double) null);
    }
  }

  public JDBCType getDatabaseJDBCType(final JsonNode field) {
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
  public SnowflakeType getDatabaseFieldType(final JsonNode field) {
    try {
      final String typeName = field.get(INTERNAL_COLUMN_TYPE_NAME).asText();
      return getDatabaseFieldType(typeName);
    } catch (final IllegalArgumentException ex) {
      LOGGER.warn(String.format("Could not convert column: %s from table: %s.%s with type: %s. Casting to VARCHAR.",
          field.get(INTERNAL_COLUMN_NAME),
          field.get(INTERNAL_SCHEMA_NAME),
          field.get(INTERNAL_TABLE_NAME),
          field.get(INTERNAL_COLUMN_TYPE)));
      return SnowflakeType.TEXT;
    }
  }

  public SnowflakeType getDatabaseFieldType(final String internalSnowflakeTypeName) throws IllegalArgumentException {
    try {
      return SnowflakeType.fromString(internalSnowflakeTypeName);
    } catch (final IllegalArgumentException ex) {
      LOGGER.error(String.format("Could not detect Snowflake type from type name '%s'.", internalSnowflakeTypeName));
      throw ex;
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

  protected void setTimestampWithTimezone(final PreparedStatement preparedStatement, final int parameterIndex, final String value)
      throws SQLException {
    preparedStatement.setString(parameterIndex, value);
  }

  protected void setTimeWithTimezone(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    preparedStatement.setString(parameterIndex, value);
  }

  public JsonNode getAirbyteSourceType(final JDBCType jdbcType) {
    // Return a json node containing the database dialect and the source type
    return Jsons.jsonNode(
        ImmutableMap.builder()
            .put("dialect", SQL_DIALECT)
            .put("type", jdbcType.getName())
            .build());
  }

  public JsonSchemaType getAirbyteTypeFromJDBCType(final JDBCType jdbcType) {
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
  public JsonSchemaType getAirbyteType(SnowflakeType snowflakeType) {
    switch (snowflakeType) {
      case BINARY -> {
        return JsonSchemaType.BINARY_DATA_V1;
      }
      case BOOLEAN -> {
        return JsonSchemaType.BOOLEAN;
      }
      case CHAR, TEXT -> {
        return JsonSchemaType.STRING;
      }
      case DATE -> {
        return JsonSchemaType.DATE_V1;
      }
      case FIXED -> {
        return JsonSchemaType.NUMBER_V1;
      }
      case INTEGER -> {
        return JsonSchemaType.INTEGER_V1;
      }
      case REAL -> {
        return JsonSchemaType.NUMBER;
      }
      case ARRAY -> {
        return JsonSchemaType.ARRAY;
      }
      case TIME -> {
        return JsonSchemaType.TIME_WITHOUT_TIMEZONE_V1;
      }
      case TIMESTAMP, TIMESTAMP_NTZ -> {
        return JsonSchemaType.TIMESTAMP_WITHOUT_TIMEZONE_V1;
      }
      case TIMESTAMP_TZ, TIMESTAMP_LTZ -> {
        return JsonSchemaType.TIMESTAMP_WITH_TIMEZONE_V1;
      }
      case ANY, OBJECT, VARIANT, GEOGRAPHY, GEOMETRY -> {
        // Failsafe type is 'string'.
        return JsonSchemaType.STRING;
      }
      default -> {
        // Failsafe type is 'string'.
        return JsonSchemaType.STRING;
      }
    }
  }

  @Override
  public void copyToJsonField(final ResultSet resultSet, final int colIndex, final ObjectNode json) throws SQLException {
    final String columnName = resultSet.getMetaData().getColumnName(colIndex);
    final String columnTypeName = resultSet.getMetaData().getColumnTypeName(colIndex).toUpperCase();
    final SnowflakeType snowflakeType = getDatabaseFieldType(columnTypeName);

    final String stringValue = resultSet.getString(colIndex);
    if (stringValue == null) {
      json.putNull(columnName);
    } else {
      switch (snowflakeType) {
        case BINARY -> putBinary(json, columnName, resultSet, colIndex);
        case BOOLEAN -> putBoolean(json, columnName, resultSet, colIndex);
        case CHAR, TEXT -> putString(json, columnName, resultSet, colIndex);
        case DATE -> putDate(json, columnName, resultSet, colIndex);
        case FIXED -> putBigDecimal(json, columnName, resultSet, colIndex);
        case INTEGER -> putInteger(json, columnName, resultSet, colIndex);
        case REAL -> putFloat(json, columnName, resultSet, colIndex);
        case TIME -> putTime(json, columnName, resultSet, colIndex);
        case TIMESTAMP_LTZ, TIMESTAMP_TZ -> putTimestampWithTimezone(json, columnName, resultSet, colIndex);

        // Note: TIMESTAMP type is configurable by the user, defaults to NTZ:
        // https://docs.snowflake.com/en/sql-reference/data-types-datetime#timestamp
        case TIMESTAMP_NTZ, TIMESTAMP -> putTimestamp(json, columnName, resultSet, colIndex);

        // TODO: Improve handling of complex types:
        case ANY -> json.put(columnName, stringValue);
        case ARRAY -> json.put(columnName, stringValue);
        case GEOGRAPHY -> json.put(columnName, stringValue);
        case GEOMETRY -> json.put(columnName, stringValue);
        case OBJECT -> json.put(columnName, stringValue);
        case VARIANT -> json.put(columnName, stringValue);

        // For any other type, write as string:
        default -> json.put(columnName, stringValue);
      }
    }
  }

  @Override
  protected void setDate(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    final LocalDate date = LocalDate.parse(value);
    preparedStatement.setDate(parameterIndex, Date.valueOf(date));
  }

  @Override
  protected void putTimestampWithTimezone(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index)
      throws SQLException {
    final Timestamp timestamp = resultSet.getTimestamp(index);
    node.put(columnName, DateTimeConverter.convertToTimestampWithTimezone(timestamp));
  }

  @Override
  protected void putTimestamp(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    final Timestamp timestamp = resultSet.getTimestamp(index);
    node.put(columnName, DateTimeConverter.convertToTimestamp(timestamp));
  }

  @Override
  protected void putTime(final ObjectNode node,
                         final String columnName,
                         final ResultSet resultSet,
                         final int index)
      throws SQLException {
    putJavaSQLTime(node, columnName, resultSet, index);
  }

}
