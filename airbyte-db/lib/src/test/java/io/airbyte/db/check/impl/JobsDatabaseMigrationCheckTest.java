/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.check.impl;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.db.check.DatabaseCheckException;
import org.flywaydb.core.Flyway;
import org.flywaydb.core.api.MigrationInfo;
import org.flywaydb.core.api.MigrationInfoService;
import org.flywaydb.core.api.MigrationVersion;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link JobsDatabaseMigrationCheck} class.
 */
public class JobsDatabaseMigrationCheckTest {

  @Test
  void testMigrationCheck() {
    final var minimumVersion = "1.0.0";
    final var currentVersion = "1.2.3";
    final var migrationVersion = MigrationVersion.fromVersion(currentVersion);
    final var migrationInfo = mock(MigrationInfo.class);
    final var migrationInfoService = mock(MigrationInfoService.class);
    final var flyway = mock(Flyway.class);

    when(migrationInfo.getVersion()).thenReturn(migrationVersion);
    when(migrationInfoService.current()).thenReturn(migrationInfo);
    when(flyway.info()).thenReturn(migrationInfoService);

    final var check = new JobsDatabaseMigrationCheck(flyway, minimumVersion, AbstractDatabaseAvailabilityCheckTest.TIMEOUT_MS);
    Assertions.assertDoesNotThrow(() -> check.check());
  }

  @Test
  void testMigrationCheckEqualVersion() {
    final var minimumVersion = "1.2.3";
    final var currentVersion = minimumVersion;
    final var migrationVersion = MigrationVersion.fromVersion(currentVersion);
    final var migrationInfo = mock(MigrationInfo.class);
    final var migrationInfoService = mock(MigrationInfoService.class);
    final var flyway = mock(Flyway.class);

    when(migrationInfo.getVersion()).thenReturn(migrationVersion);
    when(migrationInfoService.current()).thenReturn(migrationInfo);
    when(flyway.info()).thenReturn(migrationInfoService);

    final var check = new JobsDatabaseMigrationCheck(flyway, minimumVersion, AbstractDatabaseAvailabilityCheckTest.TIMEOUT_MS);
    Assertions.assertDoesNotThrow(() -> check.check());
  }

  @Test
  void testMigrationCheckTimeout() {
    final var minimumVersion = "2.0.0";
    final var currentVersion = "1.2.3";
    final var migrationVersion = MigrationVersion.fromVersion(currentVersion);
    final var migrationInfo = mock(MigrationInfo.class);
    final var migrationInfoService = mock(MigrationInfoService.class);
    final var flyway = mock(Flyway.class);

    when(migrationInfo.getVersion()).thenReturn(migrationVersion);
    when(migrationInfoService.current()).thenReturn(migrationInfo);
    when(flyway.info()).thenReturn(migrationInfoService);

    final var check = new JobsDatabaseMigrationCheck(flyway, minimumVersion, AbstractDatabaseAvailabilityCheckTest.TIMEOUT_MS);
    Assertions.assertThrows(DatabaseCheckException.class, () -> check.check());
  }

  @Test
  void checkDatabaseAvailabilityNullFlyway() {
    final var minimumVersion = "2.0.0";
    final var check = new JobsDatabaseMigrationCheck(null, minimumVersion, AbstractDatabaseAvailabilityCheckTest.TIMEOUT_MS);
    Assertions.assertThrows(DatabaseCheckException.class, () -> check.check());
  }

}
