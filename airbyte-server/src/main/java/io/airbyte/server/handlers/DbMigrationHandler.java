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
import org.flywaydb.core.api.MigrationInfo;
import org.flywaydb.core.api.output.MigrateOutput;
import org.flywaydb.core.api.output.MigrateResult;

public class DbMigrationHandler {

  private final DatabaseMigrator configDbMigrator;
  private final DatabaseMigrator jobDbMigrator;

  public DbMigrationHandler(Database configsDatabase, Database jobsDatabase) {
    this.configDbMigrator = new ConfigsDatabaseMigrator(configsDatabase, DbMigrationHandler.class.getSimpleName());
    this.jobDbMigrator = new JobsDatabaseMigrator(jobsDatabase, DbMigrationHandler.class.getSimpleName());
  }

  public DbMigrationReadList list(DbMigrationRequestBody request) {
    DatabaseMigrator migrator = getMigrator(request.getDatabase());
    return new DbMigrationReadList()
        .migrations(migrator.list().stream().map(DbMigrationHandler::toMigrationRead).collect(Collectors.toList()));
  }

  public DbMigrationExecutionRead migrate(DbMigrationRequestBody request) {
    DatabaseMigrator migrator = getMigrator(request.getDatabase());
    MigrateResult result = migrator.migrate();
    return new DbMigrationExecutionRead()
        .initialVersion(result.initialSchemaVersion)
        .targetVersion(result.targetSchemaVersion)
        .executedMigrations(result.migrations.stream().map(DbMigrationHandler::toMigrationRead).collect(Collectors.toList()));
  }

  private DatabaseMigrator getMigrator(String database) {
    if (database.equalsIgnoreCase("configs")) {
      return configDbMigrator;
    } else if (database.equalsIgnoreCase("jobs")) {
      return jobDbMigrator;
    }
    throw new IllegalArgumentException("Unexpected database: " + database);
  }

  private static DbMigrationRead toMigrationRead(MigrationInfo info) {
    return new DbMigrationRead()
        .migrationType(info.getType().name())
        .migrationVersion(info.getVersion().toString())
        .migrationDescription(info.getDescription())
        .migrationState(DbMigrationState.fromValue(info.getState().name()))
        .migratedBy(info.getInstalledBy())
        .migratedAt(info.getInstalledOn() == null ? null : info.getInstalledOn().getTime())
        .migrationScript(info.getScript());
  }

  private static DbMigrationRead toMigrationRead(MigrateOutput output) {
    return new DbMigrationRead()
        .migrationType(String.format("%s %s", output.type, output.category))
        .migrationVersion(output.version)
        .migrationDescription(output.description)
        .migrationScript(output.filepath);
  }

}
