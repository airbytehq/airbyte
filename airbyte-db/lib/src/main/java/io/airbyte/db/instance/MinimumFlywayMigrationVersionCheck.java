/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance;

import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Contains reusable methods asserting if a database is ready.
 * <p>
 * This is intended to be used by applications in combination with the bootloader, and the minimum
 * migration env vars from {@link io.airbyte.config.Configs}, so application know it is safe to
 * start interacting with the database.
 * <p>
 * Both methods here poll every {@link #DEFAULT_POLL_PERIOD_MS} and have configurable timeouts.
 */
public class MinimumFlywayMigrationVersionCheck {

  public static final long DEFAULT_ASSERT_DATABASE_TIMEOUT_MS = 2 * BaseDatabaseInstance.DEFAULT_CONNECTION_TIMEOUT_MS;

  private static final Logger LOGGER = LoggerFactory.getLogger(MinimumFlywayMigrationVersionCheck.class);
  private static final long DEFAULT_POLL_PERIOD_MS = 2000;

  /**
   * Assert the given database can be connected to.
   *
   * @param db
   * @param timeoutMs
   */
  public static void assertDatabase(DatabaseInstance db, long timeoutMs) {
    var currWaitingTime = 0;
    var initialized = false;
    while (!initialized) {
      if (currWaitingTime >= timeoutMs) {
        throw new RuntimeException("Timeout while connecting to the database..");
      }

      try {
        initialized = db.isInitialized();
      } catch (IOException e) {
        currWaitingTime += BaseDatabaseInstance.DEFAULT_CONNECTION_TIMEOUT_MS;
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
  public static void assertMigrations(DatabaseMigrator migrator, String minimumFlywayVersion, long timeoutMs) throws InterruptedException {
    var currWaitingTime = 0;
    var currDatabaseMigrationVersion = migrator.getLatestMigration().getVersion().getVersion();

    while (currDatabaseMigrationVersion.compareTo(minimumFlywayVersion) < 0) {
      if (currWaitingTime >= timeoutMs) {
        throw new RuntimeException("Timeout while waiting for database to fulfill minimum flyway migration version..");
      }

      Thread.sleep(DEFAULT_POLL_PERIOD_MS);
      currWaitingTime += DEFAULT_POLL_PERIOD_MS;
      currDatabaseMigrationVersion = migrator.getLatestMigration().getVersion().getVersion();
    }
  }

}
