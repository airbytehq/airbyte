package io.airbyte.db.jdbc;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public class DefaultJdbcStreamingQueryConfig implements JdbcStreamingQueryConfiguration {

  @Override
  public void accept(final Connection connection, final PreparedStatement preparedStatement) throws SQLException {
    connection.setAutoCommit(false);
    preparedStatement.setFetchSize(1000);
  }

}
