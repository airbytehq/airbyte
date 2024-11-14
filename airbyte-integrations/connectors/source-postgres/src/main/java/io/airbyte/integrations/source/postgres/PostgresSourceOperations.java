/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.cdk.db.DataTypeUtils.TIMESTAMPTZ_FORMATTER;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_COLUMN_NAME;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_COLUMN_TYPE;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_COLUMN_TYPE_NAME;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_DECIMAL_DIGITS;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_SCHEMA_NAME;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_TABLE_NAME;
import static io.airbyte.integrations.source.postgres.PostgresType.safeGetJdbcType;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.BinaryNode;
import com.fasterxml.jackson.databind.node.NullNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.cdk.db.DataTypeUtils;
import io.airbyte.cdk.db.SourceOperations;
import io.airbyte.cdk.db.jdbc.AbstractJdbcCompatibleSourceOperations;
import io.airbyte.cdk.db.jdbc.DateTimeConverter;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.JsonSchemaPrimitiveUtil.JsonSchemaPrimitive;
import io.airbyte.protocol.models.JsonSchemaType;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.sql.Date;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.*;
import java.time.format.DateTimeParseException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import org.postgresql.PGStatement;
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

public class PostgresSourceOperations extends AbstractJdbcCompatibleSourceOperations<PostgresType>
    implements SourceOperations<ResultSet, PostgresType> {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresSourceOperations.class);
  private static final String TIMESTAMPTZ = "timestamptz";
  private static final String TIMETZ = "timetz";
  private static final ObjectMapper OBJECT_MAPPER = MoreMappers.initMapper();
  private static final Map<Integer, PostgresType> POSTGRES_TYPE_DICT = new HashMap<>();
  private final Map<String, Map<String, ColumnInfo>> streamColumnInfo = new HashMap<>();

  private static final String POSITIVE_INFINITY_STRING = "Infinity";
  private static final String NEGATIVE_INFINITY_STRING = "-Infinity";
  private static final Date POSITIVE_INFINITY_DATE = new Date(PGStatement.DATE_POSITIVE_INFINITY);
  private static final Date NEGATIVE_INFINITY_DATE = new Date(PGStatement.DATE_NEGATIVE_INFINITY);
  private static final Timestamp POSITIVE_INFINITY_TIMESTAMP = new Timestamp(PGStatement.DATE_POSITIVE_INFINITY);
  private static final Timestamp NEGATIVE_INFINITY_TIMESTAMP = new Timestamp(PGStatement.DATE_NEGATIVE_INFINITY);
  private static final OffsetDateTime POSITIVE_INFINITY_OFFSET_DATE_TIME = OffsetDateTime.MAX;
  private static final OffsetDateTime NEGATIVE_INFINITY_OFFSET_DATE_TIME = OffsetDateTime.MIN;

  static {
    Arrays.stream(PostgresType.class.getEnumConstants()).forEach(c -> POSTGRES_TYPE_DICT.put(c.type, c));
  }

  @Override
  public void setCursorField(final PreparedStatement preparedStatement,
                             final int parameterIndex,
                             final PostgresType cursorFieldType,
                             final String value)
      throws SQLException {

    LOGGER.warn("SGX setCursorField value=" + value + "cursorFieldType=" + cursorFieldType);
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
  protected void setDate(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    preparedStatement.setObject(parameterIndex, LocalDate.parse(value));
  }

  @Override
  public void copyToJsonField(final ResultSet resultSet, final int colIndex, final ObjectNode json) throws SQLException {
    final PgResultSetMetaData metadata = (PgResultSetMetaData) resultSet.getMetaData();
    final String columnName = metadata.getColumnName(colIndex);
    final ColumnInfo columnInfo = getColumnInfo(colIndex, metadata, columnName);
    final String value = resultSet.getString(colIndex);
    if (value == null) {
      json.putNull(columnName);
    } else {
      switch (columnInfo.columnTypeName) {
        case "bool", "boolean" -> putBoolean(json, columnName, resultSet, colIndex);
        case "bytea" -> json.put(columnName, value);
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
        case "_varchar", "_char", "_bpchar", "_text", "_name" -> putArray(json, columnName, resultSet, colIndex);
        case "_int2", "_int4", "_int8", "_oid" -> putLongArray(json, columnName, resultSet, colIndex);
        case "_numeric", "_decimal" -> {
          // If a numeric_array column precision is not 0 AND scale is 0,
          // then we know the precision and scale are purposefully chosen
          if (metadata.getPrecision(colIndex) != 0 && metadata.getScale(colIndex) == 0) {
            putBigIntegerArray(json, columnName, resultSet, colIndex);
          } else {
            putBigDecimalArray(json, columnName, resultSet, colIndex);
          }
        }
        case "_money" -> putMoneyArray(json, columnName, resultSet, colIndex);
        case "_float4", "_float8" -> putDoubleArray(json, columnName, resultSet, colIndex);
        case "_bool" -> putBooleanArray(json, columnName, resultSet, colIndex);
        case "_bit" -> putBitArray(json, columnName, resultSet, colIndex);
        case "_bytea" -> putByteaArray(json, columnName, resultSet, colIndex);
        case "_date" -> putDateArray(json, columnName, resultSet, colIndex);
        case "_timestamptz" -> putTimestampTzArray(json, columnName, resultSet, colIndex);
        case "_timestamp" -> putTimestampArray(json, columnName, resultSet, colIndex);
        case "_timetz" -> putTimeTzArray(json, columnName, resultSet, colIndex);
        case "_time" -> putTimeArray(json, columnName, resultSet, colIndex);
        default -> {
          switch (columnInfo.columnType) {
            case BOOLEAN -> json.put(columnName, value.equalsIgnoreCase("t"));
            case TINYINT, SMALLINT -> putShortInt(json, columnName, resultSet, colIndex);
            case INTEGER -> putInteger(json, columnName, resultSet, colIndex);
            case BIGINT -> putBigInt(json, columnName, resultSet, colIndex);
            case FLOAT, DOUBLE -> putDouble(json, columnName, resultSet, colIndex);
            case REAL -> putFloat(json, columnName, resultSet, colIndex);
            case NUMERIC, DECIMAL -> {
              if (metadata.getPrecision(colIndex) != 0 && metadata.getScale(colIndex) == 0) {
                putBigInteger(json, columnName, resultSet, colIndex);
              } else {
                putBigDecimal(json, columnName, resultSet, colIndex);
              }
            }
            // BIT is a bit string in Postgres, e.g. '0100'
            case BIT, CHAR, VARCHAR, LONGVARCHAR -> json.put(columnName, value);
            case DATE -> putDate(json, columnName, resultSet, colIndex);
            case TIME -> putTime(json, columnName, resultSet, colIndex);
            case TIMESTAMP -> putTimestamp(json, columnName, resultSet, colIndex);
            case BLOB, BINARY, VARBINARY, LONGVARBINARY -> putBinary(json, columnName, resultSet, colIndex);
            case ARRAY -> putArray(json, columnName, resultSet, colIndex);
            default -> {
              if (columnInfo.columnType.isArrayType()) {
                putArray(json, columnName, resultSet, colIndex);
              } else {
                json.put(columnName, value);
              }
            }
          }
        }
      }
    }
  }

  private void putTimeArray(final ObjectNode node, final String columnName, final ResultSet resultSet, final int colIndex) throws SQLException {
    final ArrayNode arrayNode = Jsons.arrayNode();
    final ResultSet arrayResultSet = resultSet.getArray(colIndex).getResultSet();
    while (arrayResultSet.next()) {
      final LocalTime time = getObject(arrayResultSet, 2, LocalTime.class);
      if (time == null) {
        arrayNode.add(NullNode.getInstance());
      } else {
        arrayNode.add(DateTimeConverter.convertToTime(time));
      }
    }
    node.set(columnName, arrayNode);
  }

  private void putTimeTzArray(final ObjectNode node, final String columnName, final ResultSet resultSet, final int colIndex) throws SQLException {
    final ArrayNode arrayNode = Jsons.arrayNode();
    final ResultSet arrayResultSet = resultSet.getArray(colIndex).getResultSet();
    while (arrayResultSet.next()) {
      final OffsetTime timetz = getObject(arrayResultSet, 2, OffsetTime.class);
      if (timetz == null) {
        arrayNode.add(NullNode.getInstance());
      } else {
        arrayNode.add(DateTimeConverter.convertToTimeWithTimezone(timetz));
      }
    }
    node.set(columnName, arrayNode);
  }

  private void putTimestampArray(final ObjectNode node, final String columnName, final ResultSet resultSet, final int colIndex) throws SQLException {
    final ArrayNode arrayNode = Jsons.arrayNode();
    final ResultSet arrayResultSet = resultSet.getArray(colIndex).getResultSet();
    while (arrayResultSet.next()) {
      final Timestamp timestamp = arrayResultSet.getTimestamp(2);
      if (timestamp == null) {
        arrayNode.add(NullNode.getInstance());
      } else if (POSITIVE_INFINITY_TIMESTAMP.equals(timestamp)) {
        arrayNode.add(POSITIVE_INFINITY_STRING);
      } else if (NEGATIVE_INFINITY_TIMESTAMP.equals(timestamp)) {
        arrayNode.add(NEGATIVE_INFINITY_STRING);
      } else {
        arrayNode.add(DateTimeConverter.convertToTimestamp(timestamp));
      }
    }
    node.set(columnName, arrayNode);
  }

  private void putTimestampTzArray(final ObjectNode node, final String columnName, final ResultSet resultSet, final int colIndex)
      throws SQLException {
    final ArrayNode arrayNode = Jsons.arrayNode();
    final ResultSet arrayResultSet = resultSet.getArray(colIndex).getResultSet();
    while (arrayResultSet.next()) {
      final OffsetDateTime timestamptz = getObject(arrayResultSet, 2, OffsetDateTime.class);
      if (timestamptz == null) {
        arrayNode.add(NullNode.getInstance());
      } else if (POSITIVE_INFINITY_OFFSET_DATE_TIME.equals(timestamptz)) {
        arrayNode.add(POSITIVE_INFINITY_STRING);
      } else if (NEGATIVE_INFINITY_OFFSET_DATE_TIME.equals(timestamptz)) {
        arrayNode.add(NEGATIVE_INFINITY_STRING);
      } else {
        final LocalDate localDate = timestamptz.toLocalDate();
        arrayNode.add(resolveEra(localDate, timestamptz.format(TIMESTAMPTZ_FORMATTER)));
      }
    }
    node.set(columnName, arrayNode);
  }

  private void putDateArray(final ObjectNode node, final String columnName, final ResultSet resultSet, final int colIndex) throws SQLException {
    final ArrayNode arrayNode = Jsons.arrayNode();
    final ResultSet arrayResultSet = resultSet.getArray(colIndex).getResultSet();
    while (arrayResultSet.next()) {
      final Date date = getObject(arrayResultSet, 2, Date.class);
      if (date == null) {
        arrayNode.add(NullNode.getInstance());
      } else if (POSITIVE_INFINITY_DATE.equals(date)) {
        arrayNode.add(POSITIVE_INFINITY_STRING);
      } else if (NEGATIVE_INFINITY_DATE.equals(date)) {
        arrayNode.add(NEGATIVE_INFINITY_STRING);
      } else {
        arrayNode.add(DateTimeConverter.convertToDate(date));
      }
    }
    node.set(columnName, arrayNode);
  }

  private void putByteaArray(final ObjectNode node, final String columnName, final ResultSet resultSet, final int colIndex) throws SQLException {
    final ArrayNode arrayNode = Jsons.arrayNode();
    final ResultSet arrayResultSet = resultSet.getArray(colIndex).getResultSet();
    while (arrayResultSet.next()) {
      arrayNode.add(new BinaryNode(arrayResultSet.getBytes(2)));
    }
    node.set(columnName, arrayNode);
  }

  private void putBitArray(final ObjectNode node, final String columnName, final ResultSet resultSet, final int colIndex) throws SQLException {
    final ArrayNode arrayNode = Jsons.arrayNode();
    final ResultSet arrayResultSet = resultSet.getArray(colIndex).getResultSet();
    while (arrayResultSet.next()) {
      final String res = arrayResultSet.getString(2);
      if (res == null) {
        arrayNode.add(NullNode.getInstance());
      } else {
        arrayNode.add("1".equals(res));
      }
    }
    node.set(columnName, arrayNode);
  }

  private void putBooleanArray(final ObjectNode node, final String columnName, final ResultSet resultSet, final int colIndex) throws SQLException {
    final ArrayNode arrayNode = Jsons.arrayNode();
    final ResultSet arrayResultSet = resultSet.getArray(colIndex).getResultSet();
    while (arrayResultSet.next()) {
      final String res = arrayResultSet.getString(2);
      if (res == null) {
        arrayNode.add(NullNode.getInstance());
      } else {
        arrayNode.add("t".equalsIgnoreCase(res));
      }
    }
    node.set(columnName, arrayNode);
  }

  private void putBigDecimalArray(final ObjectNode node, final String columnName, final ResultSet resultSet, final int colIndex) throws SQLException {
    final ArrayNode arrayNode = Jsons.arrayNode();
    final ResultSet arrayResultSet = resultSet.getArray(colIndex).getResultSet();
    while (arrayResultSet.next()) {
      final BigDecimal bigDecimal = DataTypeUtils.throwExceptionIfInvalid(() -> arrayResultSet.getBigDecimal(2));
      if (bigDecimal != null) {
        arrayNode.add(bigDecimal);
      } else {
        arrayNode.add((BigDecimal) null);
      }
    }
    node.set(columnName, arrayNode);
  }

  private void putBigIntArray(final ObjectNode node, final String columnName, final ResultSet resultSet, final int colIndex) throws SQLException {
    final ArrayNode arrayNode = Jsons.arrayNode();
    final ResultSet arrayResultSet = resultSet.getArray(colIndex).getResultSet();
    while (arrayResultSet.next()) {
      final long value = DataTypeUtils.throwExceptionIfInvalid(() -> arrayResultSet.getLong(2));
      arrayNode.add(value);
    }
    node.set(columnName, arrayNode);
  }

  private void putBigIntegerArray(final ObjectNode node, final String columnName, final ResultSet resultSet, final int colIndex) throws SQLException {
    final ArrayNode arrayNode = Jsons.arrayNode();
    final ResultSet arrayResultSet = resultSet.getArray(colIndex).getResultSet();
    while (arrayResultSet.next()) {
      final BigInteger value = DataTypeUtils.throwExceptionIfInvalid(() -> arrayResultSet.getBigDecimal(2).toBigInteger());
      arrayNode.add(value);
    }
    node.set(columnName, arrayNode);
  }

  private void putDoubleArray(final ObjectNode node, final String columnName, final ResultSet resultSet, final int colIndex) throws SQLException {
    final ArrayNode arrayNode = Jsons.arrayNode();
    final ResultSet arrayResultSet = resultSet.getArray(colIndex).getResultSet();
    while (arrayResultSet.next()) {
      arrayNode.add(DataTypeUtils.throwExceptionIfInvalid(() -> arrayResultSet.getDouble(2), Double::isFinite));
    }
    node.set(columnName, arrayNode);
  }

  private void putMoneyArray(final ObjectNode node, final String columnName, final ResultSet resultSet, final int colIndex) throws SQLException {
    final ArrayNode arrayNode = Jsons.arrayNode();
    final ResultSet arrayResultSet = resultSet.getArray(colIndex).getResultSet();
    while (arrayResultSet.next()) {
      final String moneyValue = parseMoneyValue(arrayResultSet.getString(2));
      arrayNode.add(
          DataTypeUtils.throwExceptionIfInvalid(() -> DataTypeUtils.throwExceptionIfInvalid(() -> Double.valueOf(moneyValue), Double::isFinite)));
    }
    node.set(columnName, arrayNode);
  }

  private void putLongArray(final ObjectNode node, final String columnName, final ResultSet resultSet, final int colIndex) throws SQLException {
    final ArrayNode arrayNode = Jsons.arrayNode();
    final ResultSet arrayResultSet = resultSet.getArray(colIndex).getResultSet();
    while (arrayResultSet.next()) {
      arrayNode.add(arrayResultSet.getLong(2));
    }
    node.set(columnName, arrayNode);
  }

  @Override
  protected void putDate(ObjectNode node, String columnName, ResultSet resultSet, int index) throws SQLException {
    Date dateFromResultSet = resultSet.getDate(index);
    if (POSITIVE_INFINITY_DATE.equals(dateFromResultSet)) {
      node.put(columnName, POSITIVE_INFINITY_STRING);
    } else if (NEGATIVE_INFINITY_DATE.equals(dateFromResultSet)) {
      node.put(columnName, NEGATIVE_INFINITY_STRING);
    } else {
      super.putDate(node, columnName, resultSet, index);
    }
  }

  @Override
  protected void putTime(ObjectNode node, String columnName, ResultSet resultSet, int index) throws SQLException {
    super.putTime(node, columnName, resultSet, index);
  }

  @Override
  protected void putTimestamp(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    Timestamp timestampFromResultSet = resultSet.getTimestamp(index);
    String strValue = resultSet.getString(index);
    if (POSITIVE_INFINITY_TIMESTAMP.equals(timestampFromResultSet)) {
      node.put(columnName, POSITIVE_INFINITY_STRING);
    } else if (NEGATIVE_INFINITY_TIMESTAMP.equals(timestampFromResultSet)) {
      node.put(columnName, NEGATIVE_INFINITY_STRING);
    } else {
      node.put(columnName, DateTimeConverter.convertToTimestamp(timestampFromResultSet));
    }
  }

  @Override
  protected void putTimeWithTimezone(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    final OffsetTime timetz = getObject(resultSet, index, OffsetTime.class);
    node.put(columnName, DateTimeConverter.convertToTimeWithTimezone(timetz));
  }

  @Override
  protected void putTimestampWithTimezone(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index)
      throws SQLException {
    final OffsetDateTime timestampTz = getObject(resultSet, index, OffsetDateTime.class);
    final String timestampTzVal;
    if (POSITIVE_INFINITY_OFFSET_DATE_TIME.equals(timestampTz)) {
      timestampTzVal = POSITIVE_INFINITY_STRING;
    } else if (NEGATIVE_INFINITY_OFFSET_DATE_TIME.equals(timestampTz)) {
      timestampTzVal = NEGATIVE_INFINITY_STRING;
    } else {
      final LocalDate localDate = timestampTz.toLocalDate();
      timestampTzVal = resolveEra(localDate, timestampTz.format(TIMESTAMPTZ_FORMATTER));
    }

    node.put(columnName, timestampTzVal);
  }

  @Override
  public PostgresType getDatabaseFieldType(final JsonNode field) {
    try {
      final String typeName = field.get(INTERNAL_COLUMN_TYPE_NAME).asText().toLowerCase();
      // Postgres boolean is mapped to JDBCType.BIT, but should be BOOLEAN
      return switch (typeName) {
        case "_bit" -> PostgresType.BIT_ARRAY;
        case "_bool" -> PostgresType.BOOL_ARRAY;
        case "_name" -> PostgresType.NAME_ARRAY;
        case "_varchar" -> PostgresType.VARCHAR_ARRAY;
        case "_char" -> PostgresType.CHAR_ARRAY;
        case "_bpchar" -> PostgresType.BPCHAR_ARRAY;
        case "_text" -> PostgresType.TEXT_ARRAY;
        case "_int4" -> PostgresType.INT4_ARRAY;
        case "_int2" -> PostgresType.INT2_ARRAY;
        case "_int8" -> PostgresType.INT8_ARRAY;
        case "_money" -> PostgresType.MONEY_ARRAY;
        case "_oid" -> PostgresType.OID_ARRAY;
        case "_numeric" -> PostgresType.NUMERIC_ARRAY;
        case "_float4" -> PostgresType.FLOAT4_ARRAY;
        case "_float8" -> PostgresType.FLOAT8_ARRAY;
        case "_timestamptz" -> PostgresType.TIMESTAMPTZ_ARRAY;
        case "_timestamp" -> PostgresType.TIMESTAMP_ARRAY;
        case "_timetz" -> PostgresType.TIMETZ_ARRAY;
        case "_time" -> PostgresType.TIME_ARRAY;
        case "_date" -> PostgresType.DATE_ARRAY;
        case "_bytea" -> PostgresType.BYTEA_ARRAY;
        case "bool", "boolean" -> PostgresType.BOOLEAN;
        // BYTEA is variable length binary string with hex output format by default (e.g. "\x6b707a").
        // It should not be converted to base64 binary string. So it is represented as JDBC VARCHAR.
        // https://www.postgresql.org/docs/14/datatype-binary.html
        case "bytea" -> PostgresType.VARCHAR;
        case "numeric", "decimal" -> {
          if (field.get(INTERNAL_DECIMAL_DIGITS) != null && field.get(INTERNAL_DECIMAL_DIGITS).asInt() == 0) {
            yield PostgresType.BIGINT;
          } else {
            yield PostgresType.valueOf(field.get(INTERNAL_COLUMN_TYPE).asInt(), POSTGRES_TYPE_DICT);
          }
        }
        case TIMESTAMPTZ -> PostgresType.TIMESTAMP_WITH_TIMEZONE;
        case TIMETZ -> PostgresType.TIME_WITH_TIMEZONE;
        default -> PostgresType.valueOf(field.get(INTERNAL_COLUMN_TYPE).asInt(), POSTGRES_TYPE_DICT);
      };
    } catch (final IllegalArgumentException ex) {
      LOGGER.warn(String.format("Could not convert column: %s from table: %s.%s with type: %s. Casting to VARCHAR.",
          field.get(INTERNAL_COLUMN_NAME),
          field.get(INTERNAL_SCHEMA_NAME),
          field.get(INTERNAL_TABLE_NAME),
          field.get(INTERNAL_COLUMN_TYPE)));
      return PostgresType.VARCHAR;
    }
  }

  @Override
  public JsonSchemaType getAirbyteType(final PostgresType jdbcType) {
    return switch (jdbcType) {
      case BOOLEAN -> JsonSchemaType.BOOLEAN;
      case TINYINT, SMALLINT, INTEGER, BIGINT -> JsonSchemaType.INTEGER;
      case FLOAT, DOUBLE, REAL, NUMERIC, DECIMAL -> JsonSchemaType.NUMBER;
      case BLOB, BINARY, VARBINARY, LONGVARBINARY -> JsonSchemaType.STRING_BASE_64;
      case ARRAY -> JsonSchemaType.ARRAY;
      case BIT_ARRAY -> JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
          .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.BOOLEAN)
              .build())
          .build();
      case BOOL_ARRAY -> JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
          .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.BOOLEAN)
              .build())
          .build();
      case BYTEA_ARRAY -> JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
          .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.STRING)
              .build())
          .build();
      case NAME_ARRAY -> JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
          .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.STRING)
              .build())
          .build();
      case VARCHAR_ARRAY -> JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
          .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.STRING)
              .build())
          .build();
      case CHAR_ARRAY -> JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
          .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.STRING)
              .build())
          .build();
      case BPCHAR_ARRAY -> JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
          .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.STRING)
              .build())
          .build();
      case TEXT_ARRAY -> JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
          .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.STRING)
              .build())
          .build();
      case INT4_ARRAY -> JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
          .withItems(JsonSchemaType.INTEGER)
          .build();
      case INT2_ARRAY -> JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
          .withItems(JsonSchemaType.INTEGER)
          .build();
      case INT8_ARRAY -> JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
          .withItems(JsonSchemaType.INTEGER)
          .build();
      case MONEY_ARRAY -> JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
          .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.NUMBER)
              .build())
          .build();
      case OID_ARRAY -> JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
          .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.NUMBER)
              .build())
          .build();
      case NUMERIC_ARRAY -> JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
          .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.NUMBER)
              .build())
          .build();
      case FLOAT4_ARRAY -> JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
          .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.NUMBER)
              .build())
          .build();
      case FLOAT8_ARRAY -> JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
          .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.NUMBER)
              .build())
          .build();
      case TIMESTAMPTZ_ARRAY -> JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
          .withItems(JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE)
          .build();
      case TIMESTAMP_ARRAY -> JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
          .withItems(JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE)
          .build();
      case TIMETZ_ARRAY -> JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
          .withItems(JsonSchemaType.STRING_TIME_WITH_TIMEZONE)
          .build();
      case TIME_ARRAY -> JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
          .withItems(JsonSchemaType.STRING_TIME_WITHOUT_TIMEZONE)
          .build();
      case DATE_ARRAY -> JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
          .withItems(JsonSchemaType.STRING_DATE)
          .build();

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
                                                final Class<T> clazz)
      throws SQLException {
    final T object = getObject(resultSet, index, clazz);
    node.put(columnName, object.getValue());
  }

  @Override
  protected void putBigDecimal(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) {
    final BigDecimal bigDecimal = DataTypeUtils.throwExceptionIfInvalid(() -> resultSet.getBigDecimal(index));
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
    node.put(columnName, DataTypeUtils.throwExceptionIfInvalid(() -> Double.valueOf(moneyValue), Double::isFinite));
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
  public boolean isCursorType(final PostgresType type) {
    return PostgresUtils.ALLOWED_CURSOR_TYPES.contains(type);
  }

  private ColumnInfo getColumnInfo(final int colIndex, final PgResultSetMetaData metadata, final String columnName) throws SQLException {
    final String tableName = metadata.getBaseTableName(colIndex);
    final String schemaName = metadata.getBaseSchemaName(colIndex);
    final String key = schemaName + tableName;
    if (!streamColumnInfo.containsKey(key)) {
      streamColumnInfo.clear();
      streamColumnInfo.put(key, new HashMap<>(metadata.getColumnCount()));
    }

    final Map<String, ColumnInfo> stringColumnInfoMap = streamColumnInfo.get(key);
    if (stringColumnInfoMap.containsKey(columnName)) {
      return stringColumnInfoMap.get(columnName);
    } else {
      final PostgresType columnType = safeGetJdbcType(metadata.getColumnType(colIndex), POSTGRES_TYPE_DICT);
      final ColumnInfo columnInfo = new ColumnInfo(metadata.getColumnTypeName(colIndex).toLowerCase(), columnType);
      stringColumnInfoMap.put(columnName, columnInfo);
      return columnInfo;
    }
  }

  private static class ColumnInfo {

    public String columnTypeName;
    public PostgresType columnType;

    public ColumnInfo(final String columnTypeName, final PostgresType columnType) {
      this.columnTypeName = columnTypeName;
      this.columnType = columnType;
    }

  }

}
