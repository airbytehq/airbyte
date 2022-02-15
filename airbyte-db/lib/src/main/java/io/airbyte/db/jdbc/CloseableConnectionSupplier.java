package io.airbyte.db.jdbc;

import java.sql.Connection;
import java.sql.SQLException;

public interface CloseableConnectionSupplier extends AutoCloseable {

  Connection getConnection() throws SQLException;

}
