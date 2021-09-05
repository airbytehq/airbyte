/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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

  /**
   * Directory under which a new migration will be created. This should match the database's name and
   * match the {@link Db} enum. Set in main to enforce correct implementation.
   */
  private static String migrationDirectory;

  private final String schemaDumpFile;

  protected MigrationDevCenter(String schemaDumpFile) {
    this.schemaDumpFile = schemaDumpFile;
  }

  private static PostgreSQLContainer<?> createContainer() {
    PostgreSQLContainer<?> container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName("airbyte")
        .withUsername("docker")
        .withPassword("docker");
    container.start();
    return container;
  }

  protected abstract FlywayDatabaseMigrator getMigrator(Database database);

  protected abstract Database getDatabase(PostgreSQLContainer<?> container) throws IOException;

  private void createMigration() {
    try (PostgreSQLContainer<?> container = createContainer(); Database database = getDatabase(container)) {
      FlywayDatabaseMigrator migrator = getMigrator(database);
      MigrationDevHelper.createNextMigrationFile(migrationDirectory, migrator);
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  private void runLastMigration() {
    try (PostgreSQLContainer<?> container = createContainer(); Database database = getDatabase(container)) {
      FlywayDatabaseMigrator fullMigrator = getMigrator(database);
      DevDatabaseMigrator devDatabaseMigrator = new DevDatabaseMigrator(fullMigrator);
      MigrationDevHelper.runLastMigration(devDatabaseMigrator);
      String schema = fullMigrator.dumpSchema();
      MigrationDevHelper.dumpSchema(schema, schemaDumpFile, false);
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  private void dumpSchema() {
    try (PostgreSQLContainer<?> container = createContainer(); Database database = getDatabase(container)) {
      FlywayDatabaseMigrator migrator = getMigrator(database);
      migrator.migrate();
      String schema = migrator.dumpSchema();
      MigrationDevHelper.dumpSchema(schema, schemaDumpFile, true);
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  public static void main(String[] args) {
    final MigrationDevCenter devCenter;

    Db db = Db.valueOf(args[0].toUpperCase());
    switch (db) {
      case CONFIGS -> {
        devCenter = new ConfigsDatabaseMigrationDevCenter();
        migrationDirectory = "configs";
      }
      case JOBS -> {
        devCenter = new JobsDatabaseMigrationDevCenter();
        migrationDirectory = "jobs";
      }
      default -> throw new IllegalArgumentException("Unexpected database: " + args[0]);
    }

    Command command = Command.valueOf(args[1].toUpperCase());
    switch (command) {
      case CREATE -> devCenter.createMigration();
      case MIGRATE -> devCenter.runLastMigration();
      case DUMP_SCHEMA -> devCenter.dumpSchema();
      default -> throw new IllegalArgumentException("Unexpected command: " + args[1]);
    }
  }

}
