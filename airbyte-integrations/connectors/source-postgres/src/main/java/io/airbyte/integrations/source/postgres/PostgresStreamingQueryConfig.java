/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import io.airbyte.cdk.db.jdbc.streaming.JdbcStreamingQueryConfig;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import org.jetbrains.annotations.NotNull;

public class PostgresStreamingQueryConfig implements JdbcStreamingQueryConfig {

  @Override
  public void initialize(final Connection connection, final @NotNull Statement preparedStatement) throws SQLException {
    connection.setAutoCommit(false);
    // Nothing else to do, adaptive streaming is enabled via JDBC connection parameters.
  }

  @Override
  public void accept(ResultSet resultSet, Object o) {}

}
