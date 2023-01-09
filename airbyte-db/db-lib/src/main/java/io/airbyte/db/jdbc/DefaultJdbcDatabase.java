/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

import com.google.errorprone.annotations.MustBeClosed;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.db.JdbcCompatibleSourceOperations;
import java.sql.Connection;
import java.sql.DatabaseMetaData;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.Objects;
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

  protected final DataSource dataSource;

  public DefaultJdbcDatabase(final DataSource dataSource) {
    this(dataSource, JdbcUtils.getDefaultSourceOperations());
  }

  public DefaultJdbcDatabase(final DataSource dataSource, final JdbcCompatibleSourceOperations<?> sourceOperations) {
    super(sourceOperations);
    this.dataSource = dataSource;
  }

  @Override
  public void execute(final CheckedConsumer<Connection, SQLException> query) throws SQLException {
    try (final Connection connection = dataSource.getConnection()) {
      query.accept(connection);
    }
  }

  @Override
  public <T> List<T> bufferedResultSetQuery(final CheckedFunction<Connection, ResultSet, SQLException> query,
                                            final CheckedFunction<ResultSet, T, SQLException> recordTransform)
      throws SQLException {
    try (final Connection connection = dataSource.getConnection();
        final Stream<T> results = toUnsafeStream(query.apply(connection), recordTransform)) {
      return results.collect(Collectors.toList());
    }
  }

  @Override
  @MustBeClosed
  public <T> Stream<T> unsafeResultSetQuery(final CheckedFunction<Connection, ResultSet, SQLException> query,
                                            final CheckedFunction<ResultSet, T, SQLException> recordTransform)
      throws SQLException {
    final Connection connection = dataSource.getConnection();
    return toUnsafeStream(query.apply(connection), recordTransform)
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
    try (final Connection connection = dataSource.getConnection()) {
      final DatabaseMetaData metaData = connection.getMetaData();
      return metaData;
    } catch (final SQLException e) {
      // Some databases like Redshift will have null cause
      if (Objects.isNull(e.getCause()) || !(e.getCause() instanceof SQLException)) {
        throw new ConnectionErrorException(e.getSQLState(), e.getErrorCode(), e.getMessage(), e);
      } else {
        final SQLException cause = (SQLException) e.getCause();
        throw new ConnectionErrorException(e.getSQLState(), cause.getErrorCode(), cause.getMessage(), e);
      }
    }
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
  @MustBeClosed
  public <T> Stream<T> unsafeQuery(final CheckedFunction<Connection, PreparedStatement, SQLException> statementCreator,
                                   final CheckedFunction<ResultSet, T, SQLException> recordTransform)
      throws SQLException {
    final Connection connection = dataSource.getConnection();
    return toUnsafeStream(statementCreator.apply(connection).executeQuery(), recordTransform)
        .onClose(() -> {
          try {
            LOGGER.info("closing connection");
            connection.close();
          } catch (final SQLException e) {
            throw new RuntimeException(e);
          }
        });
  }

}
