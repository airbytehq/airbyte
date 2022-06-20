/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc.streaming;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public class NoOpStreamingQueryConfig implements JdbcStreamingQueryConfig {

  @Override
  public void initialize(final Connection connection, final Statement preparedStatement) throws SQLException {}

  @Override
  public void accept(final ResultSet resultSet, final Object o) throws SQLException {}

}
