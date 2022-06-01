/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.factory;

import java.util.Map;
import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.jooq.impl.DSL;

/**
 * Temporary factory class that provides convenience methods for creating a {@link DSLContext}
 * instances. This class will be removed once the project has been converted to leverage an
 * application framework to manage the creation and injection of {@link DSLContext} objects.
 */
public class DSLContextFactory {

  /**
   * Constructs a configured {@link DSLContext} instance using the provided configuration.
   *
   * @param dataSource The {@link DataSource} used to connect to the database.
   * @param dialect The SQL dialect to use with objects created from this context.
   * @return The configured {@link DSLContext}.
   */
  public static DSLContext create(final DataSource dataSource, final SQLDialect dialect) {
    return DSL.using(dataSource, dialect);
  }

  /**
   * Constructs a configured {@link DSLContext} instance using the provided configuration.
   *
   * @param username The username of the database user.
   * @param password The password of the database user.
   * @param driverClassName The fully qualified name of the JDBC driver class.
   * @param jdbcConnectionString The JDBC connection string.
   * @param dialect The SQL dialect to use with objects created from this context.
   * @return The configured {@link DSLContext}.
   */
  public static DSLContext create(final String username,
                                  final String password,
                                  final String driverClassName,
                                  final String jdbcConnectionString,
                                  final SQLDialect dialect) {
    return DSL.using(DataSourceFactory.create(username, password, driverClassName, jdbcConnectionString), dialect);
  }

  /**
   * Constructs a configured {@link DSLContext} instance using the provided configuration.
   *
   * @param username The username of the database user.
   * @param password The password of the database user.
   * @param driverClassName The fully qualified name of the JDBC driver class.
   * @param jdbcConnectionString The JDBC connection string.
   * @param dialect The SQL dialect to use with objects created from this context.
   * @param connectionProperties Additional configuration properties for the underlying driver.
   * @return The configured {@link DSLContext}.
   */
  public static DSLContext create(final String username,
                                  final String password,
                                  final String driverClassName,
                                  final String jdbcConnectionString,
                                  final SQLDialect dialect,
                                  final Map<String, String> connectionProperties) {
    return DSL.using(DataSourceFactory.create(username, password, driverClassName, jdbcConnectionString, connectionProperties), dialect);
  }

}
