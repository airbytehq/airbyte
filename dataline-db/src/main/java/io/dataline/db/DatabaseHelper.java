package io.dataline.db;

import java.sql.Connection;
import java.sql.SQLException;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.jooq.impl.DSL;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DatabaseHelper {
  private static final Logger LOGGER = LoggerFactory.getLogger(DatabaseHelper.class);

  public static synchronized BasicDataSource getConnectionPool(
      String username, String password, String jdbcConnectionString) {

    BasicDataSource connectionPool = new BasicDataSource();
    connectionPool.setDriverClassName("org.sqlite.JDBC");
    connectionPool.setUsername(username);
    connectionPool.setPassword(password);
    connectionPool.setUrl(jdbcConnectionString);

    return connectionPool;
  }

  public static DSLContext getContext(Connection connection) {
    return DSL.using(connection, SQLDialect.POSTGRES);
  }

  public static <T> T query(BasicDataSource connectionPool, ContextQueryFunction<T> transform)
      throws SQLException {
    try (Connection connection = connectionPool.getConnection()) {
      DSLContext context = getContext(connection);
      return transform.apply(context);
    }
  }
}
