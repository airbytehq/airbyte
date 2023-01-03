/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.init.impl;

import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.testcontainers.containers.PostgreSQLContainer;

/**
 * Common test setup for database initialization tests.
 */
class CommonDatabaseInitializerTest {

  protected PostgreSQLContainer<?> container;

  protected DataSource dataSource;

  protected DSLContext dslContext;

  @BeforeEach
  void setup() {
    container = new PostgreSQLContainer<>("postgres:13-alpine");
    container.start();

    dataSource = DataSourceFactory.create(container.getUsername(), container.getPassword(), container.getDriverClassName(), container.getJdbcUrl());
    dslContext = DSLContextFactory.create(dataSource, SQLDialect.POSTGRES);
  }

  @SuppressWarnings("PMD.SignatureDeclareThrowsException")
  @AfterEach
  void cleanup() throws Exception {
    DataSourceFactory.close(dataSource);
    dslContext.close();
    container.stop();
  }

}
