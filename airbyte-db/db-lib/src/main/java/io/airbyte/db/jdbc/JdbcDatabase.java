/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.errorprone.annotations.MustBeClosed;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.db.JdbcCompatibleSourceOperations;
import io.airbyte.db.SqlDatabase;
import java.sql.Connection;
import java.sql.DatabaseMetaData;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.List;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.function.Consumer;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;

/**
 * Database object for interacting with a JDBC connection.
 */
public abstract class JdbcDatabase extends SqlDatabase {

  protected final JdbcCompatibleSourceOperations<?> sourceOperations;
  protected Exception streamException;
  protected boolean isStreamFailed;

  public JdbcDatabase(final JdbcCompatibleSourceOperations<?> sourceOperations) {
    this.sourceOperations = sourceOperations;
  }

  /**
   * Execute a database query.
   *
   * @param query the query to execute against the database.
   * @throws SQLException SQL related exceptions.
   */
  public abstract void execute(CheckedConsumer<Connection, SQLException> query) throws SQLException;

  @Override
  public void execute(final String sql) throws SQLException {
    execute(connection -> connection.createStatement().execute(sql));
  }

  public void executeWithinTransaction(final List<String> queries) throws SQLException {
    execute(connection -> {
      connection.setAutoCommit(false);
      for (final String s : queries) {
        connection.createStatement().execute(s);
      }
      connection.commit();
      connection.setAutoCommit(true);
    });
  }

  /**
   * Map records returned in a result set. It is an "unsafe" stream because the stream must be
   * manually closed. Otherwise, there will be a database connection leak.
   *
   * @param resultSet the result set
   * @param mapper function to make each record of the result set
   * @param <T> type that each record will be mapped to
   * @return stream of records that the result set is mapped to.
   */
  @MustBeClosed
  protected static <T> Stream<T> toUnsafeStream(final ResultSet resultSet, final CheckedFunction<ResultSet, T, SQLException> mapper) {
    return StreamSupport.stream(new Spliterators.AbstractSpliterator<>(Long.MAX_VALUE, Spliterator.ORDERED) {

      @Override
      public boolean tryAdvance(final Consumer<? super T> action) {
        try {
          if (!resultSet.next()) {
            resultSet.close();
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

  /**
   * Use a connection to create a {@link ResultSet} and map it into a list. The entire
   * {@link ResultSet} will be buffered in memory before the list is returned. The caller does not
   * need to worry about closing any database resources.
   *
   * @param query execute a query using a {@link Connection} to get a {@link ResultSet}.
   * @param recordTransform transform each record of that result set into the desired type. do NOT
   *        just pass the {@link ResultSet} through. it is a stateful object will not be accessible if
   *        returned from recordTransform.
   * @param <T> type that each record will be mapped to.
   * @return Result of the query mapped to a list.
   * @throws SQLException SQL related exceptions.
   */
  public abstract <T> List<T> bufferedResultSetQuery(CheckedFunction<Connection, ResultSet, SQLException> query,
                                                     CheckedFunction<ResultSet, T, SQLException> recordTransform)
      throws SQLException;

  /**
   * Use a connection to create a {@link ResultSet} and map it into a stream. You CANNOT assume that
   * data will be returned from this method before the entire {@link ResultSet} is buffered in memory.
   * Review the implementation of the database's JDBC driver or use the StreamingJdbcDriver if you
   * need this guarantee. It is "unsafe" because the caller should close the returned stream to
   * release the database connection. Otherwise, there will be a connection leak.
   *
   * @param query execute a query using a {@link Connection} to get a {@link ResultSet}.
   * @param recordTransform transform each record of that result set into the desired type. do NOT
   *        just pass the {@link ResultSet} through. it is a stateful object will not be accessible if
   *        returned from recordTransform.
   * @param <T> type that each record will be mapped to.
   * @return Result of the query mapped to a stream.
   * @throws SQLException SQL related exceptions.
   */
  @MustBeClosed
  public abstract <T> Stream<T> unsafeResultSetQuery(CheckedFunction<Connection, ResultSet, SQLException> query,
                                                     CheckedFunction<ResultSet, T, SQLException> recordTransform)
      throws SQLException;

  /**
   * String query is a common use case for {@link JdbcDatabase#unsafeResultSetQuery}. So this method
   * is created as syntactic sugar.
   */
  public List<String> queryStrings(final CheckedFunction<Connection, ResultSet, SQLException> query,
                                   final CheckedFunction<ResultSet, String, SQLException> recordTransform)
      throws SQLException {
    try (final Stream<String> stream = unsafeResultSetQuery(query, recordTransform)) {
      return stream.toList();
    }
  }

  /**
   * Use a connection to create a {@link PreparedStatement} and map it into a stream. You CANNOT
   * assume that data will be returned from this method before the entire {@link ResultSet} is
   * buffered in memory. Review the implementation of the database's JDBC driver or use the
   * StreamingJdbcDriver if you need this guarantee. It is "unsafe" because the caller should close
   * the returned stream to release the database connection. Otherwise, there will be a connection
   * leak.
   *
   * @param statementCreator create a {@link PreparedStatement} from a {@link Connection}.
   * @param recordTransform transform each record of that result set into the desired type. do NOT
   *        just pass the {@link ResultSet} through. it is a stateful object will not be accessible if
   *        returned from recordTransform.
   * @param <T> type that each record will be mapped to.
   * @return Result of the query mapped to a stream.void execute(String sql)
   * @throws SQLException SQL related exceptions.
   */
  @MustBeClosed
  public abstract <T> Stream<T> unsafeQuery(CheckedFunction<Connection, PreparedStatement, SQLException> statementCreator,
                                            CheckedFunction<ResultSet, T, SQLException> recordTransform)
      throws SQLException;

  /**
   * Json query is a common use case for
   * {@link JdbcDatabase#unsafeQuery(CheckedFunction, CheckedFunction)}. So this method is created as
   * syntactic sugar.
   */
  public List<JsonNode> queryJsons(final CheckedFunction<Connection, PreparedStatement, SQLException> statementCreator,
                                   final CheckedFunction<ResultSet, JsonNode, SQLException> recordTransform)
      throws SQLException {
    try (final Stream<JsonNode> stream = unsafeQuery(statementCreator, recordTransform)) {
      return stream.toList();
    }
  }

  public int queryInt(final String sql, final String... params) throws SQLException {
    try (final Stream<Integer> stream = unsafeQuery(c -> {
      PreparedStatement statement = c.prepareStatement(sql);
      int i = 1;
      for (String param : params) {
        statement.setString(i, param);
        ++i;
      }
      return statement;
    }, rs -> rs.getInt(1))) {
      return stream.findFirst().get();
    }
  }

  /**
   * It is "unsafe" because the caller must manually close the returned stream. Otherwise, there will
   * be a database connection leak.
   */
  @MustBeClosed
  @Override
  public Stream<JsonNode> unsafeQuery(final String sql, final String... params) throws SQLException {
    return unsafeQuery(connection -> {
      final PreparedStatement statement = connection.prepareStatement(sql);
      int i = 1;
      for (final String param : params) {
        statement.setString(i, param);
        ++i;
      }
      return statement;
    }, sourceOperations::rowToJson);
  }

  /**
   * Json query is a common use case for {@link JdbcDatabase#unsafeQuery(String, String...)}. So this
   * method is created as syntactic sugar.
   */
  public List<JsonNode> queryJsons(final String sql, final String... params) throws SQLException {
    try (final Stream<JsonNode> stream = unsafeQuery(sql, params)) {
      return stream.toList();
    }
  }

  public ResultSetMetaData queryMetadata(final String sql, final String... params) throws SQLException {
    try (final Stream<ResultSetMetaData> q = unsafeQuery(c -> {
      PreparedStatement statement = c.prepareStatement(sql);
      int i = 1;
      for (String param : params) {
        statement.setString(i, param);
        ++i;
      }
      return statement;
    },
        ResultSet::getMetaData)) {
      return q.findFirst().orElse(null);
    }
  }

  public abstract DatabaseMetaData getMetaData() throws SQLException;

}
