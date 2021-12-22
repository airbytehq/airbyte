/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
  protected FlywayDatabaseMigrator(final Database database,
                                   final String dbIdentifier,
                                   final String migrationRunner,
                                   final String migrationFileLocations) {
    this(database, getConfiguration(database, dbIdentifier, migrationRunner, migrationFileLocations).load());
  }

  @VisibleForTesting
  public FlywayDatabaseMigrator(final Database database, final Flyway flyway) {
    this.database = database;
    this.flyway = flyway;
  }

  private static FluentConfiguration getConfiguration(final Database database,
                                                      final String dbIdentifier,
                                                      final String migrationRunner,
                                                      final String migrationFileLocations) {
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
    final MigrateResult result = flyway.migrate();
    result.warnings.forEach(LOGGER::warn);
    return result;
  }

  @Override
  public List<MigrationInfo> list() {
    final MigrationInfoService result = flyway.info();
    result.getInfoResult().warnings.forEach(LOGGER::warn);
    return Arrays.asList(result.all());
  }

  @Override
  public MigrationInfo getLatestMigration() {
    return flyway.info().current();
  }

  @Override
  public BaselineResult createBaseline() {
    final BaselineResult result = flyway.baseline();
    result.warnings.forEach(LOGGER::warn);
    return result;
  }

  @Override
  public String dumpSchema() throws IOException {
    return getDisclaimer() + new ExceptionWrappingDatabase(database).query(ctx -> ctx.meta().ddl().queryStream()
        .map(query -> query.toString() + ";")
        .filter(statement -> !statement.startsWith("create schema"))
        .collect(Collectors.joining("\n")));
  }

  protected String getDisclaimer() {
    return """
           // The content of the file is just to have a basic idea of the current state of the database and is not fully accurate.\040
           // It is also not used by any piece of code to generate anything.\040
           // It doesn't contain the enums created in the database and the default values might also be buggy.\s
           """ + '\n';
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
