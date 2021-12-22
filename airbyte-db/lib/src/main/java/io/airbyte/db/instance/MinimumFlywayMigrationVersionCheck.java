/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance;

import io.airbyte.commons.lang.Exceptions;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Contains reusable methods asserting if a database is ready.
 * <p>
 * This is intended to be used by applications in combination with the bootloader, and the minimum
 * migration env vars from {@link io.airbyte.config.Configs}, so applications know it is safe to
 * start interacting with the database.
 * <p>
 * Both methods here poll every {@link #SLEEP_TIME}, which is dynamic, and have configurable
 * timeouts.
 */
public class MinimumFlywayMigrationVersionCheck {

  public static final long DEFAULT_ASSERT_DATABASE_TIMEOUT_MS = 2 * BaseDatabaseInstance.DEFAULT_CONNECTION_TIMEOUT_MS;

  private static final Logger LOGGER = LoggerFactory.getLogger(MinimumFlywayMigrationVersionCheck.class);
  private static final long NUM_POLL_TIMES = 10;
  private static final long SLEEP_TIME = DEFAULT_ASSERT_DATABASE_TIMEOUT_MS / NUM_POLL_TIMES;

  /**
   * Assert the given database can be connected to.
   *
   * @param db
   * @param timeoutMs
   */
  public static void assertDatabase(final DatabaseInstance db, final long timeoutMs) {
    final var startTime = System.currentTimeMillis();
    var initialized = false;
    while (!initialized) {
      LOGGER.info("Waiting for database...");

      if ((System.currentTimeMillis() - startTime) >= timeoutMs) {
        throw new RuntimeException("Timeout while connecting to the database..");
      }

      // Assume the DB it not ready if initialized is false, or if there is an exception.
      // Sleep between polls.
      try {
        initialized = db.isInitialized();
        if (!initialized) {
          Thread.sleep(SLEEP_TIME);
        }
      } catch (final Exception e) {
        Exceptions.toRuntime(() -> Thread.sleep(SLEEP_TIME));
      }

    }
  }

  /**
   * Assert the given database contains the minimum flyway migrations needed to run the application.
   *
   * @param migrator
   * @param minimumFlywayVersion
   * @param timeoutMs
   * @throws InterruptedException
   */
  public static void assertMigrations(final DatabaseMigrator migrator, final String minimumFlywayVersion, final long timeoutMs)
      throws InterruptedException {
    var currWaitingTime = 0;
    var currDatabaseMigrationVersion = migrator.getLatestMigration().getVersion().getVersion();
    LOGGER.info("Current database migration version " + currDatabaseMigrationVersion);
    LOGGER.info("Minimum Flyway version required " + minimumFlywayVersion);
    while (currDatabaseMigrationVersion.compareTo(minimumFlywayVersion) < 0) {
      if (currWaitingTime >= timeoutMs) {
        throw new RuntimeException("Timeout while waiting for database to fulfill minimum flyway migration version..");
      }

      Thread.sleep(SLEEP_TIME);
      currWaitingTime += SLEEP_TIME;
      currDatabaseMigrationVersion = migrator.getLatestMigration().getVersion().getVersion();
    }
  }

}
