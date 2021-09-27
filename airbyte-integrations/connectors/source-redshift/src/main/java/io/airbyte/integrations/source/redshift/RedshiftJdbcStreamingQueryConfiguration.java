/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.redshift;

import io.airbyte.db.jdbc.JdbcStreamingQueryConfiguration;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public class RedshiftJdbcStreamingQueryConfiguration implements JdbcStreamingQueryConfiguration {

  // aws docs on how setting up batching:
  // https://docs.aws.amazon.com/redshift/latest/dg/queries-troubleshooting.html
  @Override
  public void accept(Connection connection, PreparedStatement preparedStatement) throws SQLException {
    connection.setAutoCommit(false);
    preparedStatement.setFetchSize(1000);
  }

}
