/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.version;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class AirbyteVersionTest {

  @Test
  void testParseVersion() {
    final AirbyteVersion version = new AirbyteVersion("6.7.8");
    assertEquals("6", version.getMajorVersion());
    assertEquals("7", version.getMinorVersion());
    assertEquals("8", version.getPatchVersion());
  }

  @Test
  void testParseVersionWithLabel() {
    final AirbyteVersion version = new AirbyteVersion("6.7.8-omega");
    assertEquals("6", version.getMajorVersion());
    assertEquals("7", version.getMinorVersion());
    assertEquals("8", version.getPatchVersion());
  }

  @Test
  void testCompatibleVersionCompareTo() {
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
  void testPatchVersionCompareTo() {
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
  void testGreaterThan() {
    assertFalse(new AirbyteVersion("6.7.8-omega").greaterThan(new AirbyteVersion("6.7.8-gamma")));
    assertFalse(new AirbyteVersion("6.7.8-alpha").greaterThan(new AirbyteVersion("6.7.9-alpha")));
    assertFalse(new AirbyteVersion("6.7.8-alpha").greaterThan(new AirbyteVersion("6.7.11-alpha")));
    assertTrue(new AirbyteVersion("6.8.0-alpha").greaterThan(new AirbyteVersion("6.7.8-alpha")));
    assertTrue(new AirbyteVersion("6.11.0-alpha").greaterThan(new AirbyteVersion("6.7.8-alpha")));
    assertFalse(new AirbyteVersion("3.8.0-alpha").greaterThan(new AirbyteVersion("6.7.8-alpha")));
    assertFalse(new AirbyteVersion("3.8.0-alpha").greaterThan(new AirbyteVersion("11.7.8-alpha")));
    assertFalse(new AirbyteVersion("1.2.3-prod").greaterThan(new AirbyteVersion("dev")));
    assertFalse(new AirbyteVersion("dev").greaterThan(new AirbyteVersion("1.2.3-prod")));
  }

  @Test
  void testLessThan() {
    assertFalse(new AirbyteVersion("6.7.8-omega").lessThan(new AirbyteVersion("6.7.8-gamma")));
    assertTrue(new AirbyteVersion("6.7.8-alpha").lessThan(new AirbyteVersion("6.7.9-alpha")));
    assertTrue(new AirbyteVersion("6.7.8-alpha").lessThan(new AirbyteVersion("6.7.11-alpha")));
    assertFalse(new AirbyteVersion("6.8.0-alpha").lessThan(new AirbyteVersion("6.7.8-alpha")));
    assertFalse(new AirbyteVersion("6.11.0-alpha").lessThan(new AirbyteVersion("6.7.8-alpha")));
    assertTrue(new AirbyteVersion("3.8.0-alpha").lessThan(new AirbyteVersion("6.7.8-alpha")));
    assertTrue(new AirbyteVersion("3.8.0-alpha").lessThan(new AirbyteVersion("11.7.8-alpha")));
    assertFalse(new AirbyteVersion("1.2.3-prod").lessThan(new AirbyteVersion("dev")));
    assertFalse(new AirbyteVersion("dev").lessThan(new AirbyteVersion("1.2.3-prod")));
  }

  @Test
  void testInvalidVersions() {
    assertThrows(NullPointerException.class, () -> new AirbyteVersion(null));
    assertThrows(IllegalArgumentException.class, () -> new AirbyteVersion("0.6"));
  }

  @Test
  void testSerialize() {
    final var devVersion = "dev";
    assertEquals(devVersion, new AirbyteVersion(devVersion).serialize());

    final var nonDevVersion = "0.1.2-alpha";
    assertEquals(nonDevVersion, new AirbyteVersion(nonDevVersion).serialize());
  }

  @Test
  void testCheckVersion() {
    AirbyteVersion.assertIsCompatible(new AirbyteVersion("3.2.1"), new AirbyteVersion("3.2.1"));
    assertThrows(IllegalStateException.class, () -> AirbyteVersion.assertIsCompatible(new AirbyteVersion("1.2.3"), new AirbyteVersion("3.2.1")));
  }

  @Test
  void testCheckOnlyPatchVersion() {
    assertFalse(new AirbyteVersion("6.7.8").checkOnlyPatchVersionIsUpdatedComparedTo(new AirbyteVersion("6.7.8")));
    assertFalse(new AirbyteVersion("6.9.8").checkOnlyPatchVersionIsUpdatedComparedTo(new AirbyteVersion("6.8.9")));
    assertFalse(new AirbyteVersion("7.7.8").checkOnlyPatchVersionIsUpdatedComparedTo(new AirbyteVersion("6.7.11")));
    assertTrue(new AirbyteVersion("6.7.9").checkOnlyPatchVersionIsUpdatedComparedTo(new AirbyteVersion("6.7.8")));
  }

}
