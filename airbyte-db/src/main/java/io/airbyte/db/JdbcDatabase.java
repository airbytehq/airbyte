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

package io.airbyte.db;

import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.functional.CheckedFunction;
import java.io.Closeable;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import javax.sql.DataSource;

/**
 * Database object for interacting with a JDBC connection.
 */
public class JdbcDatabase implements AutoCloseable {

  private final DataSource ds;

  public JdbcDatabase(final DataSource ds) {
    this.ds = ds;
  }

  /**
   * Execute a database query immediately.
   *
   * @param query the query to execute against the database.
   * @throws SQLException SQL related exceptions.
   */
  public void execute(CheckedConsumer<Connection, SQLException> query) throws SQLException {
    try (final Connection connection = ds.getConnection()) {
      query.accept(connection);
    }
  }

  /**
   * Execute a database query immediately and collect it into a list.
   *
   * @param query execute a query using a connection to get a JDBC ResultSet.
   * @param recordTransform transform each record of that result set into the desired type. do NOT
   *        just pass the ResultSet through. it is a stateful object will not be accessible if
   *        returned from recordTransform.
   * @param <T> type that each record will be mapped to.
   * @return List with the mapped records.
   * @throws SQLException SQL related exceptions.
   */
  public <T> List<T> query(CheckedFunction<Connection, ResultSet, SQLException> query, CheckedFunction<ResultSet, T, SQLException> recordTransform)
      throws SQLException {
    try (final Connection connection = ds.getConnection()) {
      return JdbcUtils.mapResultSet(query.apply(connection), recordTransform).collect(Collectors.toList());
    }
  }

  /**
   * Use a connection to create a JDBC PreparedStatement and then execute it lazily.
   *
   * @param statementCreator create a JDBC PreparedStatement from a Connection.
   * @param recordTransform transform each record of that result set into the desired type. do NOT
   *        just pass the ResultSet through. it is a stateful object will not be accessible if
   *        returned from recordTransform.
   * @param <T> type that each record will be mapped to.
   * @return Stream of records.
   */
  public <T> Stream<T> queryLazy(CheckedFunction<Connection, PreparedStatement, SQLException> statementCreator,
                                 CheckedFunction<ResultSet, T, SQLException> recordTransform) {
    return Stream.of(1).flatMap(i -> {
      try {
        // we don't open the connection until we need it.
        final Connection connection = ds.getConnection();
        return JdbcUtils.fetchStream(statementCreator.apply(connection), recordTransform)
            // because this stream is inside the flatMap of another stream, we have a guarantee that the close
            // of this stream will be closed if the outer stream is fully consumed.
            .onClose(() -> {
              try {
                connection.close();
              } catch (SQLException e) {
                throw new RuntimeException(e);
              }
            });
      } catch (SQLException e) {
        throw new RuntimeException(e);
      }
    });
  }

  @Override
  public void close() throws Exception {
    // Just a safety in case we are using a datasource implementation that requires closing.
    // BasicDataSource from apache does since it also provides a pooling mechanism to reuse connections.

    if (ds instanceof AutoCloseable) {
      ((AutoCloseable) ds).close();
    }
    if (ds instanceof Closeable) {
      ((Closeable) ds).close();
    }
  }

}
