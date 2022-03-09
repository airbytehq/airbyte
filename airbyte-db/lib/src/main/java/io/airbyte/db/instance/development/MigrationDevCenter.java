/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.development;

import io.airbyte.db.Database;
import io.airbyte.db.instance.FlywayDatabaseMigrator;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrationDevCenter;
import io.airbyte.db.instance.jobs.JobsDatabaseMigrationDevCenter;
import java.io.IOException;
import org.testcontainers.containers.PostgreSQLContainer;

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

  protected MigrationDevCenter(final String dbIdentifier, final String schemaDumpFile) {
    this.dbIdentifier = dbIdentifier;
    this.schemaDumpFile = schemaDumpFile;
  }

  private static PostgreSQLContainer<?> createContainer() {
    final PostgreSQLContainer<?> container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName("airbyte")
        .withUsername("docker")
        .withPassword("docker");
    container.start();
    return container;
  }

  protected abstract FlywayDatabaseMigrator getMigrator(Database database);

  protected abstract Database getDatabase(PostgreSQLContainer<?> container) throws IOException;

  private void createMigration() {
    try (final PostgreSQLContainer<?> container = createContainer(); final Database database = getDatabase(container)) {
      final FlywayDatabaseMigrator migrator = getMigrator(database);
      MigrationDevHelper.createNextMigrationFile(dbIdentifier, migrator);
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  private void runLastMigration() {
    try (final PostgreSQLContainer<?> container = createContainer(); final Database database = getDatabase(container)) {
      final FlywayDatabaseMigrator fullMigrator = getMigrator(database);
      final DevDatabaseMigrator devDatabaseMigrator = new DevDatabaseMigrator(fullMigrator);
      MigrationDevHelper.runLastMigration(devDatabaseMigrator);
      final String schema = fullMigrator.dumpSchema();
      MigrationDevHelper.dumpSchema(schema, schemaDumpFile, false);
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  private void dumpSchema() {
    try (final PostgreSQLContainer<?> container = createContainer(); final Database database = getDatabase(container)) {
      final FlywayDatabaseMigrator migrator = getMigrator(database);
      migrator.migrate();
      final String schema = migrator.dumpSchema();
      MigrationDevHelper.dumpSchema(schema, schemaDumpFile, true);
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
      case DUMP_SCHEMA -> devCenter.dumpSchema();
      default -> throw new IllegalArgumentException("Unexpected command: " + args[1]);
    }
  }

}
