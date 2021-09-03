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

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.db.Database;
import io.airbyte.db.ExceptionWrappingDatabase;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;
import org.flywaydb.core.Flyway;
import org.flywaydb.core.api.MigrationInfo;
import org.flywaydb.core.api.MigrationInfoService;
import org.flywaydb.core.api.configuration.FluentConfiguration;
import org.flywaydb.core.api.output.BaselineResult;
import org.flywaydb.core.api.output.MigrateResult;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class FlywayDatabaseMigrator implements DatabaseMigrator {

  private static final Logger LOGGER = LoggerFactory.getLogger(FlywayDatabaseMigrator.class);
  // Constants for Flyway baseline. See here for details:
  // https://flywaydb.org/documentation/command/baseline
  private static final String BASELINE_VERSION = "0.29.0.001";
  private static final String BASELINE_DESCRIPTION = "Baseline from file-based migration v1";
  private static final boolean BASELINE_ON_MIGRATION = true;

  private final Database database;
  private final Flyway flyway;

  /**
   * @param dbIdentifier A name to identify the database. Preferably one word. This identifier will be
   *        used to construct the migration history table name. For example, if the identifier is
   *        "imports", the history table name will be "airbyte_imports_migrations".
   * @param migrationFileLocations Example: "classpath:db/migration". See:
   *        https://flywaydb.org/documentation/concepts/migrations#discovery-1
   */
  protected FlywayDatabaseMigrator(Database database,
                                   String dbIdentifier,
                                   String migrationRunner,
                                   String migrationFileLocations) {
    this(database, getConfiguration(database, dbIdentifier, migrationRunner, migrationFileLocations).load());
  }

  @VisibleForTesting
  public FlywayDatabaseMigrator(Database database, Flyway flyway) {
    this.database = database;
    this.flyway = flyway;
  }

  private static String getDefaultMigrationFileLocation(String dbIdentifier) {
    return String.format("classpath:io/airbyte/db/instance/%s/migrations", dbIdentifier);
  }

  private static FluentConfiguration getConfiguration(Database database,
                                                      String dbIdentifier,
                                                      String migrationRunner,
                                                      String migrationFileLocations) {
    return Flyway.configure()
        .dataSource(database.getDataSource())
        .baselineVersion(BASELINE_VERSION)
        .baselineDescription(BASELINE_DESCRIPTION)
        .baselineOnMigrate(BASELINE_ON_MIGRATION)
        .installedBy(migrationRunner)
        .table(String.format("airbyte_%s_migrations", dbIdentifier))
        .locations(migrationFileLocations);
  }

  @Override
  public MigrateResult migrate() {
    MigrateResult result = flyway.migrate();
    result.warnings.forEach(LOGGER::warn);
    return result;
  }

  @Override
  public List<MigrationInfo> list() {
    MigrationInfoService result = flyway.info();
    result.getInfoResult().warnings.forEach(LOGGER::warn);
    return Arrays.asList(result.all());
  }

  @Override
  public BaselineResult createBaseline() {
    BaselineResult result = flyway.baseline();
    result.warnings.forEach(LOGGER::warn);
    return result;
  }

  @Override
  public String dumpSchema() throws IOException {
    return new ExceptionWrappingDatabase(database).query(ctx -> ctx.meta().ddl().queryStream()
        .map(query -> query.toString() + ";")
        .filter(statement -> !statement.startsWith("create schema"))
        .collect(Collectors.joining("\n")));
  }

  @VisibleForTesting
  public Database getDatabase() {
    return database;
  }

  @VisibleForTesting
  public Flyway getFlyway() {
    return flyway;
  }

}
