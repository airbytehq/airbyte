/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.development;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.instance.FlywayDatabaseMigrator;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrationDevCenter;
import io.airbyte.db.instance.jobs.JobsDatabaseMigrationDevCenter;
import java.io.IOException;
import javax.sql.DataSource;
import org.flywaydb.core.Flyway;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.ext.ScriptUtils;
import org.testcontainers.jdbc.JdbcDatabaseDelegate;

/**
 * Helper class for migration development. See README for details.
 */
public abstract class MigrationDevCenter {

  private enum Db {
    CONFIGS,
    JOBS
  }

  private enum Command {
    CREATE,
    MIGRATE,
    DUMP_SCHEMA
  }

  private final String dbIdentifier;
  private final String schemaDumpFile;
  private final String initialScript;

  protected MigrationDevCenter(final String dbIdentifier, final String schemaDumpFile, final String initialScript) {
    this.dbIdentifier = dbIdentifier;
    this.schemaDumpFile = schemaDumpFile;
    this.initialScript = initialScript;
  }

  private PostgreSQLContainer<?> createContainer() {
    final PostgreSQLContainer<?> container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName("airbyte")
        .withUsername("docker")
        .withPassword("docker");
    container.start();
    final var containerDelegate = new JdbcDatabaseDelegate(container, "");
    ScriptUtils.runInitScript(containerDelegate, initialScript);
    return container;
  }

  protected abstract FlywayDatabaseMigrator getMigrator(Database database, Flyway flyway);

  protected abstract Flyway getFlyway(DataSource dataSource);

  private Database getDatabase(final DSLContext dslContext) throws IOException {
    return new Database(dslContext);
  }

  private void createMigration() {
    try (final PostgreSQLContainer<?> container = createContainer()) {
      final DataSource dataSource =
          DataSourceFactory.create(container.getUsername(), container.getPassword(), container.getDriverClassName(), container.getJdbcUrl());
      try (final DSLContext dslContext = DSLContextFactory.create(dataSource, SQLDialect.POSTGRES)) {
        final Flyway flyway = getFlyway(dataSource);
        final Database database = getDatabase(dslContext);
        final FlywayDatabaseMigrator migrator = getMigrator(database, flyway);
        MigrationDevHelper.createNextMigrationFile(dbIdentifier, migrator);
      }
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  private void runLastMigration() {
    try (final PostgreSQLContainer<?> container = createContainer()) {
      final DataSource dataSource =
          DataSourceFactory.create(container.getUsername(), container.getPassword(), container.getDriverClassName(), container.getJdbcUrl());
      try (final DSLContext dslContext = DSLContextFactory.create(dataSource, SQLDialect.POSTGRES)) {
        final Flyway flyway = getFlyway(dataSource);
        final Database database = getDatabase(dslContext);
        final FlywayDatabaseMigrator fullMigrator = getMigrator(database, flyway);
        final DevDatabaseMigrator devDatabaseMigrator = new DevDatabaseMigrator(fullMigrator);
        MigrationDevHelper.runLastMigration(devDatabaseMigrator);
        final String schema = fullMigrator.dumpSchema();
        MigrationDevHelper.dumpSchema(schema, schemaDumpFile, false);
      }
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  @VisibleForTesting
  public String dumpSchema(final boolean persistToFile) {
    try (final PostgreSQLContainer<?> container = createContainer()) {
      final DataSource dataSource =
          DataSourceFactory.create(container.getUsername(), container.getPassword(), container.getDriverClassName(), container.getJdbcUrl());
      try (final DSLContext dslContext = DSLContextFactory.create(dataSource, SQLDialect.POSTGRES)) {
        final Flyway flyway = getFlyway(dataSource);
        final Database database = getDatabase(dslContext);
        final FlywayDatabaseMigrator migrator = getMigrator(database, flyway);
        migrator.migrate();
        final String schema = migrator.dumpSchema();
        if (persistToFile) {
          MigrationDevHelper.dumpSchema(schema, schemaDumpFile, true);
        }
        return schema;
      }
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  public static void main(final String[] args) {
    final MigrationDevCenter devCenter;

    final Db db = Db.valueOf(args[0].toUpperCase());
    switch (db) {
      case CONFIGS -> devCenter = new ConfigsDatabaseMigrationDevCenter();
      case JOBS -> devCenter = new JobsDatabaseMigrationDevCenter();
      default -> throw new IllegalArgumentException("Unexpected database: " + args[0]);
    }

    final Command command = Command.valueOf(args[1].toUpperCase());
    switch (command) {
      case CREATE -> devCenter.createMigration();
      case MIGRATE -> devCenter.runLastMigration();
      case DUMP_SCHEMA -> devCenter.dumpSchema(true);
      default -> throw new IllegalArgumentException("Unexpected command: " + args[1]);
    }
  }

}
