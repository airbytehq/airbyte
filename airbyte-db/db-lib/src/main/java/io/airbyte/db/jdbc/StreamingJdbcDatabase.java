/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.errorprone.annotations.MustBeClosed;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.db.JdbcCompatibleSourceOperations;
import io.airbyte.db.jdbc.streaming.JdbcStreamingQueryConfig;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Consumer;
import java.util.function.Supplier;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;
import javax.sql.DataSource;
import org.apache.commons.lang3.StringUtils;
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

  @Override
  @MustBeClosed
  public <T> Stream<T> unsafeQueries(final CheckedFunction<Connection, List<PreparedStatement>, SQLException> statementCreator,
      final CheckedFunction<ResultSet, T, SQLException> recordTransform)
      throws SQLException {
    try {
      final Connection connection = dataSource.getConnection();
      final List<PreparedStatement> statements = statementCreator.apply(connection);
      final JdbcStreamingQueryConfig streamingConfig = streamingQueryConfigProvider.get();
      streamingConfig.initialize(connection, statements.get(0)); //TEMP
      return toUnsafeStreams(statements, recordTransform, streamingConfig)
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

  protected <T> Stream<T> toUnsafeStreams(final List<PreparedStatement> statements,
      final CheckedFunction<ResultSet, T, SQLException> mapper,
      final JdbcStreamingQueryConfig streamingConfig) {
    statements.clear(); // TEMP
    final var it = statements.listIterator();

    return StreamSupport.stream(new Spliterators.AbstractSpliterator<>(Long.MAX_VALUE, Spliterator.ORDERED) {
      private ResultSet currentResultSet = null;
      private Connection currConn = null;
      boolean added = false;
      OffsetDateTime startTime = null;
      private String loadNextQuery(final long weNeed) throws SQLException {
        final String quotedCursorField = "\"created_at\"";
        final String qualifiedTableName = "\"2b_users\".\"users\"";
        final String columnList = "\"id\",\"age\",\"name\",\"email\",\"title\",\"gender\",\"height\",\"weight\",\"language\",\"telephone\",\"blood_type\",\"created_at\",\"occupation\",\"updated_at\",\"nationality\",\"academic_degree\"";
        if (startTime == null) {
          AtomicReference<OffsetDateTime> minDate = new AtomicReference<>();
          AtomicLong quickCount = new AtomicLong();
          List<OffsetDateTime> stream = bufferedResultSetQuery(connection -> connection.createStatement().executeQuery("select MIN(created_at) from %s".formatted(qualifiedTableName)),
              resultSet -> resultSet.getObject("min", OffsetDateTime.class));

          stream.stream().findFirst().ifPresent(d -> {
            LOGGER.info("*** min is {}", d.toString());
            minDate.set(d);
          });
          startTime = minDate.get();
        }
        double eachRec = 2.8;
        var upperLimit = startTime.plus((long)(weNeed * eachRec), ChronoUnit.SECONDS);
        String firstAttemptQuery = "select count(%s) from %s where %s > '%s' AND %s <= '%s'".formatted(quotedCursorField, qualifiedTableName, quotedCursorField, startTime.toString(), quotedCursorField, upperLimit.toString());
        LOGGER.info("*** query {}", firstAttemptQuery);
        List<Long> firstAttemptList = bufferedResultSetQuery(connection -> connection.createStatement().executeQuery(firstAttemptQuery),
            resultSet -> resultSet.getLong("count"));
        long firstAttempt = firstAttemptList.get(0);
        LOGGER.info("*** first attempt got {} records", firstAttempt);
        if (firstAttempt == 0) {
          return null;
        }
        double ratio = (double)weNeed / (double)firstAttempt;
        long actualOffset = Math.max((long)(weNeed * eachRec * ratio), 120);
        LOGGER.info("*** ratio {} actualOffset {} seconds", ratio, actualOffset);
//        actualOffset = Math.max(actualOffset / 2, 100L); //TEMP
//        LOGGER.info("*** half -- ratio {} actualOffset {} seconds", ratio, actualOffset);
        upperLimit = startTime.plus(actualOffset, ChronoUnit.SECONDS);
        String secondAttemptQuery = "select count(%s) from %s where %s > '%s' AND %s <= '%s'".formatted(quotedCursorField, qualifiedTableName, quotedCursorField, startTime.toString(), quotedCursorField, upperLimit.toString());
        LOGGER.info("*** 2nd query {}", secondAttemptQuery);
        List<Long> secondAttemptList = bufferedResultSetQuery(connection -> connection.createStatement().executeQuery(secondAttemptQuery),
            resultSet -> resultSet.getLong("count"));
        long secondAttempt = secondAttemptList.get(0);

        LOGGER.info("*** second attempt got {} records", secondAttempt);
//        final var sttmnt = "SELECT %s FROM %s where \"created_at\" > '%s' and \"created_at\" <= '%s' ORDER BY %s ASC".formatted(columnList, qualifiedTableName, startTime.toString(), upperLimit.toString(), quotedCursorField);
        final var sttmnt = "SELECT %s FROM %s where \"created_at\" > '%s' and \"created_at\" <= '%s'".formatted(columnList, qualifiedTableName, startTime.toString(), upperLimit.toString());
        startTime = upperLimit;
        return sttmnt;
      }
      private ResultSet getNext() {
        try {
//          LOGGER.info("*** currentResultSet is {}", currentResultSet);
          if (currentResultSet == null || !currentResultSet.next()) {
            if (currentResultSet != null) {
              LOGGER.info("*** closing");
              currentResultSet.close();
              if (currConn != null) {
                currConn.setAutoCommit(true);
                currConn.close();
              }
            }
            LOGGER.info("*** loading next query for size {} (start {})", streamingConfig.getFetchSize(), startTime);
//            for (int i = 0; i < 10; i++) {
//              loadNextQuery(1_000_000);
//            }
            final var qr = loadNextQuery(streamingConfig.getFetchSize());
            if (StringUtils.isNotBlank(qr)) {
              it.add(dataSource.getConnection().prepareStatement(qr));
              it.previous();
            }

            LOGGER.info("*** getting next statement: {}", it.hasNext());
            while (it.hasNext()) {
              final var statement = it.next();
//              streamingConfig.initialize(statement.getConnection(), statement);
//              statement.getConnection().setAutoCommit(false);
//              statement.setFetchSize(streamingConfig.getFetchSize());
              LOGGER.info("*** statement {}", statement);
              currentResultSet = statement.executeQuery();
              currConn = statement.getConnection();
              LOGGER.info("*** new currentResultSet is {}", currentResultSet);
              if (currentResultSet.next()) {
                LOGGER.info("*** returning new currentResultSet");
                return currentResultSet;
              } else {
                LOGGER.info("*** nothing left to read in current result set");
                currentResultSet.close();
                if (currConn != null) {
                  currConn.setAutoCommit(true);
                  currConn.close();
                }
              }
            }
            LOGGER.info("*** end of statements");
            return null;
          }
//          LOGGER.info("*** continuing with currentResultSet");
          return currentResultSet;
        } catch (final SQLException ex) {
          LOGGER.error("error executing query", ex);
          return null;
        }
      }
      @Override
      public boolean tryAdvance(final Consumer<? super T> action) {
        try {
//          LOGGER.info("*** getting next");
          final var resultSet = getNext();
//          LOGGER.info("*** next is {}", resultSet);
          if (resultSet == null) {
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
