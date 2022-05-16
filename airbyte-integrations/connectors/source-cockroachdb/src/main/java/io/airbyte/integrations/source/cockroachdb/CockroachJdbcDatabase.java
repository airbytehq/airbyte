/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.cockroachdb;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.db.JdbcCompatibleSourceOperations;
import io.airbyte.db.jdbc.JdbcDatabase;
import java.sql.Connection;
import java.sql.DatabaseMetaData;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.stream.Stream;

/**
 * This implementation uses non-streamed queries to CockroachDB. CockroachDB does not currently
 * support multiple active pgwire portals on the same session, which makes it impossible to
 * replicate tables that have over ~1000 rows using StreamingJdbcDatabase. See:
 * https://go.crdb.dev/issue-v/40195/v21.2 and in particular, the comment:
 * https://github.com/cockroachdb/cockroach/issues/40195?version=v21.2#issuecomment-870570351 The
 * same situation as kafka-connect applies to StreamingJdbcDatabase
 */
public class CockroachJdbcDatabase
    extends JdbcDatabase {

  private final JdbcDatabase database;

  public CockroachJdbcDatabase(final JdbcDatabase database,
                               final JdbcCompatibleSourceOperations<?> sourceOperations) {
    super(sourceOperations);
    this.database = database;
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
  public <T> Stream<T> unsafeResultSetQuery(final CheckedFunction<Connection, ResultSet, SQLException> query,
                                            final CheckedFunction<ResultSet, T, SQLException> recordTransform)
      throws SQLException {
    return database.unsafeResultSetQuery(query, recordTransform);
  }

  @Override
  public <T> Stream<T> unsafeQuery(final CheckedFunction<Connection, PreparedStatement, SQLException> statementCreator,
                                   final CheckedFunction<ResultSet, T, SQLException> recordTransform)
      throws SQLException {
    return database.unsafeQuery(statementCreator, recordTransform);
  }

  @Override
  public Stream<JsonNode> unsafeQuery(final String sql, final String... params) throws SQLException {
    return bufferedResultSetQuery(connection -> {
      final PreparedStatement statement = connection.prepareStatement(sql);
      int i = 1;
      for (final String param : params) {
        statement.setString(i, param);
        ++i;
      }
      return statement.executeQuery();
    }, sourceOperations::rowToJson).stream();

  }

}
