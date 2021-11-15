/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.functional.CheckedFunction;
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
import java.util.Collections;
import java.util.List;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.StringJoiner;
import java.util.function.Consumer;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;
import javax.xml.bind.DatatypeConverter;

/**
 * Source operation skeleton for JDBC compatible databases.
 */
public abstract class AbstractJdbcCompatibleSourceOperations<Datatype> implements JdbcCompatibleSourceOperations<Datatype> {

  /**
   * @param colIndex 1-based column index.
   */
  protected abstract void setJsonField(final ResultSet resultSet, final int colIndex, final ObjectNode json) throws SQLException;

  @Override
  public <T> Stream<T> toStream(final ResultSet resultSet, final CheckedFunction<ResultSet, T, SQLException> mapper) {
    return StreamSupport.stream(new Spliterators.AbstractSpliterator<>(Long.MAX_VALUE, Spliterator.ORDERED) {

      @Override
      public boolean tryAdvance(final Consumer<? super T> action) {
        try {
          if (!resultSet.next()) {
            return false;
          }
          action.accept(mapper.apply(resultSet));
          return true;
        } catch (final SQLException e) {
          throw new RuntimeException(e);
        }
      }

    }, false);
  }

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
    final Timestamp t = resultSet.getTimestamp(index);
    final java.util.Date d = new java.util.Date(t.getTime() + (t.getNanos() / 1000000));
    node.put(columnName, DataTypeUtils.toISO8601String(d));
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
      preparedStatement.setTimestamp(parameterIndex, Timestamp
          .from(DataTypeUtils.DATE_FORMAT.parse(value).toInstant()));
    } catch (final ParseException e) {
      throw new RuntimeException(e);
    }
  }

  protected void setDate(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    try {
      final Timestamp from = Timestamp.from(DataTypeUtils.DATE_FORMAT.parse(value).toInstant());
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

}
