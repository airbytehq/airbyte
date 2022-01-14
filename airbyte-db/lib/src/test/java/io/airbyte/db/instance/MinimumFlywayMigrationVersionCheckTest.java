/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.commons.lang.Exceptions;
import java.io.IOException;
import java.util.Date;
import lombok.val;
import org.flywaydb.core.api.MigrationInfo;
import org.flywaydb.core.api.MigrationState;
import org.flywaydb.core.api.MigrationType;
import org.flywaydb.core.api.MigrationVersion;
import org.junit.jupiter.api.Test;

public class MinimumFlywayMigrationVersionCheckTest {

  private static final long DEFAULT_TIMEOUT_MS = 2 * 1000;

  @Test
  void testDatabaseNotSetupFails() throws IOException {
    val database = mock(DatabaseInstance.class);
    when(database.isInitialized()).thenThrow(new IOException()).thenReturn(false);

    val startTime = System.currentTimeMillis();
    assertThrows(RuntimeException.class, () -> MinimumFlywayMigrationVersionCheck.assertDatabase(database, DEFAULT_TIMEOUT_MS));
    assertTrue(System.currentTimeMillis() - startTime >= DEFAULT_TIMEOUT_MS);
  }

  @Test
  void testDatabaseFailsPollsCorrectTimes() throws IOException {
    val database = spy(DatabaseInstance.class);
    when(database.isInitialized()).thenThrow(new IOException()).thenReturn(false);

    Exceptions.swallow(() -> MinimumFlywayMigrationVersionCheck.assertDatabase(database, DEFAULT_TIMEOUT_MS));
    verify(database, times(MinimumFlywayMigrationVersionCheck.NUM_POLL_TIMES)).isInitialized();
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
  void testMigrationMatchesMinimum() {
    val version = "0.22.0.1";
    val migrator = mock(DatabaseMigrator.class);
    when(migrator.getLatestMigration()).thenReturn(new StubMigrationInfo(version));

    assertDoesNotThrow(() -> MinimumFlywayMigrationVersionCheck.assertMigrations(migrator, version, DEFAULT_TIMEOUT_MS));
  }

  @Test
  void testMigrationExceedsMinimum() {
    val minVersion = "0.22.0.1";
    val latestVersion = "0.30.0";
    val migrator = mock(DatabaseMigrator.class);
    when(migrator.getLatestMigration()).thenReturn(new StubMigrationInfo(latestVersion));

    assertDoesNotThrow(() -> MinimumFlywayMigrationVersionCheck.assertMigrations(migrator, minVersion, DEFAULT_TIMEOUT_MS));
  }

  @Test
  void testMigrationFulfilledAfter() {
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
  void testMigrationTimeout() {
    val startVersion = "0.22.0.1";
    val minVersion = "0.30.0";

    val migrator = mock(DatabaseMigrator.class);
    when(migrator.getLatestMigration()).thenReturn(new StubMigrationInfo(startVersion));

    val startTime = System.currentTimeMillis();
    assertThrows(RuntimeException.class, () -> MinimumFlywayMigrationVersionCheck.assertMigrations(migrator, minVersion, DEFAULT_TIMEOUT_MS));
    assertTrue(System.currentTimeMillis() - startTime >= DEFAULT_TIMEOUT_MS);
  }

  @Test
  void testMigrationPollsCorrectTimes() {
    val startVersion = "0.22.0.1";
    val minVersion = "0.30.0";

    val migrator = spy(DatabaseMigrator.class);
    when(migrator.getLatestMigration()).thenReturn(new StubMigrationInfo(startVersion));

    Exceptions.swallow(() -> MinimumFlywayMigrationVersionCheck.assertMigrations(migrator, minVersion, DEFAULT_TIMEOUT_MS));
    verify(migrator, times(MinimumFlywayMigrationVersionCheck.NUM_POLL_TIMES + 1)).getLatestMigration();
  }

  /**
   * For testing purposes.
   */
  private static class StubMigrationInfo implements MigrationInfo {

    private final String version;

    public StubMigrationInfo(final String version) {
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
    public int compareVersion(final MigrationInfo o) {
      return 0;
    }

    @Override
    public int compareTo(final MigrationInfo o) {
      return 0;
    }

  }

}
