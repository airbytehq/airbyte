/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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

    if (flywayOptional.isPresent()) {
      final var flyway = flywayOptional.get();
      var currDatabaseMigrationVersion = flyway.info().current().getVersion().getVersion();
      getLogger().info("Current database migration version {}.", currDatabaseMigrationVersion);
      getLogger().info("Minimum Flyway version required {}.", getMinimumFlywayVersion());

      while (currDatabaseMigrationVersion.compareTo(getMinimumFlywayVersion()) < 0) {
        if (System.currentTimeMillis() - startTime >= getTimeoutMs()) {
          throw new DatabaseCheckException("Timeout while waiting for database to fulfill minimum flyway migration version..");
        }

        try {
          Thread.sleep(sleepTime);
        } catch (final InterruptedException e) {
          throw new DatabaseCheckException("Unable to wait for database to be migrated.", e);
        }
        currDatabaseMigrationVersion = flyway.info().current().getVersion().getVersion();
      }
      getLogger().info("Verified that database has been migrated to the required minimum version {}.", getTimeoutMs());
    } else {
      throw new DatabaseCheckException("Flyway configuration not present.");
    }
  }

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
