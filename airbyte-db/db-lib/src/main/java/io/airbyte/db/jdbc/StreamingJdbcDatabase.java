/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

import com.google.errorprone.annotations.MustBeClosed;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.db.JdbcCompatibleSourceOperations;
import io.airbyte.db.jdbc.streaming.JdbcStreamingQueryConfig;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.function.Consumer;
import java.util.function.Supplier;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This database allows a developer to specify a {@link JdbcStreamingQueryConfig}. This allows the
 * developer to specify the correct configuration in order for a {@link PreparedStatement} to
 * execute as in a streaming / chunked manner.
 */
public class StreamingJdbcDatabase extends DefaultJdbcDatabase {

  private static final Logger LOGGER = LoggerFactory.getLogger(StreamingJdbcDatabase.class);

  private final Supplier<JdbcStreamingQueryConfig> streamingQueryConfigProvider;

  public StreamingJdbcDatabase(final DataSource dataSource,
                               final JdbcCompatibleSourceOperations<?> sourceOperations,
                               final Supplier<JdbcStreamingQueryConfig> streamingQueryConfigProvider) {
    super(dataSource, sourceOperations);
    this.streamingQueryConfigProvider = streamingQueryConfigProvider;
  }

  /**
   * Assuming that the {@link JdbcStreamingQueryConfig} is configured correctly for the JDBC driver
   * being used, this method will return data in streaming / chunked fashion. Review the provided
   * {@link JdbcStreamingQueryConfig} to understand the size of these chunks. If the entire stream is
   * consumed the database connection will be closed automatically and the caller need not call close
   * on the returned stream. This query (and the first chunk) are fetched immediately. Subsequent
   * chunks will not be pulled until the first chunk is consumed.
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
  @MustBeClosed
  public <T> Stream<T> unsafeQuery(final CheckedFunction<Connection, PreparedStatement, SQLException> statementCreator,
                                   final CheckedFunction<ResultSet, T, SQLException> recordTransform)
      throws SQLException {
    try {
      final Connection connection = dataSource.getConnection();
      final PreparedStatement statement = statementCreator.apply(connection);
      final JdbcStreamingQueryConfig streamingConfig = streamingQueryConfigProvider.get();
      streamingConfig.initialize(connection, statement);
      return toUnsafeStream(statement.executeQuery(), recordTransform, streamingConfig)
          .onClose(() -> {
            try {
              connection.setAutoCommit(true);
              connection.close();
              if (isStreamFailed) {
                throw new RuntimeException(streamException);
              }
            } catch (final SQLException e) {
              throw new RuntimeException(e);
            }
          });
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * This method differs from {@link DefaultJdbcDatabase#toUnsafeStream} in that it takes a streaming
   * config that adjusts the fetch size dynamically according to sampled row size.
   */
  protected <T> Stream<T> toUnsafeStream(final ResultSet resultSet,
                                         final CheckedFunction<ResultSet, T, SQLException> mapper,
                                         final JdbcStreamingQueryConfig streamingConfig) {
    return StreamSupport.stream(new Spliterators.AbstractSpliterator<>(Long.MAX_VALUE, Spliterator.ORDERED) {

      @Override
      public boolean tryAdvance(final Consumer<? super T> action) {
        try {
          if (!resultSet.next()) {
            resultSet.close();
            return false;
          }
          final T dataRow = mapper.apply(resultSet);
          streamingConfig.accept(resultSet, dataRow);
          action.accept(dataRow);
          return true;
        } catch (final SQLException e) {
          LOGGER.error("SQLState: {}, Message: {}", e.getSQLState(), e.getMessage());
          streamException = e;
          isStreamFailed = true;
          // throwing an exception in tryAdvance() method lead to the endless loop in Spliterator and stream
          // will never close
          return false;
        }
      }

    }, false);
  }

}
