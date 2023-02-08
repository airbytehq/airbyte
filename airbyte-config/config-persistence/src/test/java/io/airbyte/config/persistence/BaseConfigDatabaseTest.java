/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.init.DatabaseInitializationException;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.configs.ConfigsDatabaseTestProvider;
import io.airbyte.db.instance.test.TestDatabaseProviders;
import io.airbyte.test.utils.DatabaseConnectionHelper;
import java.io.IOException;
import java.sql.SQLException;
import javax.sql.DataSource;
import org.flywaydb.core.Flyway;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.testcontainers.containers.PostgreSQLContainer;

/**
 * This class exists to abstract away the lifecycle of the test container database and the config
 * database schema. This is ALL it intends to do. Any additional functionality belongs somewhere
 * else. It is useful for test suites that need to interact directly with the database.
 *
 * This class sets up a test container database and runs the config database migrations against it
 * to provide the most up-to-date schema.
 *
 * What this class is NOT designed to do:
 * <ul>
 * <li>test migration behavior, only should be used to test query behavior against the current
 * schema.</li>
 * <li>expose database details -- if you are attempting to expose container, dataSource, dslContext,
 * something is wrong.</li>
 * <li>add test fixtures or helpers--do NOT put "generic" resource helper methods (e.g.
 * createTestSource())</li>
 * </ul>
 *
 * This comment is emphatically worded, because it is tempting to add things to this class. It has
 * already happened in 3 previous iterations, and each time it takes multiple engineering days to
 * fix it.
 *
 * Usage:
 * <ul>
 * <li>Extend: Extend this class. By doing so, it will automatically create the test container db
 * and run migrations against it at the start of the test suite (@BeforeAll).</li>
 * <li>Use database: As part of the @BeforeAll the database field is set. This is the only field
 * that the extending class can access. It's lifecycle is fully managed by this class.</li>
 * <li>Reset schema: To reset the database in between tests, call truncateAllTables() as part
 * of @BeforeEach. This is the only method that this class exposes externally. It is exposed in such
 * a way, because most test suites need to declare their own @BeforeEach, so it is easier for them
 * to simply call this method there, then trying to apply a more complex inheritance scheme.</li>
 * </ul>
 *
 * Note: truncateAllTables() works by truncating each table in the db, if you add a new table, you
 * will need to add it to that method for it work as expected.
 */
@SuppressWarnings({"PMD.MutableStaticState", "PMD.SignatureDeclareThrowsException"})
class BaseConfigDatabaseTest {

  static Database database;

  // keep these private, do not expose outside this class!
  private static PostgreSQLContainer<?> container;
  private static DataSource dataSource;
  private static DSLContext dslContext;

  /**
   * Create db test container, sets up java database resources, and runs migrations. Should not be
   * called externally. It is not private because junit cannot access private methods.
   *
   * @throws DatabaseInitializationException - db fails to initialize
   * @throws IOException - failure when interacting with db.
   */
  @BeforeAll
  static void dbSetup() throws DatabaseInitializationException, IOException {
    createDbContainer();
    setDb();
    migrateDb();
  }

  /**
   * Close all resources (container, data source, dsl context, database). Should not be called
   * externally. It is not private because junit cannot access private methods.
   *
   * @throws Exception - exception while closing resources
   */
  @AfterAll
  static void dbDown() throws Exception {
    dslContext.close();
    DataSourceFactory.close(dataSource);
    container.close();
  }

  /**
   * Truncates tables to reset them. Designed to be used in between tests.
   *
   * Note: NEW TABLES -- When a new table is added to the db, it will need to be added here.
   *
   * @throws SQLException - failure in truncate query.
   */
  static void truncateAllTables() throws SQLException {
    database.query(ctx -> ctx
        .execute(
            """
            TRUNCATE TABLE
              actor,
              actor_catalog,
              actor_catalog_fetch_event,
              actor_definition,
              actor_definition_workspace_grant,
              actor_oauth_parameter,
              connection,
              connection_operation,
              operation,
              state,
              stream_reset,
              workspace,
              workspace_service_account
            """));
  }

  private static void createDbContainer() {
    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName("airbyte")
        .withUsername("docker")
        .withPassword("docker");
    container.start();
  }

  private static void setDb() throws DatabaseInitializationException, IOException {
    dataSource = DatabaseConnectionHelper.createDataSource(container);
    dslContext = DSLContextFactory.create(dataSource, SQLDialect.POSTGRES);
    final TestDatabaseProviders databaseProviders = new TestDatabaseProviders(dataSource, dslContext);
    database = databaseProviders.createNewConfigsDatabase();
    databaseProviders.createNewJobsDatabase();
  }

  private static void migrateDb() throws IOException, DatabaseInitializationException {
    final Flyway flyway = FlywayFactory.create(
        dataSource,
        StreamResetPersistenceTest.class.getName(),
        ConfigsDatabaseMigrator.DB_IDENTIFIER,
        ConfigsDatabaseMigrator.MIGRATION_FILE_LOCATION);
    new ConfigsDatabaseTestProvider(dslContext, flyway).create(true);
  }

}
