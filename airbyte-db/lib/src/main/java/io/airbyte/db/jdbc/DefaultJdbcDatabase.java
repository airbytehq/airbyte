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

import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.functional.CheckedFunction;
import java.io.Closeable;
import java.sql.Connection;
import java.sql.DatabaseMetaData;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Database object for interacting with a JDBC connection. Can be used for any JDBC compliant db.
 */
public class DefaultJdbcDatabase extends JdbcDatabase {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultJdbcDatabase.class);

  private final CloseableConnectionSupplier connectionSupplier;

  public DefaultJdbcDatabase(final DataSource dataSource) {
    this(new DataSourceConnectionSupplier(dataSource), JdbcUtils.getDefaultSourceOperations());
  }

  public DefaultJdbcDatabase(final DataSource dataSource, JdbcSourceOperations sourceOperations) {
    this(new DataSourceConnectionSupplier(dataSource), sourceOperations);
  }

  public DefaultJdbcDatabase(CloseableConnectionSupplier connectionSupplier, JdbcSourceOperations sourceOperations) {
    super(sourceOperations);
    this.connectionSupplier = connectionSupplier;
  }

  public DefaultJdbcDatabase(final CloseableConnectionSupplier connectionSupplier) {
    super(JdbcUtils.getDefaultSourceOperations());
    this.connectionSupplier = connectionSupplier;
  }

  @Override
  public void execute(CheckedConsumer<Connection, SQLException> query) throws SQLException {
    try (final Connection connection = connectionSupplier.getConnection()) {
      query.accept(connection);
    }
  }

  @Override
  public <T> List<T> bufferedResultSetQuery(CheckedFunction<Connection, ResultSet, SQLException> query,
                                            CheckedFunction<ResultSet, T, SQLException> recordTransform)
      throws SQLException {
    try (final Connection connection = connectionSupplier.getConnection()) {
      return sourceOperations.toStream(query.apply(connection), recordTransform).collect(Collectors.toList());
    }
  }

  @Override
  public <T> Stream<T> resultSetQuery(CheckedFunction<Connection, ResultSet, SQLException> query,
                                      CheckedFunction<ResultSet, T, SQLException> recordTransform)
      throws SQLException {
    final Connection connection = connectionSupplier.getConnection();
    return sourceOperations.toStream(query.apply(connection), recordTransform)
        .onClose(() -> {
          try {
            connection.close();
          } catch (SQLException e) {
            throw new RuntimeException(e);
          }
        });
  }

  @Override
  public DatabaseMetaData getMetaData() throws SQLException {
    Connection conn = connectionSupplier.getConnection();
    DatabaseMetaData metaData = conn.getMetaData();
    conn.close();
    return metaData;
  }

  /**
   * You CANNOT assume that data will be returned from this method before the entire {@link ResultSet}
   * is buffered in memory. Review the implementation of the database's JDBC driver or use the
   * StreamingJdbcDriver if you need this guarantee. The caller should close the returned stream to
   * release the database connection.
   *
   * @param statementCreator create a {@link PreparedStatement} from a {@link Connection}.
   * @param recordTransform transform each record of that result set into the desired type. do NOT
   *        just pass the {@link ResultSet} through. it is a stateful object will not be accessible if
   *        returned from recordTransform.
   * @param <T> type that each record will be mapped to.
   * @return Result of the query mapped to a stream.
   * @throws SQLException SQL related exceptions.
   */
  @Override
  public <T> Stream<T> query(CheckedFunction<Connection, PreparedStatement, SQLException> statementCreator,
                             CheckedFunction<ResultSet, T, SQLException> recordTransform)
      throws SQLException {
    final Connection connection = connectionSupplier.getConnection();
    return sourceOperations.toStream(statementCreator.apply(connection).executeQuery(), recordTransform)
        .onClose(() -> {
          try {
            LOGGER.info("closing connection");
            connection.close();
          } catch (SQLException e) {
            throw new RuntimeException(e);
          }
        });
  }

  @Override
  public void close() throws Exception {
    connectionSupplier.close();
  }

  public interface CloseableConnectionSupplier extends AutoCloseable {

    Connection getConnection() throws SQLException;

  }

  public static final class DataSourceConnectionSupplier implements CloseableConnectionSupplier {

    private final DataSource dataSource;

    public DataSourceConnectionSupplier(DataSource dataSource) {
      this.dataSource = dataSource;
    }

    @Override
    public Connection getConnection() throws SQLException {
      return dataSource.getConnection();
    }

    @Override
    public void close() throws Exception {
      // Just a safety in case we are using a datasource implementation that requires closing.
      // BasicDataSource from apache does since it also provides a pooling mechanism to reuse connections.

      if (dataSource instanceof AutoCloseable) {
        ((AutoCloseable) dataSource).close();
      }
      if (dataSource instanceof Closeable) {
        ((Closeable) dataSource).close();
      }
    }

  }

}
