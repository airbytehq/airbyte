/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.db.SqlDatabase;
import java.sql.Connection;
import java.sql.DatabaseMetaData;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.stream.Stream;

/**
 * Database object for interacting with a JDBC connection.
 */
public abstract class JdbcDatabase extends SqlDatabase {

  protected final JdbcSourceOperations sourceOperations;

  public JdbcDatabase(JdbcSourceOperations sourceOperations) {
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
  public void execute(String sql) throws SQLException {
    execute(connection -> connection.createStatement().execute(sql));
  }

  public void executeWithinTransaction(List<String> queries) throws SQLException {
    execute(connection -> {
      connection.setAutoCommit(false);
      for (String s : queries) {
        connection.createStatement().execute(s);
      }
      connection.commit();
      connection.setAutoCommit(true);
    });
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
   * need this guarantee. The caller should close the returned stream to release the database
   * connection.
   *
   * @param query execute a query using a {@link Connection} to get a {@link ResultSet}.
   * @param recordTransform transform each record of that result set into the desired type. do NOT
   *        just pass the {@link ResultSet} through. it is a stateful object will not be accessible if
   *        returned from recordTransform.
   * @param <T> type that each record will be mapped to.
   * @return Result of the query mapped to a stream.
   * @throws SQLException SQL related exceptions.
   */
  public abstract <T> Stream<T> resultSetQuery(CheckedFunction<Connection, ResultSet, SQLException> query,
                                               CheckedFunction<ResultSet, T, SQLException> recordTransform)
      throws SQLException;

  /**
   * Use a connection to create a {@link PreparedStatement} and map it into a stream. You CANNOT
   * assume that data will be returned from this method before the entire {@link ResultSet} is
   * buffered in memory. Review the implementation of the database's JDBC driver or use the
   * StreamingJdbcDriver if you need this guarantee. The caller should close the returned stream to
   * release the database connection.
   *
   * @param statementCreator create a {@link PreparedStatement} from a {@link Connection}.
   * @param recordTransform transform each record of that result set into the desired type. do NOT
   *        just pass the {@link ResultSet} through. it is a stateful object will not be accessible if
   *        returned from recordTransform.
   * @param <T> type that each record will be mapped to.
   * @return Result of the query mapped to a stream.void execute(String sql)
   * @throws SQLException SQL related exceptions.
   */
  public abstract <T> Stream<T> query(CheckedFunction<Connection, PreparedStatement, SQLException> statementCreator,
                                      CheckedFunction<ResultSet, T, SQLException> recordTransform)
      throws SQLException;

  public int queryInt(String sql, String... params) throws SQLException {
    try (Stream<Integer> q = query(c -> {
      PreparedStatement statement = c.prepareStatement(sql);
      int i = 1;
      for (String param : params) {
        statement.setString(i, param);
        ++i;
      }
      return statement;
    },
        rs -> rs.getInt(1))) {
      return q.findFirst().get();
    }
  }

  @Override
  public Stream<JsonNode> query(String sql, String... params) throws SQLException {
    return query(connection -> {
      PreparedStatement statement = connection.prepareStatement(sql);
      int i = 1;
      for (String param : params) {
        statement.setString(i, param);
        ++i;
      }
      return statement;
    }, sourceOperations::rowToJson);
  }

  public abstract DatabaseMetaData getMetaData() throws SQLException;

}
