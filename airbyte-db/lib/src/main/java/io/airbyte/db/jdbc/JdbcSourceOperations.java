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
import io.airbyte.db.DataTypeUtils;
import io.airbyte.db.SourceOperations;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import java.math.BigDecimal;
import java.sql.Date;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.text.ParseException;
import java.util.Collections;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.function.Consumer;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;
import javax.xml.bind.DatatypeConverter;

public class JdbcSourceOperations implements SourceOperations<ResultSet, JDBCType> {

  /**
   * Map records returned in a result set.
   *
   * @param resultSet the result set
   * @param mapper function to make each record of the result set
   * @param <T> type that each record will be mapped to
   * @return stream of records that the result set is mapped to.
   */
  public <T> Stream<T> toStream(ResultSet resultSet, CheckedFunction<ResultSet, T, SQLException> mapper) {
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

  @Override
  public JsonNode rowToJson(ResultSet queryContext) throws SQLException {
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

  protected JDBCType safeGetJdbcType(int columnTypeInt) {
    try {
      return JDBCType.valueOf(columnTypeInt);
    } catch (Exception e) {
      return JDBCType.VARCHAR;
    }
  }

  protected void setJsonField(ResultSet r, int i, ObjectNode o) throws SQLException {
    final int columnTypeInt = r.getMetaData().getColumnType(i);
    final String columnName = r.getMetaData().getColumnName(i);
    final JDBCType columnType = safeGetJdbcType(columnTypeInt);

    // https://www.cis.upenn.edu/~bcpierce/courses/629/jdkdocs/guide/jdbc/getstart/mapping.doc.html
    switch (columnType) {
      case BIT, BOOLEAN -> putBoolean(o, columnName, r, i);
      case TINYINT, SMALLINT -> putShortInt(o, columnName, r, i);
      case INTEGER -> putInteger(o, columnName, r, i);
      case BIGINT -> putBigInt(o, columnName, r, i);
      case FLOAT, DOUBLE -> putDouble(o, columnName, r, i);
      case REAL -> putReal(o, columnName, r, i);
      case NUMERIC, DECIMAL -> putNumber(o, columnName, r, i);
      case CHAR, VARCHAR, LONGVARCHAR -> putString(o, columnName, r, i);
      case DATE -> putDate(o, columnName, r, i);
      case TIME -> putTime(o, columnName, r, i);
      case TIMESTAMP -> putTimestamp(o, columnName, r, i);
      case BLOB, BINARY, VARBINARY, LONGVARBINARY -> putBinary(o, columnName, r, i);
      default -> putDefault(o, columnName, r, i);
    }
  }

  protected void putBoolean(ObjectNode node, String columnName, ResultSet resultSet, int index) throws SQLException {
    node.put(columnName, resultSet.getBoolean(index));
  }

  protected void putShortInt(ObjectNode node, String columnName, ResultSet resultSet, int index) throws SQLException {
    node.put(columnName, resultSet.getShort(index));
  }

  /**
   * In some sources Integer might have value larger than {@link Integer#MAX_VALUE}. E.q. MySQL has
   * unsigned Integer type, which can contain value 3428724653. If we fail to cast Integer value, we
   * will try to cast Long.
   */
  protected void putInteger(ObjectNode node, String columnName, ResultSet resultSet, int index) throws SQLException {
    try {
      node.put(columnName, resultSet.getInt(index));
    } catch (SQLException e) {
      node.put(columnName, DataTypeUtils.returnNullIfInvalid(() -> resultSet.getLong(index)));
    }
  }

  protected void putBigInt(ObjectNode node, String columnName, ResultSet resultSet, int index) throws SQLException {
    node.put(columnName, DataTypeUtils.returnNullIfInvalid(() -> resultSet.getLong(index)));
  }

  protected void putDouble(ObjectNode node, String columnName, ResultSet resultSet, int index) throws SQLException {
    node.put(columnName, DataTypeUtils.returnNullIfInvalid(() -> resultSet.getDouble(index), Double::isFinite));
  }

  protected void putReal(ObjectNode node, String columnName, ResultSet resultSet, int index) throws SQLException {
    node.put(columnName, DataTypeUtils.returnNullIfInvalid(() -> resultSet.getFloat(index), Float::isFinite));
  }

  protected void putNumber(ObjectNode node, String columnName, ResultSet resultSet, int index) throws SQLException {
    node.put(columnName, DataTypeUtils.returnNullIfInvalid(() -> resultSet.getBigDecimal(index)));
  }

  protected void putString(ObjectNode node, String columnName, ResultSet resultSet, int index) throws SQLException {
    node.put(columnName, resultSet.getString(index));
  }

  protected void putDate(ObjectNode node, String columnName, ResultSet resultSet, int index) throws SQLException {
    node.put(columnName, DataTypeUtils.toISO8601String(resultSet.getDate(index)));
  }

  protected void putTime(ObjectNode node, String columnName, ResultSet resultSet, int index) throws SQLException {
    node.put(columnName, DataTypeUtils.toISO8601String(resultSet.getTime(index)));
  }

  protected void putTimestamp(ObjectNode node, String columnName, ResultSet resultSet, int index) throws SQLException {
    // https://www.cis.upenn.edu/~bcpierce/courses/629/jdkdocs/guide/jdbc/getstart/mapping.doc.html
    final Timestamp t = resultSet.getTimestamp(index);
    java.util.Date d = new java.util.Date(t.getTime() + (t.getNanos() / 1000000));
    node.put(columnName, DataTypeUtils.toISO8601String(d));
  }

  protected void putBinary(ObjectNode node, String columnName, ResultSet resultSet, int index) throws SQLException {
    node.put(columnName, resultSet.getBytes(index));
  }

  protected void putDefault(ObjectNode node, String columnName, ResultSet resultSet, int index) throws SQLException {
    node.put(columnName, resultSet.getString(index));
  }

  // todo (cgardens) - move generic date helpers to commons.

  public void setStatementField(PreparedStatement preparedStatement,
                                int parameterIndex,
                                JDBCType cursorFieldType,
                                String value)
      throws SQLException {
    switch (cursorFieldType) {
      // parse time, and timestamp the same way. this seems to not cause an problems and allows us
      // to treat them all as ISO8601. if this causes any problems down the line, we can adjust.
      // Parsing TIME as a TIMESTAMP might potentially break for ClickHouse cause it doesn't expect TIME
      // value in the following format
      case TIME, TIMESTAMP -> {
        try {
          preparedStatement.setTimestamp(parameterIndex, Timestamp.from(
              DataTypeUtils.DATE_FORMAT.parse(value).toInstant()));
        } catch (ParseException e) {
          throw new RuntimeException(e);
        }
      }

      case DATE -> {
        try {
          Timestamp from = Timestamp.from(DataTypeUtils.DATE_FORMAT.parse(value).toInstant());
          preparedStatement.setDate(parameterIndex, new Date(from.getTime()));
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
      case BINARY, BLOB -> preparedStatement.setBytes(parameterIndex, DatatypeConverter.parseHexBinary(value));
      // since cursor are expected to be comparable, handle cursor typing strictly and error on
      // unrecognized types
      default -> throw new IllegalArgumentException(String.format("%s is not supported.", cursorFieldType));
    }
  }

  @Override
  public JsonSchemaPrimitive getType(JDBCType bigQueryType) {
    return switch (bigQueryType) {
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
      case BLOB, BINARY, VARBINARY, LONGVARBINARY -> JsonSchemaPrimitive.STRING;
      // since column types aren't necessarily meaningful to Airbyte, liberally convert all unrecgonised
      // types to String
      default -> JsonSchemaPrimitive.STRING;
    };
  }

}
