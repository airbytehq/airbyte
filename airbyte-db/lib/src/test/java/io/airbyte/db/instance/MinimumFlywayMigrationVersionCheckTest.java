/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import java.io.IOException;
import java.util.Date;
import lombok.val;
import org.flywaydb.core.api.MigrationInfo;
import org.flywaydb.core.api.MigrationState;
import org.flywaydb.core.api.MigrationType;
import org.flywaydb.core.api.MigrationVersion;
import org.junit.jupiter.api.Test;

public class MinimumFlywayMigrationVersionCheckTest {

  private static final long DEFAULT_TIMEOUT_MS = 10 * 1000;

  @Test
  void testDatabaseNotSetupFails() throws IOException {
    val database = mock(DatabaseInstance.class);
    when(database.isInitialized()).thenThrow(new IOException()).thenReturn(false);

    assertThrows(RuntimeException.class, () -> MinimumFlywayMigrationVersionCheck.assertDatabase(database, DEFAULT_TIMEOUT_MS));
  }

  @Test
  void testDatabaseSetupSucceeds() throws IOException {
    val database = mock(DatabaseInstance.class);
    when(database.isInitialized())
        .thenReturn(false)
        .thenReturn(false)
        .thenReturn(true);

    assertDoesNotThrow(() -> MinimumFlywayMigrationVersionCheck.assertDatabase(database, DEFAULT_TIMEOUT_MS));
  }

  @Test
  void testMatchesMinimum() {
    val version = "0.22.0.1";
    val migrator = mock(DatabaseMigrator.class);
    when(migrator.getLatestMigration()).thenReturn(new StubMigrationInfo(version));

    assertDoesNotThrow(() -> MinimumFlywayMigrationVersionCheck.assertMigrations(migrator, version, DEFAULT_TIMEOUT_MS));
  }

  @Test
  void testExceedsMinimum() {
    val minVersion = "0.22.0.1";
    val latestVersion = "0.30.0";
    val migrator = mock(DatabaseMigrator.class);
    when(migrator.getLatestMigration()).thenReturn(new StubMigrationInfo(latestVersion));

    assertDoesNotThrow(() -> MinimumFlywayMigrationVersionCheck.assertMigrations(migrator, minVersion, DEFAULT_TIMEOUT_MS));
  }

  @Test
  void testFulfilledAfter() {
    val startVersion = "0.22.0.1";
    val minVersion = "0.30.0";
    val latestVersion = "0.33.0.1";

    val migrator = mock(DatabaseMigrator.class);
    when(migrator.getLatestMigration())
        .thenReturn(new StubMigrationInfo(startVersion))
        .thenReturn(new StubMigrationInfo(startVersion))
        .thenReturn(new StubMigrationInfo(startVersion))
        .thenReturn(new StubMigrationInfo(latestVersion));

    assertDoesNotThrow(() -> MinimumFlywayMigrationVersionCheck.assertMigrations(migrator, minVersion, DEFAULT_TIMEOUT_MS));
  }

  @Test
  void testTimeout() {
    val startVersion = "0.22.0.1";
    val minVersion = "0.30.0";

    val migrator = mock(DatabaseMigrator.class);
    when(migrator.getLatestMigration()).thenReturn(new StubMigrationInfo(startVersion));

    assertThrows(RuntimeException.class, () -> MinimumFlywayMigrationVersionCheck.assertMigrations(migrator, minVersion, DEFAULT_TIMEOUT_MS));
  }

  /**
   * For testing purposes.
   */
  private static class StubMigrationInfo implements MigrationInfo {

    private final String version;

    public StubMigrationInfo(String version) {
      this.version = version;
    }

    @Override
    public MigrationType getType() {
      return null;
    }

    @Override
    public Integer getChecksum() {
      return null;
    }

    @Override
    public MigrationVersion getVersion() {
      return MigrationVersion.fromVersion(version);
    }

    @Override
    public String getDescription() {
      return null;
    }

    @Override
    public String getScript() {
      return null;
    }

    @Override
    public MigrationState getState() {
      return null;
    }

    @Override
    public Date getInstalledOn() {
      return null;
    }

    @Override
    public String getInstalledBy() {
      return null;
    }

    @Override
    public Integer getInstalledRank() {
      return null;
    }

    @Override
    public Integer getExecutionTime() {
      return null;
    }

    @Override
    public String getPhysicalLocation() {
      return null;
    }

    @Override
    public int compareVersion(MigrationInfo o) {
      return 0;
    }

    @Override
    public int compareTo(MigrationInfo o) {
      return 0;
    }

  }

}
