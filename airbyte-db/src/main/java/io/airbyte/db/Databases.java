package io.airbyte.db;

import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.SQLDialect;

public class Databases {

  public static DatabaseHandle createPostgresHandle(String username, String password, String jdbcConnectionString) {
    return createHandle(username, password, jdbcConnectionString, "org.postgresql.Driver", SQLDialect.POSTGRES);
  }

  public static DatabaseHandle createHandle(final String username,
                                         final String password,
                                         final String jdbcConnectionString,
                                         final String driverClassName,
                                         final SQLDialect dialect) {
    final BasicDataSource connectionPool = new BasicDataSource();
    connectionPool.setDriverClassName(driverClassName);
    connectionPool.setUsername(username);
    connectionPool.setPassword(password);
    connectionPool.setUrl(jdbcConnectionString);

    return new DatabaseHandle(connectionPool, dialect);
  }

}
