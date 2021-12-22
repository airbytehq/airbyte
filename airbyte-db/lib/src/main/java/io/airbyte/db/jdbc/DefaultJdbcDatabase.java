/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.db.JdbcCompatibleSourceOperations;
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

  public DefaultJdbcDatabase(final DataSource dataSource, final JdbcCompatibleSourceOperations<?> sourceOperations) {
    this(new DataSourceConnectionSupplier(dataSource), sourceOperations);
  }

  public DefaultJdbcDatabase(final CloseableConnectionSupplier connectionSupplier, final JdbcCompatibleSourceOperations<?> sourceOperations) {
    super(sourceOperations);
    this.connectionSupplier = connectionSupplier;
  }

  public DefaultJdbcDatabase(final CloseableConnectionSupplier connectionSupplier) {
    super(JdbcUtils.getDefaultSourceOperations());
    this.connectionSupplier = connectionSupplier;
  }

  @Override
  public void execute(final CheckedConsumer<Connection, SQLException> query) throws SQLException {
    try (final Connection connection = connectionSupplier.getConnection()) {
      query.accept(connection);
    }
  }

  @Override
  public <T> List<T> bufferedResultSetQuery(final CheckedFunction<Connection, ResultSet, SQLException> query,
                                            final CheckedFunction<ResultSet, T, SQLException> recordTransform)
      throws SQLException {
    try (final Connection connection = connectionSupplier.getConnection()) {
      return toStream(query.apply(connection), recordTransform).collect(Collectors.toList());
    }
  }

  @Override
  public <T> Stream<T> resultSetQuery(final CheckedFunction<Connection, ResultSet, SQLException> query,
                                      final CheckedFunction<ResultSet, T, SQLException> recordTransform)
      throws SQLException {
    final Connection connection = connectionSupplier.getConnection();
    return toStream(query.apply(connection), recordTransform)
        .onClose(() -> {
          try {
            connection.close();
          } catch (final SQLException e) {
            throw new RuntimeException(e);
          }
        });
  }

  @Override
  public DatabaseMetaData getMetaData() throws SQLException {
    final Connection conn = connectionSupplier.getConnection();
    final DatabaseMetaData metaData = conn.getMetaData();
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
  public <T> Stream<T> query(final CheckedFunction<Connection, PreparedStatement, SQLException> statementCreator,
                             final CheckedFunction<ResultSet, T, SQLException> recordTransform)
      throws SQLException {
    final Connection connection = connectionSupplier.getConnection();
    return toStream(statementCreator.apply(connection).executeQuery(), recordTransform)
        .onClose(() -> {
          try {
            LOGGER.info("closing connection");
            connection.close();
          } catch (final SQLException e) {
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

    public DataSourceConnectionSupplier(final DataSource dataSource) {
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
