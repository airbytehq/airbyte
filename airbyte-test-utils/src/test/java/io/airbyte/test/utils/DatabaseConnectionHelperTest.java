/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.utils;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.zaxxer.hikari.HikariDataSource;
import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

public class DatabaseConnectionHelperTest {

  private static final String DATABASE_NAME = "airbyte_test_database";

  protected static PostgreSQLContainer<?> container;

  @BeforeAll
  public static void dbSetup() {
    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName(DATABASE_NAME)
        .withUsername("docker")
        .withPassword("docker");
    container.start();
  }

  @AfterAll
  public static void dbDown() {
    container.close();
  }

  @Test
  void testCreatingFromATestContainer() {
    final DataSource dataSource = DatabaseConnectionHelper.createDataSource(container);
    assertNotNull(dataSource);
    assertEquals(HikariDataSource.class, dataSource.getClass());
    assertEquals(5, ((HikariDataSource) dataSource).getHikariConfigMXBean().getMaximumPoolSize());
  }

  @Test
  void testCreatingADslContextFromATestContainer() {
    final SQLDialect dialect = SQLDialect.POSTGRES;
    final DSLContext dslContext = DatabaseConnectionHelper.createDslContext(container, dialect);
    assertNotNull(dslContext);
    assertEquals(dialect, dslContext.configuration().dialect());
  }

}
