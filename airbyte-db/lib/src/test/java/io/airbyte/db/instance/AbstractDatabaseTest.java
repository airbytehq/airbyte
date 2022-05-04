/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance;

import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.test.utils.DatabaseConnectionHelper;
import java.io.Closeable;
import java.io.IOException;
import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
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
  protected DataSource dataSource;
  protected DSLContext dslContext;

  @BeforeEach
  public void setup() throws IOException {
    dataSource = DatabaseConnectionHelper.createDataSource(container);
    dslContext = DSLContextFactory.create(dataSource, SQLDialect.POSTGRES);
    database = getDatabase(dataSource, dslContext);
  }

  @AfterEach
  void tearDown() throws IOException {
    dslContext.close();
    if (dataSource instanceof Closeable closeable) {
      closeable.close();
    }
  }

  /**
   * Create an initialized {@link Database}. The downstream implementation should do it by calling
   * {@link DatabaseInstance#getAndInitialize} or {@link DatabaseInstance#getInitialized}, and
   * {@link DatabaseMigrator#migrate} if necessary.
   *
   * @param dataSource The {@link DataSource} used to access the database.
   * @param dslContext The {@link DSLContext} used to execute queries.
   * @return an initialized {@link Database} instance.
   */
  public abstract Database getDatabase(DataSource dataSource, DSLContext dslContext) throws IOException;

  public DataSource getDataSource() {
    return dataSource;
  }

  public DSLContext getDslContext() {
    return dslContext;
  }

}
