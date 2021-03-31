/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.db.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import java.math.BigDecimal;
import java.sql.Connection;
import java.sql.Date;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.time.Instant;
import java.util.Collections;
import java.util.List;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.StringJoiner;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;
import javax.xml.bind.DatatypeConverter;

public class JdbcUtils {

  private static final DateFormat DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'"); // Quoted "Z" to indicate UTC, no timezone offset

  /**
   * Map records returned in a result set.
   *
   * @param resultSet the result set
   * @param mapper function to make each record of the result set
   * @param <T> type that each record will be mapped to
   * @return stream of records that the result set is mapped to.
   */
  public static <T> Stream<T> toStream(ResultSet resultSet, CheckedFunction<ResultSet, T, SQLException> mapper) {
    return StreamSupport.stream(new Spliterators.AbstractSpliterator<>(Long.MAX_VALUE, Spliterator.ORDERED) {

      @Override
      public boolean tryAdvance(Consumer<? super T> action) {
        try {
          if (!resultSet.next()) {
            return false;
          }
          action.accept(mapper.apply(resultSet));
          return true;
        } catch (SQLException e) {
          throw new RuntimeException(e);
        }
      }

    }, false);
  }

  /**
   * Collect each record of a ResultSet into a list of JsonNode.
   *
   * @param resultSet the result set
   * @return Stream of JsonNode.
   * @throws SQLException exceptions throws when parsing the ResultSet.
   */
  public static Stream<JsonNode> toJsonStream(ResultSet resultSet) throws SQLException {
    return toStream(resultSet, JdbcUtils::rowToJson);
  }

  public static JsonNode rowToJson(ResultSet r) throws SQLException {
    // the first call communicates with the database. after that the result is cached.
    final int columnCount = r.getMetaData().getColumnCount();
    final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());

    for (int i = 1; i <= columnCount; i++) {
      // attempt to access the column. this allows us to know if it is null before we do type-specific
      // parsing. if it is null, we can move on. while awkward, this seems to be the agreed upon way of
      // checking for null values with jdbc.
      r.getObject(i);
      if (r.wasNull()) {
        continue;
      }

      // convert to java types that will convert into reasonable json.
      setJsonField(r, i, jsonNode);
    }

    return jsonNode;
  }

  private static JDBCType safeGetJdbcType(int columnTypeInt) {
    try {
      return JDBCType.valueOf(columnTypeInt);
    } catch (Exception e) {
      return JDBCType.VARCHAR;
    }
  }

  private static void setJsonField(ResultSet r, int i, ObjectNode o) throws SQLException {
    final int columnTypeInt = r.getMetaData().getColumnType(i);
    final String columnName = r.getMetaData().getColumnName(i);
    final JDBCType columnType = safeGetJdbcType(columnTypeInt);

    // https://www.cis.upenn.edu/~bcpierce/courses/629/jdkdocs/guide/jdbc/getstart/mapping.doc.html
    switch (columnType) {
      case BIT, BOOLEAN -> o.put(columnName, r.getBoolean(i));
      case TINYINT, SMALLINT -> o.put(columnName, r.getShort(i));
      case INTEGER -> o.put(columnName, r.getInt(i));
      case BIGINT -> o.put(columnName, nullIfInvalid(() -> r.getLong(i)));
      case FLOAT, DOUBLE -> o.put(columnName, nullIfInvalid(() -> r.getDouble(i), Double::isFinite));
      case REAL -> o.put(columnName, nullIfInvalid(() -> r.getFloat(i), Float::isFinite));
      case NUMERIC, DECIMAL -> o.put(columnName, nullIfInvalid(() -> r.getBigDecimal(i)));
      case CHAR, VARCHAR, LONGVARCHAR -> o.put(columnName, r.getString(i));
      case DATE -> o.put(columnName, toISO8601String(r.getDate(i)));
      case TIME -> o.put(columnName, toISO8601String(r.getTime(i)));
      case TIMESTAMP -> {
        // https://www.cis.upenn.edu/~bcpierce/courses/629/jdkdocs/guide/jdbc/getstart/mapping.doc.html
        final Timestamp t = r.getTimestamp(i);
        java.util.Date d = new java.util.Date(t.getTime() + (t.getNanos() / 1000000));
        o.put(columnName, toISO8601String(d));
      }
      case BINARY, VARBINARY, LONGVARBINARY -> o.put(columnName, r.getBytes(i));
      default -> o.put(columnName, r.getString(i));
    }
  }

  // todo (cgardens) - move generic date helpers to commons.

  public static String toISO8601String(long epochMillis) {
    return DATE_FORMAT.format(Date.from(Instant.ofEpochMilli(epochMillis)));
  }

  public static String toISO8601String(java.util.Date date) {
    return DATE_FORMAT.format(date);
  }

  public static void setStatementField(PreparedStatement preparedStatement,
                                       int parameterIndex,
                                       JDBCType cursorFieldType,
                                       String value)
      throws SQLException {
    switch (cursorFieldType) {
      // parse date, time, and timestamp the same way. this seems to not cause an problems and allows us
      // to treat them all as ISO8601. if this causes any problems down the line, we can adjust.
      case DATE, TIME, TIMESTAMP -> {
        try {
          preparedStatement.setTimestamp(parameterIndex, Timestamp.from(DATE_FORMAT.parse(value).toInstant()));
        } catch (ParseException e) {
          throw new RuntimeException(e);
        }
      }
      // todo (cgardens) - currently we do not support bit because it requires special handling in the
      // prepared statement.
      // see
      // https://www.postgresql-archive.org/Problems-with-BIT-datatype-and-preparedStatment-td5733533.html.
      // case BIT -> preparedStatement.setString(parameterIndex, value);
      case BOOLEAN -> preparedStatement.setBoolean(parameterIndex, Boolean.parseBoolean(value));
      case TINYINT, SMALLINT -> preparedStatement.setShort(parameterIndex, Short.parseShort(value));
      case INTEGER -> preparedStatement.setInt(parameterIndex, Integer.parseInt(value));
      case BIGINT -> preparedStatement.setLong(parameterIndex, Long.parseLong(value));
      case FLOAT, DOUBLE -> preparedStatement.setDouble(parameterIndex, Double.parseDouble(value));
      case REAL -> preparedStatement.setFloat(parameterIndex, Float.parseFloat(value));
      case NUMERIC, DECIMAL -> preparedStatement.setBigDecimal(parameterIndex, new BigDecimal(value));
      case CHAR, NCHAR, NVARCHAR, VARCHAR, LONGVARCHAR -> preparedStatement.setString(parameterIndex, value);
      case BINARY -> preparedStatement.setBytes(parameterIndex, DatatypeConverter.parseHexBinary(value));
      // since cursor are expected to be comparable, handle cursor typing strictly and error on
      // unrecognized types
      default -> throw new IllegalArgumentException(String.format("%s is not supported.", cursorFieldType));
    }
  }

  // the switch statement intentionally has duplicates so that its structure matches the type switch
  // statement above.

  @SuppressWarnings("DuplicateBranchesInSwitch")
  public static JsonSchemaPrimitive getType(JDBCType jdbcType) {
    return switch (jdbcType) {
      case BIT, BOOLEAN -> JsonSchemaPrimitive.BOOLEAN;
      case TINYINT, SMALLINT -> JsonSchemaPrimitive.NUMBER;
      case INTEGER -> JsonSchemaPrimitive.NUMBER;
      case BIGINT -> JsonSchemaPrimitive.NUMBER;
      case FLOAT, DOUBLE -> JsonSchemaPrimitive.NUMBER;
      case REAL -> JsonSchemaPrimitive.NUMBER;
      case NUMERIC, DECIMAL -> JsonSchemaPrimitive.NUMBER;
      case CHAR, NCHAR, NVARCHAR, VARCHAR, LONGVARCHAR -> JsonSchemaPrimitive.STRING;
      case DATE -> JsonSchemaPrimitive.STRING;
      case TIME -> JsonSchemaPrimitive.STRING;
      case TIMESTAMP -> JsonSchemaPrimitive.STRING;
      case BINARY, VARBINARY, LONGVARBINARY -> JsonSchemaPrimitive.STRING;
      // since column types aren't necessarily meaningful to Airbyte, liberally convert all unrecgonised
      // types to String
      default -> JsonSchemaPrimitive.STRING;
    };
  }

  private static <T> T nullIfInvalid(SQLSupplier<T> valueProducer) {
    return nullIfInvalid(valueProducer, ignored -> true);
  }

  private static <T> T nullIfInvalid(SQLSupplier<T> valueProducer, Function<T, Boolean> isValidFn) {
    // Some edge case values (e.g: Infinity, NaN) have no java or JSON equivalent, and will throw an
    // exception when parsed. We want to parse those
    // values as null.
    // This method reduces error handling boilerplate.
    try {
      T value = valueProducer.apply();
      return isValidFn.apply(value) ? value : null;
    } catch (SQLException e) {
      return null;
    }
  }

  /**
   * Create a fully qualified table name (including schema) with db-specific quoted syntax. e.g.
   * "public"."my_table"
   *
   * @param connection connection to jdbc database (gives access to proper quotes)
   * @param schemaName name of schema, if exists (CAN BE NULL)
   * @param tableName name of the table
   * @return fully qualified table name, using db-specific quoted syntax
   * @throws SQLException throws if fails to pull correct quote character.
   */
  public static String getFullyQualifiedTableNameWithQuoting(Connection connection, String schemaName, String tableName) throws SQLException {
    final String quotedTableName = enquoteIdentifier(connection, tableName);
    return schemaName != null ? enquoteIdentifier(connection, schemaName) + "." + quotedTableName : quotedTableName;
  }

  /**
   * Create a fully qualified table name (including schema). e.g. public.my_table
   *
   * @param schemaName name of schema, if exists (CAN BE NULL)
   * @param tableName name of the table
   * @return fully qualified table name
   */
  public static String getFullyQualifiedTableName(String schemaName, String tableName) {
    return schemaName != null ? schemaName + "." + tableName : tableName;
  }

  @FunctionalInterface
  private interface SQLSupplier<O> {

    O apply() throws SQLException;

  }

  /**
   * Given a database connection and identifier, adds db-specific quoting.
   *
   * @param connection database connection
   * @param identifier identifier to quote
   * @return quoted identifier
   * @throws SQLException throws if there are any issues fulling the quoting metadata from the db.
   */
  public static String enquoteIdentifier(Connection connection, String identifier) throws SQLException {
    final String identifierQuoteString = connection.getMetaData().getIdentifierQuoteString();

    return identifierQuoteString + identifier + identifierQuoteString;
  }

  /**
   * Given a database connection and identifiers, adds db-specific quoting to each identifier.
   *
   * @param connection database connection
   * @param identifiers identifiers to quote
   * @return quoted identifiers
   * @throws SQLException throws if there are any issues fulling the quoting metadata from the db.
   */
  public static String enquoteIdentifierList(Connection connection, List<String> identifiers) throws SQLException {
    final StringJoiner joiner = new StringJoiner(",");
    for (String col : identifiers) {
      String s = JdbcUtils.enquoteIdentifier(connection, col);
      joiner.add(s);
    }
    return joiner.toString();
  }

}
