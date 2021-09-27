/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.development;

import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.commons.version.AirbyteVersion;
import java.util.Optional;
import org.flywaydb.core.api.MigrationVersion;
import org.junit.jupiter.api.Test;

class MigrationDevHelperTest {

  @Test
  public void testGetCurrentAirbyteVersion() {
    // Test that this method will not throw any exception.
    MigrationDevHelper.getCurrentAirbyteVersion();
  }

  @Test
  public void testGetAirbyteVersion() {
    MigrationVersion migrationVersion = MigrationVersion.fromVersion("0.11.3.010");
    AirbyteVersion airbyteVersion = MigrationDevHelper.getAirbyteVersion(migrationVersion);
    assertEquals("0.11.3", airbyteVersion.getVersion());
  }

  @Test
  public void testFormatAirbyteVersion() {
    AirbyteVersion airbyteVersion = new AirbyteVersion("0.11.3-alpha");
    assertEquals("0_11_3", MigrationDevHelper.formatAirbyteVersion(airbyteVersion));
  }

  @Test
  public void testGetMigrationId() {
    MigrationVersion migrationVersion = MigrationVersion.fromVersion("0.11.3.010");
    assertEquals("010", MigrationDevHelper.getMigrationId(migrationVersion));
  }

  @Test
  public void testGetNextMigrationVersion() {
    // Migration version does not exist
    assertEquals("0.11.3.001", MigrationDevHelper.getNextMigrationVersion(
        new AirbyteVersion("0.11.3-alpha"),
        Optional.empty()).getVersion());

    // Airbyte version is greater
    assertEquals("0.11.3.001", MigrationDevHelper.getNextMigrationVersion(
        new AirbyteVersion("0.11.3-alpha"),
        Optional.of(MigrationVersion.fromVersion("0.10.9.003"))).getVersion());

    // Airbyte version is equal to migration version
    assertEquals("0.11.3.004", MigrationDevHelper.getNextMigrationVersion(
        new AirbyteVersion("0.11.3-alpha"),
        Optional.of(MigrationVersion.fromVersion("0.11.3.003"))).getVersion());

    // Migration version is greater
    assertEquals("0.11.3.004", MigrationDevHelper.getNextMigrationVersion(
        new AirbyteVersion("0.9.17-alpha"),
        Optional.of(MigrationVersion.fromVersion("0.11.3.003"))).getVersion());
  }

}
