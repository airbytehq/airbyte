/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.check;

import java.util.Optional;
import org.flywaydb.core.Flyway;
import org.slf4j.Logger;

/**
 * Performs a check to verify that the configured database has been migrated to the appropriate
 * version.
 */
public interface DatabaseMigrationCheck {

  /**
   * The number of times to check if the database has been migrated to the required schema version.
   * TODO replace with a default value in a value injection annotation
   */
  int NUM_POLL_TIMES = 10;

  /**
   * Checks whether the configured database has been migrated to the required minimum schema version.
   *
   * @throws DatabaseCheckException if unable to perform the check.
   */
  default void check() throws DatabaseCheckException {
    final var startTime = System.currentTimeMillis();
    final var sleepTime = getTimeoutMs() / NUM_POLL_TIMES;
    final Optional<Flyway> flywayOptional = getFlyway();

    // Verify that the database is up and reachable first
    final Optional<DatabaseAvailabilityCheck> availabilityCheck = getDatabaseAvailabilityCheck();
    if (availabilityCheck.isPresent()) {
      availabilityCheck.get().check();
      if (flywayOptional.isPresent()) {
        final var flyway = flywayOptional.get();

        /**
         * The database may be available, but not yet migrated. If this is the case, the Flyway object will
         * not be able to retrieve the current version of the schema. Therefore, wait for the migration to
         * complete before moving on with the test.
         */
        while (flyway.info().current() == null) {
          getLogger().info("Waiting for migration to complete...");
          sleep(sleepTime);
        }

        var currDatabaseMigrationVersion = flyway.info().current().getVersion().getVersion();
        getLogger().info("Current database migration version {}.", currDatabaseMigrationVersion);
        getLogger().info("Minimum Flyway version required {}.", getMinimumFlywayVersion());

        while (currDatabaseMigrationVersion.compareTo(getMinimumFlywayVersion()) < 0) {
          if (System.currentTimeMillis() - startTime >= getTimeoutMs()) {
            throw new DatabaseCheckException("Timeout while waiting for database to fulfill minimum flyway migration version..");
          }
          sleep(sleepTime);
          currDatabaseMigrationVersion = flyway.info().current().getVersion().getVersion();
        }
        getLogger().info("Verified that database has been migrated to the required minimum version {}.", getTimeoutMs());
      } else {
        throw new DatabaseCheckException("Flyway configuration not present.");
      }
    } else {
      throw new DatabaseCheckException("Availability check not configured.");
    }
  }

  /**
   * Sleep for the provided amount of time (in milliseconds).
   *
   * @param sleepTime The amount of time to sleep
   * @throws DatabaseCheckException if unable to sleep for the required amount of time.
   */
  default void sleep(final long sleepTime) throws DatabaseCheckException {
    try {
      Thread.sleep(sleepTime);
    } catch (final InterruptedException e) {
      throw new DatabaseCheckException("Unable to wait for database to be migrated.", e);
    }
  }

  /**
   * Retrieves the {@link DatabaseAvailabilityCheck} used to verify that the database is running and
   * available.
   *
   * @return The {@link DatabaseAvailabilityCheck}.
   */
  Optional<DatabaseAvailabilityCheck> getDatabaseAvailabilityCheck();

  /**
   * Retrieves the configured {@link Flyway} object to be used to check the migration status of the
   * database.
   *
   * @return The configured {@link Flyway} object.
   */
  Optional<Flyway> getFlyway();

  /**
   * Retrieves the configured {@link Logger} object to be used to record progress of the migration
   * check.
   *
   * @return The configured {@link Logger} object.
   */
  Logger getLogger();

  /**
   * Retrieves the required minimum migration version of the schema.
   *
   * @return The required minimum migration version of the schema.
   */
  String getMinimumFlywayVersion();

  /**
   * Retrieves the timeout in milliseconds for the check. Once this timeout is exceeded, the check
   * will fail with an {@link InterruptedException}.
   *
   * @return The timeout in milliseconds for the check.
   */
  long getTimeoutMs();

}
