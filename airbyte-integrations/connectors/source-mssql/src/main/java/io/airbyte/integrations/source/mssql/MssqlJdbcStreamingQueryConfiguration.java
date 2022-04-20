/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import io.airbyte.db.jdbc.DefaultJdbcStreamingQueryConfig;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public class MssqlJdbcStreamingQueryConfiguration extends DefaultJdbcStreamingQueryConfig {

  @Override
  public void accept(final Connection connection, final PreparedStatement preparedStatement) throws SQLException {
    connection.setAutoCommit(false);
    preparedStatement.setFetchSize(1000);
  }

}
