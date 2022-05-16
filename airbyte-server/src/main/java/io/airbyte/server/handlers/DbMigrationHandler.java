/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.api.model.DbMigrationExecutionRead;
import io.airbyte.api.model.DbMigrationRead;
import io.airbyte.api.model.DbMigrationReadList;
import io.airbyte.api.model.DbMigrationRequestBody;
import io.airbyte.api.model.DbMigrationState;
import io.airbyte.db.Database;
import io.airbyte.db.instance.DatabaseMigrator;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.jobs.JobsDatabaseMigrator;
import java.util.stream.Collectors;
import org.flywaydb.core.Flyway;
import org.flywaydb.core.api.MigrationInfo;
import org.flywaydb.core.api.output.MigrateOutput;
import org.flywaydb.core.api.output.MigrateResult;

public class DbMigrationHandler {

  private final DatabaseMigrator configDbMigrator;
  private final DatabaseMigrator jobDbMigrator;

  public DbMigrationHandler(final Database configsDatabase, final Flyway configsFlyway, final Database jobsDatabase, final Flyway jobsFlyway) {
    this.configDbMigrator = new ConfigsDatabaseMigrator(configsDatabase, configsFlyway);
    this.jobDbMigrator = new JobsDatabaseMigrator(jobsDatabase, jobsFlyway);
  }

  public DbMigrationReadList list(final DbMigrationRequestBody request) {
    final DatabaseMigrator migrator = getMigrator(request.getDatabase());
    return new DbMigrationReadList()
        .migrations(migrator.list().stream().map(DbMigrationHandler::toMigrationRead).collect(Collectors.toList()));
  }

  public DbMigrationExecutionRead migrate(final DbMigrationRequestBody request) {
    final DatabaseMigrator migrator = getMigrator(request.getDatabase());
    final MigrateResult result = migrator.migrate();
    return new DbMigrationExecutionRead()
        .initialVersion(result.initialSchemaVersion)
        .targetVersion(result.targetSchemaVersion)
        .executedMigrations(result.migrations.stream().map(DbMigrationHandler::toMigrationRead).collect(Collectors.toList()));
  }

  private DatabaseMigrator getMigrator(final String database) {
    if (database.equalsIgnoreCase("configs")) {
      return configDbMigrator;
    } else if (database.equalsIgnoreCase("jobs")) {
      return jobDbMigrator;
    }
    throw new IllegalArgumentException("Unexpected database: " + database);
  }

  private static DbMigrationRead toMigrationRead(final MigrationInfo info) {
    return new DbMigrationRead()
        .migrationType(info.getType().name())
        .migrationVersion(info.getVersion().toString())
        .migrationDescription(info.getDescription())
        .migrationState(DbMigrationState.fromValue(info.getState().name()))
        .migratedBy(info.getInstalledBy())
        .migratedAt(info.getInstalledOn() == null ? null : info.getInstalledOn().getTime())
        .migrationScript(info.getScript());
  }

  private static DbMigrationRead toMigrationRead(final MigrateOutput output) {
    return new DbMigrationRead()
        .migrationType(String.format("%s %s", output.type, output.category))
        .migrationVersion(output.version)
        .migrationDescription(output.description)
        .migrationScript(output.filepath);
  }

}
