/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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
