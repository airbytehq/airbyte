/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

import static io.airbyte.db.DataTypeUtils.TIMESTAMPTZ_FORMATTER;
import static io.airbyte.db.DataTypeUtils.TIMETZ_FORMATTER;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.DataTypeUtils;
import io.airbyte.db.JdbcCompatibleSourceOperations;
import java.math.BigDecimal;
import java.sql.Connection;
import java.sql.Date;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.text.ParseException;
import java.time.Instant;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.time.OffsetTime;
import java.time.chrono.IsoEra;
import java.util.Collections;
import java.util.List;
import java.util.StringJoiner;
import javax.xml.bind.DatatypeConverter;

/**
 * Source operation skeleton for JDBC compatible databases.
 */
public abstract class AbstractJdbcCompatibleSourceOperations<Datatype> implements JdbcCompatibleSourceOperations<Datatype> {

  /**
   * A Date representing the earliest date in CE. Any date before this is in BCE.
   */
  private static final Date ONE_CE = Date.valueOf("0001-01-01");

  @Override
  public JsonNode rowToJson(final ResultSet queryContext) throws SQLException {
    // the first call communicates with the database. after that the result is cached.
    final int columnCount = queryContext.getMetaData().getColumnCount();
    final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());

    for (int i = 1; i <= columnCount; i++) {
      // attempt to access the column. this allows us to know if it is null before we do type-specific
      // parsing. if it is null, we can move on. while awkward, this seems to be the agreed upon way of
      // checking for null values with jdbc.
      queryContext.getObject(i);
      if (queryContext.wasNull()) {
        continue;
      }

      // convert to java types that will convert into reasonable json.
      setJsonField(queryContext, i, jsonNode);
    }

    return jsonNode;
  }

  protected void putArray(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    final ArrayNode arrayNode = new ObjectMapper().createArrayNode();
    final ResultSet arrayResultSet = resultSet.getArray(index).getResultSet();
    while (arrayResultSet.next()) {
      arrayNode.add(arrayResultSet.getString(2));
    }
    node.set(columnName, arrayNode);
  }

  protected void putBoolean(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    node.put(columnName, resultSet.getBoolean(index));
  }

  /**
   * In some sources Short might have value larger than {@link Short#MAX_VALUE}. E.q. MySQL has
   * unsigned smallint type, which can contain value 65535. If we fail to cast Short value, we will
   * try to cast Integer.
   */
  protected void putShortInt(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    try {
      node.put(columnName, resultSet.getShort(index));
    } catch (final SQLException e) {
      node.put(columnName, DataTypeUtils.returnNullIfInvalid(() -> resultSet.getInt(index)));
    }
  }

  /**
   * In some sources Integer might have value larger than {@link Integer#MAX_VALUE}. E.q. MySQL has
   * unsigned Integer type, which can contain value 3428724653. If we fail to cast Integer value, we
   * will try to cast Long.
   */
  protected void putInteger(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    try {
      node.put(columnName, resultSet.getInt(index));
    } catch (final SQLException e) {
      node.put(columnName, DataTypeUtils.returnNullIfInvalid(() -> resultSet.getLong(index)));
    }
  }

  protected void putBigInt(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    node.put(columnName, DataTypeUtils.returnNullIfInvalid(() -> resultSet.getLong(index)));
  }

  protected void putDouble(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    node.put(columnName, DataTypeUtils.returnNullIfInvalid(() -> resultSet.getDouble(index), Double::isFinite));
  }

  protected void putFloat(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    node.put(columnName, DataTypeUtils.returnNullIfInvalid(() -> resultSet.getFloat(index), Float::isFinite));
  }

  protected void putBigDecimal(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    node.put(columnName, DataTypeUtils.returnNullIfInvalid(() -> resultSet.getBigDecimal(index)));
  }

  protected void putString(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    node.put(columnName, resultSet.getString(index));
  }

  protected void putDate(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    node.put(columnName, DataTypeUtils.toISO8601String(resultSet.getDate(index)));
  }

  protected void putTime(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    node.put(columnName, DataTypeUtils.toISO8601String(resultSet.getTime(index)));
  }

  protected void putTimestamp(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    // https://www.cis.upenn.edu/~bcpierce/courses/629/jdkdocs/guide/jdbc/getstart/mapping.doc.html
    final Instant instant = resultSet.getTimestamp(index).toInstant();
    node.put(columnName, DataTypeUtils.toISO8601StringWithMicroseconds(instant));
  }

  protected void putBinary(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    node.put(columnName, resultSet.getBytes(index));
  }

  protected void putDefault(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    node.put(columnName, resultSet.getString(index));
  }

  protected void setTime(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    setTimestamp(preparedStatement, parameterIndex, value);
  }

  protected void setTimestamp(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    // parse time, and timestamp the same way. this seems to not cause an problems and allows us
    // to treat them all as ISO8601. if this causes any problems down the line, we can adjust.
    // Parsing TIME as a TIMESTAMP might potentially break for ClickHouse cause it doesn't expect TIME
    // value in the following format
    try {
      var valueWithoutMicros = value;
      final StringBuilder nanos = new StringBuilder();
      final var dotIndex = value.indexOf(".");
      if (dotIndex > 0) {
        final var micro = value.substring(value.lastIndexOf('.') + 1, value.length() - 1);
        nanos.append(micro);
        valueWithoutMicros = value.replace("." + micro, "");
      }
      while (nanos.length() != 9) {
        nanos.append("0");
      }

      final var timestamp = Timestamp
          .from(DataTypeUtils.getDateFormat().parse(valueWithoutMicros).toInstant());
      timestamp.setNanos(Integer.parseInt(nanos.toString()));
      preparedStatement.setTimestamp(parameterIndex, timestamp);
    } catch (final ParseException e) {
      throw new RuntimeException(e);
    }
  }

  protected void setDate(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    try {
      final Timestamp from = Timestamp.from(DataTypeUtils.getDateFormat().parse(value).toInstant());
      preparedStatement.setDate(parameterIndex, new Date(from.getTime()));
    } catch (final ParseException e) {
      throw new RuntimeException(e);
    }
  }

  protected void setBit(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    // todo (cgardens) - currently we do not support bit because it requires special handling in the
    // prepared statement.
    // see
    // https://www.postgresql-archive.org/Problems-with-BIT-datatype-and-preparedStatment-td5733533.html.
    throw new RuntimeException("BIT value is not supported as incremental parameter!");
  }

  protected void setBoolean(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    preparedStatement.setBoolean(parameterIndex, Boolean.parseBoolean(value));
  }

  protected void setShortInt(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    preparedStatement.setShort(parameterIndex, Short.parseShort(value));
  }

  protected void setInteger(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    preparedStatement.setInt(parameterIndex, Integer.parseInt(value));
  }

  protected void setBigInteger(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    preparedStatement.setLong(parameterIndex, Long.parseLong(value));
  }

  protected void setDouble(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    preparedStatement.setDouble(parameterIndex, Double.parseDouble(value));
  }

  protected void setReal(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    preparedStatement.setFloat(parameterIndex, Float.parseFloat(value));
  }

  protected void setDecimal(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    preparedStatement.setBigDecimal(parameterIndex, new BigDecimal(value));
  }

  protected void setString(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    preparedStatement.setString(parameterIndex, value);
  }

  protected void setBinary(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    preparedStatement.setBytes(parameterIndex, DatatypeConverter.parseHexBinary(value));
  }

  @Override
  public String enquoteIdentifierList(final Connection connection, final List<String> identifiers) throws SQLException {
    final StringJoiner joiner = new StringJoiner(",");
    for (final String col : identifiers) {
      final String s = enquoteIdentifier(connection, col);
      joiner.add(s);
    }
    return joiner.toString();
  }

  @Override
  public String enquoteIdentifier(final Connection connection, final String identifier) throws SQLException {
    final String identifierQuoteString = connection.getMetaData().getIdentifierQuoteString();

    return identifierQuoteString + identifier + identifierQuoteString;
  }

  @Override
  public String getFullyQualifiedTableName(final String schemaName, final String tableName) {
    return JdbcUtils.getFullyQualifiedTableName(schemaName, tableName);
  }

  @Override
  public String getFullyQualifiedTableNameWithQuoting(final Connection connection, final String schemaName, final String tableName)
      throws SQLException {
    final String quotedTableName = enquoteIdentifier(connection, tableName);
    return schemaName != null ? enquoteIdentifier(connection, schemaName) + "." + quotedTableName : quotedTableName;
  }

  protected <ObjectType> ObjectType getObject(final ResultSet resultSet, final int index, final Class<ObjectType> clazz) throws SQLException {
    return resultSet.getObject(index, clazz);
  }

  protected void putTimeWithTimezone(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    final OffsetTime timetz = getObject(resultSet, index, OffsetTime.class);
    node.put(columnName, timetz.format(TIMETZ_FORMATTER));
  }

  protected void putTimestampWithTimezone(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index)
      throws SQLException {
    final OffsetDateTime timestamptz = getObject(resultSet, index, OffsetDateTime.class);
    final LocalDate localDate = timestamptz.toLocalDate();
    node.put(columnName, resolveEra(localDate, timestamptz.format(TIMESTAMPTZ_FORMATTER)));
  }

  /**
   * Modifies a string representation of a date/timestamp and normalizes its era indicator.
   * Specifically, if this is a BCE value:
   * <ul>
   * <li>The leading negative sign will be removed if present</li>
   * <li>The "BC" suffix will be appended, if not already present</li>
   * </ul>
   *
   * You most likely would prefer to call one of the overloaded methods, which accept temporal types.
   */
  public static String resolveEra(final boolean isBce, final String value) {
    String mangledValue = value;
    if (isBce) {
      if (mangledValue.startsWith("-")) {
        mangledValue = mangledValue.substring(1);
      }
      if (!mangledValue.endsWith(" BC")) {
        mangledValue += " BC";
      }
    }
    return mangledValue;
  }

  public static boolean isBce(final LocalDate date) {
    return date.getEra().equals(IsoEra.BCE);
  }

  public static String resolveEra(final LocalDate date, final String value) {
    return resolveEra(isBce(date), value);
  }

  /**
   * java.sql.Date objects don't properly represent their era (for example, using toLocalDate() always
   * returns an object in CE). So to determine the era, we just check whether the date is before 1 AD.
   *
   * This is technically kind of sketchy due to ancient timestamps being weird (leap years, etc.), but
   * my understanding is that {@link #ONE_CE} has the same weirdness, so it cancels out.
   */
  public static String resolveEra(final Date date, final String value) {
    return resolveEra(date.before(ONE_CE), value);
  }

  /**
   * See {@link #resolveEra(Date, String)} for explanation.
   */
  public static String resolveEra(final Timestamp timestamp, final String value) {
    return resolveEra(timestamp.before(ONE_CE), value);
  }

}
