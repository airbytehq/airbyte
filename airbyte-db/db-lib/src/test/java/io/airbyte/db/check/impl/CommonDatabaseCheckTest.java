/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.check.impl;

import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.testcontainers.containers.PostgreSQLContainer;

/**
 * Common test setup for database availability check tests.
 */
abstract class CommonDatabaseCheckTest {

  protected static final long TIMEOUT_MS = 500L;

  static final protected PostgreSQLContainer<?> container;

  static final protected DataSource dataSource;

  static final protected DSLContext dslContext;

  static {
    container = new PostgreSQLContainer<>("postgres:13-alpine");
    container.start();

    dataSource = DataSourceFactory.create(container.getUsername(), container.getPassword(),
        container.getDriverClassName(), container.getJdbcUrl());
    dslContext = DSLContextFactory.create(dataSource, SQLDialect.POSTGRES);
  }

}
