/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.version;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

public class TestAirbyteVersion {

  @Test
  public void testParseVersion() {
    final AirbyteVersion version = new AirbyteVersion("6.7.8");
    assertEquals("6", version.getMajorVersion());
    assertEquals("7", version.getMinorVersion());
    assertEquals("8", version.getPatchVersion());
  }

  @Test
  public void testParseVersionWithLabel() {
    final AirbyteVersion version = new AirbyteVersion("6.7.8-omega");
    assertEquals("6", version.getMajorVersion());
    assertEquals("7", version.getMinorVersion());
    assertEquals("8", version.getPatchVersion());
  }

  @Test
  public void testCompatibleVersionCompareTo() {
    assertEquals(0, new AirbyteVersion("6.7.8-omega").compatibleVersionCompareTo(new AirbyteVersion("6.7.8-gamma")));
    assertEquals(0, new AirbyteVersion("6.7.8-alpha").compatibleVersionCompareTo(new AirbyteVersion("6.7.9-alpha")));
    assertTrue(0 < new AirbyteVersion("6.8.0-alpha").compatibleVersionCompareTo(new AirbyteVersion("6.7.8-alpha")));
    assertTrue(0 < new AirbyteVersion("11.8.0-alpha").compatibleVersionCompareTo(new AirbyteVersion("6.7.8-alpha")));
    assertTrue(0 < new AirbyteVersion("6.11.0-alpha").compatibleVersionCompareTo(new AirbyteVersion("6.7.8-alpha")));
    assertTrue(0 > new AirbyteVersion("0.8.0-alpha").compatibleVersionCompareTo(new AirbyteVersion("6.7.8-alpha")));
    assertEquals(0, new AirbyteVersion("1.2.3-prod").compatibleVersionCompareTo(new AirbyteVersion("dev")));
    assertEquals(0, new AirbyteVersion("dev").compatibleVersionCompareTo(new AirbyteVersion("1.2.3-prod")));
  }

  @Test
  public void testPatchVersionCompareTo() {
    assertEquals(0, new AirbyteVersion("6.7.8-omega").patchVersionCompareTo(new AirbyteVersion("6.7.8-gamma")));
    assertTrue(0 > new AirbyteVersion("6.7.8-alpha").patchVersionCompareTo(new AirbyteVersion("6.7.9-alpha")));
    assertTrue(0 > new AirbyteVersion("6.7.8-alpha").patchVersionCompareTo(new AirbyteVersion("6.7.11-alpha")));
    assertTrue(0 < new AirbyteVersion("6.8.0-alpha").patchVersionCompareTo(new AirbyteVersion("6.7.8-alpha")));
    assertTrue(0 < new AirbyteVersion("6.11.0-alpha").patchVersionCompareTo(new AirbyteVersion("6.7.8-alpha")));
    assertTrue(0 > new AirbyteVersion("3.8.0-alpha").patchVersionCompareTo(new AirbyteVersion("6.7.8-alpha")));
    assertTrue(0 > new AirbyteVersion("3.8.0-alpha").patchVersionCompareTo(new AirbyteVersion("11.7.8-alpha")));
    assertEquals(0, new AirbyteVersion("1.2.3-prod").patchVersionCompareTo(new AirbyteVersion("dev")));
    assertEquals(0, new AirbyteVersion("dev").patchVersionCompareTo(new AirbyteVersion("1.2.3-prod")));
  }

  @Test
  public void testInvalidVersions() {
    assertThrows(NullPointerException.class, () -> new AirbyteVersion(null));
    assertThrows(IllegalArgumentException.class, () -> new AirbyteVersion("0.6"));
  }

  @Test
  public void testCheckVersion() {
    AirbyteVersion.assertIsCompatible("3.2.1", "3.2.1");
    assertThrows(IllegalStateException.class, () -> AirbyteVersion.assertIsCompatible("1.2.3", "3.2.1"));
  }

}
