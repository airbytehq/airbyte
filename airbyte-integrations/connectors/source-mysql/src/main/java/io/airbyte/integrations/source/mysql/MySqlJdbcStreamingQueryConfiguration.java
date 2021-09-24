/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import io.airbyte.db.jdbc.JdbcStreamingQueryConfiguration;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public class MySqlJdbcStreamingQueryConfiguration implements JdbcStreamingQueryConfiguration {

  @Override
  public void accept(Connection connection, PreparedStatement preparedStatement) throws SQLException {
    // This is only respected if "useCursorFetch=true" is set in the connection. See the "resultset"
    // section the MySql docs for more details.
    // https://dev.mysql.com/doc/connector-j/8.0/en/connector-j-reference-implementation-notes.html.
    // When using this approach MySql creates a temporary table which may have some effect on db
    // performance.
    // e.g. conn = DriverManager.getConnection("jdbc:mysql://localhost/?useCursorFetch=true", "user",
    // "s3cr3t");
    // We set userCursorFetch in MySqlSource.
    connection.setAutoCommit(false);
    preparedStatement.setFetchSize(1000);
    // If for some reason, you cannot set useCursorFetch in the connection, fall back on this
    // implementation below. It fetches records one at a time, which while inefficient, at least does
    // not risk OOM.
    // connection.setAutoCommit(false);
    // preparedStatement.setFetchSize(Integer.MIN_VALUE);
  }

}
