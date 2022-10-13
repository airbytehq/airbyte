/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
class JobsDatabaseMigrationCheckTest {

  private static final String CURRENT_VERSION = "1.2.3";
  private static final String VERSION_2 = "2.0.0";

  @Test
  void testMigrationCheck() {
    final var minimumVersion = "1.0.0";
    final var currentVersion = CURRENT_VERSION;
    final var migrationVersion = MigrationVersion.fromVersion(currentVersion);
    final var migrationInfo = mock(MigrationInfo.class);
    final var migrationInfoService = mock(MigrationInfoService.class);
    final var flyway = mock(Flyway.class);
    final var databaseAvailabilityCheck = mock(JobsDatabaseAvailabilityCheck.class);

    when(migrationInfo.getVersion()).thenReturn(migrationVersion);
    when(migrationInfoService.current()).thenReturn(migrationInfo);
    when(flyway.info()).thenReturn(migrationInfoService);

    final var check = new JobsDatabaseMigrationCheck(databaseAvailabilityCheck, flyway, minimumVersion, CommonDatabaseCheckTest.TIMEOUT_MS);
    Assertions.assertDoesNotThrow(() -> check.check());
  }

  @Test
  void testMigrationCheckEqualVersion() {
    final var minimumVersion = CURRENT_VERSION;
    final var currentVersion = minimumVersion;
    final var migrationVersion = MigrationVersion.fromVersion(currentVersion);
    final var migrationInfo = mock(MigrationInfo.class);
    final var migrationInfoService = mock(MigrationInfoService.class);
    final var flyway = mock(Flyway.class);
    final var databaseAvailabilityCheck = mock(JobsDatabaseAvailabilityCheck.class);

    when(migrationInfo.getVersion()).thenReturn(migrationVersion);
    when(migrationInfoService.current()).thenReturn(migrationInfo);
    when(flyway.info()).thenReturn(migrationInfoService);

    final var check = new JobsDatabaseMigrationCheck(databaseAvailabilityCheck, flyway, minimumVersion, CommonDatabaseCheckTest.TIMEOUT_MS);
    Assertions.assertDoesNotThrow(() -> check.check());
  }

  @Test
  void testMigrationCheckTimeout() {
    final var minimumVersion = VERSION_2;
    final var currentVersion = CURRENT_VERSION;
    final var migrationVersion = MigrationVersion.fromVersion(currentVersion);
    final var migrationInfo = mock(MigrationInfo.class);
    final var migrationInfoService = mock(MigrationInfoService.class);
    final var flyway = mock(Flyway.class);
    final var databaseAvailabilityCheck = mock(JobsDatabaseAvailabilityCheck.class);

    when(migrationInfo.getVersion()).thenReturn(migrationVersion);
    when(migrationInfoService.current()).thenReturn(migrationInfo);
    when(flyway.info()).thenReturn(migrationInfoService);

    final var check = new JobsDatabaseMigrationCheck(databaseAvailabilityCheck, flyway, minimumVersion, CommonDatabaseCheckTest.TIMEOUT_MS);
    Assertions.assertThrows(DatabaseCheckException.class, () -> check.check());
  }

  @Test
  void testMigrationCheckNullDatabaseAvailabilityCheck() {
    final var minimumVersion = VERSION_2;
    final var currentVersion = CURRENT_VERSION;
    final var migrationVersion = MigrationVersion.fromVersion(currentVersion);
    final var migrationInfo = mock(MigrationInfo.class);
    final var migrationInfoService = mock(MigrationInfoService.class);
    final var flyway = mock(Flyway.class);

    when(migrationInfo.getVersion()).thenReturn(migrationVersion);
    when(migrationInfoService.current()).thenReturn(migrationInfo);
    when(flyway.info()).thenReturn(migrationInfoService);

    final var check = new JobsDatabaseMigrationCheck(null, flyway, minimumVersion, CommonDatabaseCheckTest.TIMEOUT_MS);
    Assertions.assertThrows(DatabaseCheckException.class, () -> check.check());
  }

  @Test
  void testMigrationCheckNullFlyway() {
    final var minimumVersion = VERSION_2;
    final var databaseAvailabilityCheck = mock(JobsDatabaseAvailabilityCheck.class);
    final var check = new JobsDatabaseMigrationCheck(databaseAvailabilityCheck, null, minimumVersion, CommonDatabaseCheckTest.TIMEOUT_MS);
    Assertions.assertThrows(DatabaseCheckException.class, () -> check.check());
  }

  @Test
  void unavailableFlywayMigrationVersion() {
    final var minimumVersion = VERSION_2;
    final var migrationInfoService = mock(MigrationInfoService.class);
    final var flyway = mock(Flyway.class);
    final var databaseAvailabilityCheck = mock(JobsDatabaseAvailabilityCheck.class);

    when(migrationInfoService.current()).thenReturn(null);
    when(flyway.info()).thenReturn(migrationInfoService);

    final var check = new JobsDatabaseMigrationCheck(databaseAvailabilityCheck, flyway, minimumVersion, CommonDatabaseCheckTest.TIMEOUT_MS);
    Assertions.assertThrows(DatabaseCheckException.class, () -> check.check());
  }

}
