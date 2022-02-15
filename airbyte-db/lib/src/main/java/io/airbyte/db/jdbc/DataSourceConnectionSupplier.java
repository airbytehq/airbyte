package io.airbyte.db.jdbc;

import java.io.Closeable;
import java.sql.Connection;
import java.sql.SQLException;
import javax.sql.DataSource;

public class DataSourceConnectionSupplier implements CloseableConnectionSupplier {

  private final DataSource dataSource;

  public DataSourceConnectionSupplier(final DataSource dataSource) {
    this.dataSource = dataSource;
  }

  @Override
  public Connection getConnection() throws SQLException {
    return dataSource.getConnection();
  }

  @Override
  public void close() throws Exception {
    // Just a safety in case we are using a datasource implementation that requires closing.
    // BasicDataSource from apache does since it also provides a pooling mechanism to reuse connections.

    if (dataSource instanceof AutoCloseable) {
      ((AutoCloseable) dataSource).close();
    }
    if (dataSource instanceof Closeable) {
      ((Closeable) dataSource).close();
    }
  }

}
