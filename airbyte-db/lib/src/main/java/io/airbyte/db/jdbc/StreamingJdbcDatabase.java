/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.db.JdbcCompatibleSourceOperations;
import java.sql.Connection;
import java.sql.DatabaseMetaData;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.stream.Stream;
import javax.sql.DataSource;

/**
 * This database allows a developer to specify a {@link JdbcStreamingQueryConfiguration}. This
 * allows the developer to specify the correct configuration in order for a
 * {@link PreparedStatement} to execute as in a streaming / chunked manner.
 */
public class StreamingJdbcDatabase extends JdbcDatabase {

  private final DataSource dataSource;
  private final JdbcDatabase database;
  private final JdbcStreamingQueryConfiguration jdbcStreamingQueryConfiguration;

  public StreamingJdbcDatabase(final DataSource dataSource,
                               final JdbcDatabase database,
                               final JdbcStreamingQueryConfiguration jdbcStreamingQueryConfiguration) {
    this(dataSource, database, jdbcStreamingQueryConfiguration, database.sourceOperations);
  }

  public StreamingJdbcDatabase(final DataSource dataSource,
                               final JdbcDatabase database,
                               final JdbcStreamingQueryConfiguration jdbcStreamingQueryConfiguration,
                               final JdbcCompatibleSourceOperations<?> sourceOperations) {
    super(sourceOperations);
    this.dataSource = dataSource;
    this.database = database;
    this.jdbcStreamingQueryConfiguration = jdbcStreamingQueryConfiguration;
  }

  @Override
  public DatabaseMetaData getMetaData() throws SQLException {
    return database.getMetaData();
  }

  @Override
  public void execute(final CheckedConsumer<Connection, SQLException> query) throws SQLException {
    database.execute(query);
  }

  @Override
  public <T> List<T> bufferedResultSetQuery(final CheckedFunction<Connection, ResultSet, SQLException> query,
                                            final CheckedFunction<ResultSet, T, SQLException> recordTransform)
      throws SQLException {
    return database.bufferedResultSetQuery(query, recordTransform);
  }

  @Override
  public <T> Stream<T> resultSetQuery(final CheckedFunction<Connection, ResultSet, SQLException> query,
                                      final CheckedFunction<ResultSet, T, SQLException> recordTransform)
      throws SQLException {
    return database.resultSetQuery(query, recordTransform);
  }

  /**
   * Assuming that the {@link JdbcStreamingQueryConfiguration} is configured correctly for the JDBC
   * driver being used, this method will return data in streaming / chunked fashion. Review the
   * provided {@link JdbcStreamingQueryConfiguration} to understand the size of these chunks. If the
   * entire stream is consumed the database connection will be closed automatically and the caller
   * need not call close on the returned stream. This query (and the first chunk) are fetched
   * immediately. Subsequent chunks will not be pulled until the first chunk is consumed.
   *
   * @param statementCreator create a {@link PreparedStatement} from a {@link Connection}.
   * @param recordTransform transform each record of that result set into the desired type. do NOT
   *        just pass the {@link ResultSet} through. it is a stateful object will not be accessible if
   *        returned from recordTransform.
   * @param <T> type that each record will be mapped to.
   * @return Result of the query mapped to a stream. This stream must be closed!
   * @throws SQLException SQL related exceptions.
   */
  @Override
  public <T> Stream<T> query(final CheckedFunction<Connection, PreparedStatement, SQLException> statementCreator,
                             final CheckedFunction<ResultSet, T, SQLException> recordTransform)
      throws SQLException {
    try {
      final Connection connection = dataSource.getConnection();
      final PreparedStatement ps = statementCreator.apply(connection);
      // allow configuration of connection and prepared statement to make streaming possible.
      jdbcStreamingQueryConfiguration.accept(connection, ps);
      return toStream(ps.executeQuery(), recordTransform)
          .onClose(() -> {
            try {
              connection.setAutoCommit(true);
              connection.close();
            } catch (final SQLException e) {
              throw new RuntimeException(e);
            }
          });
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public void close() throws Exception {
    database.close();
  }

}
