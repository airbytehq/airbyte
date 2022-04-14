/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance;

import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import java.io.Closeable;
import java.io.IOException;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.testcontainers.containers.PostgreSQLContainer;

public abstract class AbstractDatabaseTest {

  protected static PostgreSQLContainer<?> container;
  protected static DataSource dataSource;

  @BeforeAll
  public static void dbSetup() {
    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName("airbyte")
        .withUsername("docker")
        .withPassword("docker");
    container.start();
    dataSource = Databases.dataSourceBuilder()
        .withJdbcUrl(container.getJdbcUrl())
        .withPassword(container.getPassword())
        .withUsername(container.getUsername())
        .build();
  }

  @AfterAll
  public static void dbDown() {
    container.close();
  }

  protected Database database;

  @BeforeEach
  public void setup() throws Exception {
    database = getDatabase();
  }

  @AfterEach
  void tearDown() throws Exception {
    if (dataSource instanceof Closeable) {
      ((Closeable) dataSource).close();
    }
  }

  /**
   * Create an initialized database. The downstream implementation should do it by calling
   * {@link DatabaseInstance#getAndInitialize} or {@link DatabaseInstance#getInitialized}, and
   * {@link DatabaseMigrator#migrate} if necessary.
   */
  public abstract Database getDatabase() throws IOException;

}
