/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.db2;

import io.airbyte.db.jdbc.JdbcStreamingQueryConfiguration;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public class Db2JdbcStreamingQueryConfiguration implements
    JdbcStreamingQueryConfiguration {

  @Override
  public void accept(Connection connection, PreparedStatement preparedStatement)
      throws SQLException {
    connection.setAutoCommit(false);
    preparedStatement.setFetchSize(1000);
  }

}
