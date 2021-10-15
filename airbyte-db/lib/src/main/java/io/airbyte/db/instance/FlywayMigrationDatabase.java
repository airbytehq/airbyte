/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance;

import io.airbyte.db.Database;
import java.io.IOException;
import java.sql.Connection;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.jooq.impl.DSL;
import org.jooq.meta.postgres.PostgresDatabase;
import org.jooq.tools.StringUtils;
import org.jooq.tools.jdbc.JDBCUtils;
import org.testcontainers.containers.PostgreSQLContainer;

/**
 * Custom database for jOOQ code generation. It performs the following operations:
 * <li>Run Flyway migration.</li>
 * <li>Dump the database schema.</li>
 * <li>Create a connection for jOOQ code generation.</li>
 * <p/>
 * Reference: https://github.com/sabomichal/jooq-meta-postgres-flyway
 */
public abstract class FlywayMigrationDatabase extends PostgresDatabase {

  private static final String DEFAULT_DOCKER_IMAGE = "postgres:13-alpine";

  private Connection connection;

  private final String schemaDumpFile;

  protected FlywayMigrationDatabase(String schemaDumpFile) {
    this.schemaDumpFile = schemaDumpFile;
  }

  protected abstract Database getAndInitializeDatabase(String username, String password, String connectionString) throws IOException;

  protected abstract DatabaseMigrator getDatabaseMigrator(Database database);

  @Override
  protected DSLContext create0() {
    return DSL.using(getInternalConnection(), SQLDialect.POSTGRES);
  }

  protected Connection getInternalConnection() {
    if (connection == null) {
      try {
        createInternalConnection();
      } catch (Exception e) {
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

    PostgreSQLContainer<?> container = new PostgreSQLContainer<>(dockerImage)
        .withDatabaseName("jooq_airbyte_configs")
        .withUsername("jooq_generator")
        .withPassword("jooq_generator");
    container.start();

    Database database = getAndInitializeDatabase(container.getUsername(), container.getPassword(), container.getJdbcUrl());
    DatabaseMigrator migrator = getDatabaseMigrator(database);
    migrator.migrate();

    connection = database.getDataSource().getConnection();
    setConnection(connection);
  }

  @Override
  public void close() {
    JDBCUtils.safeClose(connection);
    connection = null;
    super.close();
  }

}
