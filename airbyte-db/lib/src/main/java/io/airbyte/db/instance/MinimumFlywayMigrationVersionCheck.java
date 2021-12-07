/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MinimumFlywayMigrationVersionCheck {

  private static final Logger LOGGER = LoggerFactory.getLogger(MinimumFlywayMigrationVersionCheck.class);
  private static final long DEFAULT_POLL_PERIOD_MS = 1000;

  public static void assertDatabase(DatabaseMigrator migrator, String minimumFlywayVersion, long timeoutMs)
      throws InterruptedException {
    var currDatabaseMigrationVersion = migrator.getLatestMigration().getVersion().getVersion();

    var currWaitingTime = 0;
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
