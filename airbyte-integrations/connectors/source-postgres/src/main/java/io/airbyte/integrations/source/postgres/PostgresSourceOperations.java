/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.db.jdbc.JdbcConstants.INTERNAL_COLUMN_NAME;
import static io.airbyte.db.jdbc.JdbcConstants.INTERNAL_COLUMN_TYPE;
import static io.airbyte.db.jdbc.JdbcConstants.INTERNAL_COLUMN_TYPE_NAME;
import static io.airbyte.db.jdbc.JdbcConstants.INTERNAL_SCHEMA_NAME;
import static io.airbyte.db.jdbc.JdbcConstants.INTERNAL_TABLE_NAME;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.DataTypeUtils;
import io.airbyte.db.jdbc.DateTimeConverter;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import io.airbyte.protocol.models.JsonSchemaType;
import java.math.BigDecimal;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.OffsetDateTime;
import java.time.OffsetTime;
import java.time.format.DateTimeParseException;
import java.util.Collections;
import org.postgresql.geometric.PGbox;
import org.postgresql.geometric.PGcircle;
import org.postgresql.geometric.PGline;
import org.postgresql.geometric.PGlseg;
import org.postgresql.geometric.PGpath;
import org.postgresql.geometric.PGpoint;
import org.postgresql.geometric.PGpolygon;
import org.postgresql.jdbc.PgResultSetMetaData;
import org.postgresql.util.PGobject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresSourceOperations extends JdbcSourceOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresSourceOperations.class);
  private static final String TIMESTAMPTZ = "timestamptz";
  private static final String TIMETZ = "timetz";
  private static final ObjectMapper OBJECT_MAPPER = MoreMappers.initMapper();

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
  public void setStatementField(final PreparedStatement preparedStatement,
                                final int parameterIndex,
                                final JDBCType cursorFieldType,
                                final String value)
      throws SQLException {
    switch (cursorFieldType) {

      case TIMESTAMP -> setTimestamp(preparedStatement, parameterIndex, value);
      case TIMESTAMP_WITH_TIMEZONE -> setTimestampWithTimezone(preparedStatement, parameterIndex, value);
      case TIME -> setTime(preparedStatement, parameterIndex, value);
      case TIME_WITH_TIMEZONE -> setTimeWithTimezone(preparedStatement, parameterIndex, value);
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

  private void setTimeWithTimezone(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    try {
      preparedStatement.setObject(parameterIndex, OffsetTime.parse(value));
    } catch (final DateTimeParseException e) {
      // attempt to parse the time w/o timezone. This can be caused by schema created with a different
      // version of the connector
      preparedStatement.setObject(parameterIndex, LocalTime.parse(value));
    }
  }

  private void setTimestampWithTimezone(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    try {
      preparedStatement.setObject(parameterIndex, OffsetDateTime.parse(value));
    } catch (final DateTimeParseException e) {
      // attempt to parse the datetime w/o timezone. This can be caused by schema created with a different
      // version of the connector
      preparedStatement.setObject(parameterIndex, LocalDateTime.parse(value));
    }
  }

  @Override
  protected void setTimestamp(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    try {
      preparedStatement.setObject(parameterIndex, LocalDateTime.parse(value));
    } catch (final DateTimeParseException e) {
      // attempt to parse the datetime with timezone. This can be caused by schema created with an older
      // version of the connector
      preparedStatement.setObject(parameterIndex, OffsetDateTime.parse(value));
    }
  }

  @Override
  protected void setTime(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    try {
      preparedStatement.setObject(parameterIndex, LocalTime.parse(value));
    } catch (final DateTimeParseException e) {
      // attempt to parse the datetime with timezone. This can be caused by schema created with an older
      // version of the connector
      preparedStatement.setObject(parameterIndex, OffsetTime.parse(value));
    }
  }

  @Override
  protected void setDate(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    preparedStatement.setObject(parameterIndex, LocalDate.parse(value));
  }

  @Override
  public void setJsonField(final ResultSet resultSet, final int colIndex, final ObjectNode json) throws SQLException {
    final PgResultSetMetaData metadata = (PgResultSetMetaData) resultSet.getMetaData();
    final String columnName = metadata.getColumnName(colIndex);
    final String columnTypeName = metadata.getColumnTypeName(colIndex).toLowerCase();
    final JDBCType columnType = safeGetJdbcType(metadata.getColumnType(colIndex));
    if (resultSet.getString(colIndex) == null) {
      json.putNull(columnName);
    } else {
      switch (columnTypeName) {
        case "bool", "boolean" -> putBoolean(json, columnName, resultSet, colIndex);
        case "bytea" -> putString(json, columnName, resultSet, colIndex);
        case TIMETZ -> putTimeWithTimezone(json, columnName, resultSet, colIndex);
        case TIMESTAMPTZ -> putTimestampWithTimezone(json, columnName, resultSet, colIndex);
        case "hstore" -> putHstoreAsJson(json, columnName, resultSet, colIndex);
        case "circle" -> putObject(json, columnName, resultSet, colIndex, PGcircle.class);
        case "box" -> putObject(json, columnName, resultSet, colIndex, PGbox.class);
        case "double precision", "float", "float8" -> putDouble(json, columnName, resultSet, colIndex);
        case "line" -> putObject(json, columnName, resultSet, colIndex, PGline.class);
        case "lseg" -> putObject(json, columnName, resultSet, colIndex, PGlseg.class);
        case "path" -> putObject(json, columnName, resultSet, colIndex, PGpath.class);
        case "point" -> putObject(json, columnName, resultSet, colIndex, PGpoint.class);
        case "polygon" -> putObject(json, columnName, resultSet, colIndex, PGpolygon.class);
        default -> {
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
    }
  }

  @Override
  protected void putDate(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    node.put(columnName, DateTimeConverter.convertToDate(getObject(resultSet, index, LocalDate.class)));
  }

  @Override
  protected void putTime(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    node.put(columnName, DateTimeConverter.convertToTime(getObject(resultSet, index, LocalTime.class)));
  }

  @Override
  protected void putTimestamp(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    node.put(columnName, DateTimeConverter.convertToTimestamp(resultSet.getTimestamp(index)));
  }

  @Override
  public JDBCType getFieldType(final JsonNode field) {
    try {
      final String typeName = field.get(INTERNAL_COLUMN_TYPE_NAME).asText().toLowerCase();
      // Postgres boolean is mapped to JDBCType.BIT, but should be BOOLEAN
      return switch (typeName) {
        case "bool", "boolean" -> JDBCType.BOOLEAN;
        // BYTEA is variable length binary string with hex output format by default (e.g. "\x6b707a").
        // It should not be converted to base64 binary string. So it is represented as JDBC VARCHAR.
        // https://www.postgresql.org/docs/14/datatype-binary.html
        case "bytea" -> JDBCType.VARCHAR;
        case TIMESTAMPTZ -> JDBCType.TIMESTAMP_WITH_TIMEZONE;
        case TIMETZ -> JDBCType.TIME_WITH_TIMEZONE;
        default -> JDBCType.valueOf(field.get(INTERNAL_COLUMN_TYPE).asInt());
      };
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
  public JsonSchemaType getJsonType(final JDBCType jdbcType) {
    return switch (jdbcType) {
      case BOOLEAN -> JsonSchemaType.BOOLEAN;
      case TINYINT, SMALLINT, INTEGER, BIGINT -> JsonSchemaType.INTEGER;
      case FLOAT, DOUBLE, REAL, NUMERIC, DECIMAL -> JsonSchemaType.NUMBER;
      case BLOB, BINARY, VARBINARY, LONGVARBINARY -> JsonSchemaType.STRING_BASE_64;
      case ARRAY -> JsonSchemaType.ARRAY;
      case DATE -> JsonSchemaType.STRING_DATE;
      case TIME -> JsonSchemaType.STRING_TIME_WITHOUT_TIMEZONE;
      case TIME_WITH_TIMEZONE -> JsonSchemaType.STRING_TIME_WITH_TIMEZONE;
      case TIMESTAMP -> JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE;
      case TIMESTAMP_WITH_TIMEZONE -> JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE;

      default -> JsonSchemaType.STRING;
    };
  }

  @Override
  protected void putBoolean(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    node.put(columnName, resultSet.getString(index).equalsIgnoreCase("t"));
  }

  protected <T extends PGobject> void putObject(final ObjectNode node,
                                                final String columnName,
                                                final ResultSet resultSet,
                                                final int index,
                                                Class<T> clazz)
      throws SQLException {
    final T object = getObject(resultSet, index, clazz);
    node.put(columnName, object.getValue());
  }

  @Override
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

  private void putHstoreAsJson(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index)
      throws SQLException {
    final var data = resultSet.getObject(index);
    try {
      node.put(columnName, OBJECT_MAPPER.writeValueAsString(data));
    } catch (final JsonProcessingException e) {
      throw new RuntimeException("Could not parse 'hstore' value:" + e);
    }
  }

  /**
   * @return monetary value in numbers without the currency symbol or thousands separators.
   */
  @VisibleForTesting
  static String parseMoneyValue(final String moneyString) {
    return moneyString.replaceAll("[^\\d.-]", "");
  }

  @Override
  public boolean isCursorType(JDBCType type) {
    return PostgresUtils.ALLOWED_CURSOR_TYPES.contains(type);
  }

}
