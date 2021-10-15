/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance;

import io.airbyte.db.Database;
import java.io.IOException;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.testcontainers.containers.PostgreSQLContainer;

public abstract class AbstractDatabaseTest {

  protected static PostgreSQLContainer<?> container;

  @BeforeAll
  public static void dbSetup() {
    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName("airbyte")
        .withUsername("docker")
        .withPassword("docker");
    container.start();
  }

  @AfterAll
  public static void dbDown() {
    container.close();
  }

  protected Database database;

  @BeforeEach
  public void setup() throws Exception {
    database = getAndInitializeDatabase(container.getUsername(), container.getPassword(), container.getJdbcUrl());
  }

  @AfterEach
  void tearDown() throws Exception {
    database.close();
  }

  /**
   * Create an initialized database. The downstream implementation should do it by calling
   * {@link DatabaseInstance#getAndInitialize}.
   */
  public abstract Database getAndInitializeDatabase(String username, String password, String connectionString) throws IOException;

}
