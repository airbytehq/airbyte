/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.factory;

import io.airbyte.db.check.DatabaseAvailabilityCheck;
import io.airbyte.db.check.DatabaseMigrationCheck;
import io.airbyte.db.check.impl.ConfigsDatabaseAvailabilityCheck;
import io.airbyte.db.check.impl.ConfigsDatabaseMigrationCheck;
import io.airbyte.db.check.impl.JobsDatabaseAvailabilityCheck;
import io.airbyte.db.check.impl.JobsDatabaseMigrationCheck;
import io.airbyte.db.init.DatabaseInitializer;
import io.airbyte.db.init.impl.ConfigsDatabaseInitializer;
import io.airbyte.db.init.impl.JobsDatabaseInitializer;
import org.flywaydb.core.Flyway;
import org.jooq.DSLContext;

/**
 * Temporary factory class that provides convenience methods for creating a
 * {@link io.airbyte.db.check.DatabaseCheck} and {@link DatabaseInitializer} instances. This class
 * will be removed once the project has been converted to leverage an application framework to
 * manage the creation and injection of various check objects.
 */
public class DatabaseCheckFactory {

  /**
   * Constructs a new {@link DatabaseAvailabilityCheck} that verifies the availability of the
   * {@code Configurations} database.
   *
   * @param dslContext The {@link DSLContext} instance used to communicate with the
   *        {@code Configurations} database.
   * @param timeoutMs The amount of time to wait for the database to become available, in
   *        milliseconds.
   * @return A configured {@link DatabaseAvailabilityCheck} for the {@code Configurations} database.
   */
  public static ConfigsDatabaseAvailabilityCheck createConfigsDatabaseAvailabilityCheck(final DSLContext dslContext, final long timeoutMs) {
    return new ConfigsDatabaseAvailabilityCheck(dslContext, timeoutMs);
  }

  /**
   * Constructs a new {@link DatabaseAvailabilityCheck} that verifies the availability of the
   * {@code Jobs} database.
   *
   * @param dslContext The {@link DSLContext} instance used to communicate with the {@code Jobs}
   *        database.
   * @param timeoutMs The amount of time to wait for the database to become available, in
   *        milliseconds.
   * @return A configured {@link DatabaseAvailabilityCheck} for the {@code Jobs} database.
   */
  public static JobsDatabaseAvailabilityCheck createJobsDatabaseAvailabilityCheck(final DSLContext dslContext, final long timeoutMs) {
    return new JobsDatabaseAvailabilityCheck(dslContext, timeoutMs);
  }

  /**
   * Constructs a new {@link DatabaseMigrationCheck} that verifies that the {@code Configurations}
   * database has been migrated to the requested minimum schema version.
   *
   * @param dslContext The {@link DSLContext} instance used to communicate with the
   *        {@code Configurations} database.
   * @param flyway The {@link Flyway} instance used to determine the current migration status.
   * @param minimumMigrationVersion The required minimum schema version.
   * @param timeoutMs Teh amount of time to wait for the migration to complete/match the requested
   *        minimum schema version, in milliseconds.
   * @return The configured {@link DatabaseMigrationCheck} for the {@code Configurations} database.
   */
  public static DatabaseMigrationCheck createConfigsDatabaseMigrationCheck(final DSLContext dslContext,
                                                                           final Flyway flyway,
                                                                           final String minimumMigrationVersion,
                                                                           final long timeoutMs) {
    return new ConfigsDatabaseMigrationCheck(createConfigsDatabaseAvailabilityCheck(dslContext, timeoutMs),
        flyway, minimumMigrationVersion, timeoutMs);
  }

  /**
   * Constructs a new {@link DatabaseMigrationCheck} that verifies that the {@code Jobs} database has
   * been migrated to the requested minimum schema version.
   *
   * @param dslContext The {@link DSLContext} instance used to communicate with the
   *        {@code Configurations} database.
   * @param flyway The {@link Flyway} instance used to determine the current migration status.
   * @param minimumMigrationVersion The required minimum schema version.
   * @param timeoutMs Teh amount of time to wait for the migration to complete/match the requested
   *        minimum schema version, in milliseconds.
   * @return The configured {@link DatabaseMigrationCheck} for the {@code Jobs} database.
   */
  public static DatabaseMigrationCheck createJobsDatabaseMigrationCheck(final DSLContext dslContext,
                                                                        final Flyway flyway,
                                                                        final String minimumMigrationVersion,
                                                                        final long timeoutMs) {
    return new JobsDatabaseMigrationCheck(createJobsDatabaseAvailabilityCheck(dslContext, timeoutMs), flyway, minimumMigrationVersion, timeoutMs);
  }

  /**
   * Constructs a new {@link DatabaseInitializer} that ensures that the {@code Configurations}
   * database schema has been initialized.
   *
   * @param dslContext The {@link DSLContext} instance used to communicate with the
   *        {@code Configurations} database.
   * @param timeoutMs The amount of time to wait for the database to become available, in
   *        milliseconds.
   * @param initialSchema The initial schema creation script to be executed if the database is not
   *        already populated.
   * @return The configured {@link DatabaseInitializer} for the {@code Configurations} database.
   */
  public static DatabaseInitializer createConfigsDatabaseInitializer(final DSLContext dslContext, final long timeoutMs, final String initialSchema) {
    return new ConfigsDatabaseInitializer(createConfigsDatabaseAvailabilityCheck(dslContext, timeoutMs), dslContext, initialSchema);
  }

  /**
   * Constructs a new {@link DatabaseInitializer} that ensures that the {@code Jobs} database schema
   * has been initialized.
   *
   * @param dslContext The {@link DSLContext} instance used to communicate with the {@code Jobs}
   *        database.
   * @param timeoutMs The amount of time to wait for the database to become available, in
   *        milliseconds.
   * @param initialSchema The initial schema creation script to be executed if the database is not
   *        already populated.
   * @return The configured {@link DatabaseInitializer} for the {@code Jobs} database.
   */
  public static DatabaseInitializer createJobsDatabaseInitializer(final DSLContext dslContext, final long timeoutMs, final String initialSchema) {
    return new JobsDatabaseInitializer(createJobsDatabaseAvailabilityCheck(dslContext, timeoutMs), dslContext, initialSchema);
  }

}
