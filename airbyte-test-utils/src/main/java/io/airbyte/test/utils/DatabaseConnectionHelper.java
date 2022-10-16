/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.utils;

import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.testcontainers.containers.JdbcDatabaseContainer;

/**
 * Helper class that facilitates the creation of database connection objects for testing purposes.
 */
public class DatabaseConnectionHelper {

  /**
   * Constructs a new {@link DataSource} using the provided configuration.
   *
   * @param container A JDBC Test Container instance.
   * @return The configured {@link DataSource}.
   */
  public static DataSource createDataSource(final JdbcDatabaseContainer container) {
    return DataSourceFactory.create(container.getUsername(),
        container.getPassword(),
        container.getDriverClassName(),
        container.getJdbcUrl());
  }

  /**
   * Constructs a configured {@link DSLContext} instance using the provided configuration.
   *
   * @param container A JDBC Test Container instance.
   * @param dialect The SQL dialect to use with objects created from this context.
   * @return The configured {@link DSLContext}.
   */
  public static DSLContext createDslContext(final JdbcDatabaseContainer container, final SQLDialect dialect) {
    return DSLContextFactory.create(
        container.getUsername(),
        container.getPassword(),
        container.getDriverClassName(),
        container.getJdbcUrl(),
        dialect);
  }

}
