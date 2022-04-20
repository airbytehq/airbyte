/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public class DefaultJdbcStreamingQueryConfig implements JdbcStreamingQueryConfiguration {

  private int fetchSize = 1000;

  @Override
  public void accept(final Connection connection, final PreparedStatement preparedStatement) throws SQLException {
    connection.setAutoCommit(false);
    preparedStatement.setFetchSize(fetchSize);
  }

  @Override
  public void setFetchSize(final int fetchSize) {
    this.fetchSize = fetchSize;
  }

}
