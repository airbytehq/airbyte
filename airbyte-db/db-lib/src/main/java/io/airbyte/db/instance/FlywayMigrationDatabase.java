/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance;

import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.init.DatabaseInitializationException;
import java.io.IOException;
import java.sql.Connection;
import javax.sql.DataSource;
import org.flywaydb.core.Flyway;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.jooq.impl.DSL;
import org.jooq.meta.postgres.PostgresDatabase;
import org.jooq.tools.StringUtils;
import org.jooq.tools.jdbc.JDBCUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.PostgreSQLContainer;

/**
 * Custom database for jOOQ code generation. It performs the following operations:
 * <ul>
 * <li>Run Flyway migration.</li>
 * <li>Dump the database schema.</li>
 * <li>Create a connection for jOOQ code generation.</li>
 * </ul>
 * <p>
 * </p>
 * Reference: https://github.com/sabomichal/jooq-meta-postgres-flyway
 */
public abstract class FlywayMigrationDatabase extends PostgresDatabase {

  private static final Logger LOGGER = LoggerFactory.getLogger(FlywayMigrationDatabase.class);

  private static final String DEFAULT_DOCKER_IMAGE = "postgres:13-alpine";

  private Connection connection;

  private DataSource dataSource;

  private DSLContext dslContext;

  protected abstract Database getDatabase(DSLContext dslContext) throws IOException;

  protected abstract DatabaseMigrator getDatabaseMigrator(Database database, Flyway flyway);

  protected abstract String getInstalledBy();

  protected abstract String getDbIdentifier();

  protected abstract String[] getMigrationFileLocations();

  protected abstract void initializeDatabase(final DSLContext dslContext) throws DatabaseInitializationException, IOException;

  @Override
  protected DSLContext create0() {
    return DSL.using(getInternalConnection(), SQLDialect.POSTGRES);
  }

  protected Connection getInternalConnection() {
    if (connection == null) {
      try {
        createInternalConnection();
      } catch (final Exception e) {
        throw new RuntimeException("Failed to launch postgres container and run migration", e);
      }
    }
    return connection;
  }

  private void createInternalConnection() throws Exception {
    String dockerImage = getProperties().getProperty("dockerImage");
    if (StringUtils.isBlank(dockerImage)) {
      dockerImage = DEFAULT_DOCKER_IMAGE;
    }

    final PostgreSQLContainer<?> container = new PostgreSQLContainer<>(dockerImage)
        .withDatabaseName("jooq_airbyte_configs")
        .withUsername("jooq_generator")
        .withPassword("jooq_generator");
    container.start();

    dataSource =
        DataSourceFactory.create(container.getUsername(), container.getPassword(), container.getDriverClassName(), container.getJdbcUrl());
    dslContext = DSLContextFactory.create(dataSource, SQLDialect.POSTGRES);

    initializeDatabase(dslContext);

    final Flyway flyway = FlywayFactory.create(dataSource, getInstalledBy(), getDbIdentifier(), getMigrationFileLocations());
    final Database database = getDatabase(dslContext);
    final DatabaseMigrator migrator = getDatabaseMigrator(database, flyway);
    migrator.migrate();

    connection = dataSource.getConnection();
    setConnection(connection);
  }

  @Override
  public void close() {
    JDBCUtils.safeClose(connection);
    connection = null;
    dslContext.close();
    try {
      DataSourceFactory.close(dataSource);
    } catch (final Exception e) {
      LOGGER.warn("Unable to close data source.", e);
    }
    super.close();
  }

}
