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

package io.airbyte.db.instance;

import io.airbyte.db.Database;
import java.sql.SQLException;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;
import org.flywaydb.core.Flyway;
import org.flywaydb.core.api.MigrationInfo;
import org.flywaydb.core.api.MigrationInfoService;
import org.flywaydb.core.api.output.BaselineResult;
import org.flywaydb.core.api.output.MigrateResult;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DatabaseMigrator {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabaseMigrator.class);

  private final Database database;
  private final Flyway flyway;

  /**
   * @param dbIdentifier A name to identify the database. Preferably one word. This identifier will be
   *        used to construct the migration history table name. For example, if the identifier is
   *        "imports", the history table name will be "airbyte_imports_migrations".
   * @param migrationFileLocations Example: "classpath:db/migration". See:
   *        https://flywaydb.org/documentation/concepts/migrations#discovery-1
   */
  public DatabaseMigrator(Database database, String dbIdentifier, String migrationFileLocations) {
    this.database = database;
    this.flyway = Flyway.configure()
        .dataSource(database.getDataSource())
        .baselineVersion(MigrationConstants.BASELINE_VERSION)
        .baselineDescription(MigrationConstants.BASELINE_DESCRIPTION)
        .baselineOnMigrate(MigrationConstants.BASELINE_ON_MIGRATION)
        .installedBy(DatabaseMigrator.class.getSimpleName())
        .table(String.format("airbyte_%s_migrations", dbIdentifier))
        .locations(migrationFileLocations)
        .load();
  }

  public MigrateResult migrate() {
    MigrateResult result = flyway.migrate();
    result.warnings.forEach(LOGGER::warn);
    return result;
  }

  public List<MigrationInfo> info() {
    MigrationInfoService result = flyway.info();
    result.getInfoResult().warnings.forEach(LOGGER::warn);
    return Arrays.asList(result.all());
  }

  public BaselineResult baseline() {
    BaselineResult result = flyway.baseline();
    result.warnings.forEach(LOGGER::warn);
    return result;
  }

  public String dumpSchema() throws SQLException {
    return database.query(ctx -> ctx.meta().ddl().queryStream()
        .map(query -> query.toString() + ";")
        .filter(statement -> !statement.startsWith("create schema"))
        .collect(Collectors.joining("\n")));
  }

}
