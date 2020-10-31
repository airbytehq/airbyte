package io.airbyte.db;

import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.SQLDialect;

public class Databases {

  public static Database createPostgresDatabase(String username, String password, String jdbcConnectionString) {
    return createDatabase(username, password, jdbcConnectionString, "org.postgresql.Driver", SQLDialect.POSTGRES);
  }

  public static Database createDatabase(final String username,
                                        final String password,
                                        final String jdbcConnectionString,
                                        final String driverClassName,
                                        final SQLDialect dialect) {
    final BasicDataSource connectionPool = new BasicDataSource();
    connectionPool.setDriverClassName(driverClassName);
    connectionPool.setUsername(username);
    connectionPool.setPassword(password);
    connectionPool.setUrl(jdbcConnectionString);

    return new Database(connectionPool, dialect);
  }

}
