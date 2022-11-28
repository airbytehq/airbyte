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

  private static final String VERSION_678 = "6.7.8";
  private static final String VERSION_678_OMEGA = "6.7.8-omega";
  private static final String VERSION_678_ALPHA = "6.7.8-alpha";
  private static final String VERSION_678_GAMMA = "6.7.8-gamma";
  private static final String VERSION_679_ALPHA = "6.7.9-alpha";
  private static final String VERSION_680_ALPHA = "6.8.0-alpha";
  private static final String VERSION_6110_ALPHA = "6.11.0-alpha";
  private static final String VERSION_123_PROD = "1.2.3-prod";
  private static final String DEV = "dev";
  private static final String VERSION_380_ALPHA = "3.8.0-alpha";

  @Test
  void testParseVersion() {
    final AirbyteVersion version = new AirbyteVersion(VERSION_678);
    assertEquals("6", version.getMajorVersion());
    assertEquals("7", version.getMinorVersion());
    assertEquals("8", version.getPatchVersion());
  }

  @Test
  void testParseVersionWithLabel() {
    final AirbyteVersion version = new AirbyteVersion(VERSION_678_OMEGA);
    assertEquals("6", version.getMajorVersion());
    assertEquals("7", version.getMinorVersion());
    assertEquals("8", version.getPatchVersion());
  }

  @Test
  void testCompatibleVersionCompareTo() {
    assertEquals(0, new AirbyteVersion(VERSION_678_OMEGA).compatibleVersionCompareTo(new AirbyteVersion(VERSION_678_GAMMA)));
    assertEquals(0, new AirbyteVersion(VERSION_678_ALPHA).compatibleVersionCompareTo(new AirbyteVersion(VERSION_679_ALPHA)));
    assertTrue(0 < new AirbyteVersion(VERSION_680_ALPHA).compatibleVersionCompareTo(new AirbyteVersion(VERSION_678_ALPHA)));
    assertTrue(0 < new AirbyteVersion("11.8.0-alpha").compatibleVersionCompareTo(new AirbyteVersion(VERSION_678_ALPHA)));
    assertTrue(0 < new AirbyteVersion(VERSION_6110_ALPHA).compatibleVersionCompareTo(new AirbyteVersion(VERSION_678_ALPHA)));
    assertTrue(0 > new AirbyteVersion("0.8.0-alpha").compatibleVersionCompareTo(new AirbyteVersion(VERSION_678_ALPHA)));
    assertEquals(0, new AirbyteVersion(VERSION_123_PROD).compatibleVersionCompareTo(new AirbyteVersion(DEV)));
    assertEquals(0, new AirbyteVersion(DEV).compatibleVersionCompareTo(new AirbyteVersion(VERSION_123_PROD)));
  }

  @Test
  void testPatchVersionCompareTo() {
    assertEquals(0, new AirbyteVersion(VERSION_678_OMEGA).patchVersionCompareTo(new AirbyteVersion(VERSION_678_GAMMA)));
    assertTrue(0 > new AirbyteVersion(VERSION_678_ALPHA).patchVersionCompareTo(new AirbyteVersion(VERSION_679_ALPHA)));
    assertTrue(0 > new AirbyteVersion(VERSION_678_ALPHA).patchVersionCompareTo(new AirbyteVersion("6.7.11-alpha")));
    assertTrue(0 < new AirbyteVersion(VERSION_680_ALPHA).patchVersionCompareTo(new AirbyteVersion(VERSION_678_ALPHA)));
    assertTrue(0 < new AirbyteVersion(VERSION_6110_ALPHA).patchVersionCompareTo(new AirbyteVersion(VERSION_678_ALPHA)));
    assertTrue(0 > new AirbyteVersion(VERSION_380_ALPHA).patchVersionCompareTo(new AirbyteVersion(VERSION_678_ALPHA)));
    assertTrue(0 > new AirbyteVersion(VERSION_380_ALPHA).patchVersionCompareTo(new AirbyteVersion("11.7.8-alpha")));
    assertEquals(0, new AirbyteVersion(VERSION_123_PROD).patchVersionCompareTo(new AirbyteVersion(DEV)));
    assertEquals(0, new AirbyteVersion(DEV).patchVersionCompareTo(new AirbyteVersion(VERSION_123_PROD)));
  }

  @Test
  void testGreaterThan() {
    assertFalse(new AirbyteVersion(VERSION_678_OMEGA).greaterThan(new AirbyteVersion(VERSION_678_GAMMA)));
    assertFalse(new AirbyteVersion(VERSION_678_ALPHA).greaterThan(new AirbyteVersion(VERSION_679_ALPHA)));
    assertFalse(new AirbyteVersion(VERSION_678_ALPHA).greaterThan(new AirbyteVersion("6.7.11-alpha")));
    assertTrue(new AirbyteVersion(VERSION_680_ALPHA).greaterThan(new AirbyteVersion(VERSION_678_ALPHA)));
    assertTrue(new AirbyteVersion(VERSION_6110_ALPHA).greaterThan(new AirbyteVersion(VERSION_678_ALPHA)));
    assertFalse(new AirbyteVersion(VERSION_380_ALPHA).greaterThan(new AirbyteVersion(VERSION_678_ALPHA)));
    assertFalse(new AirbyteVersion(VERSION_380_ALPHA).greaterThan(new AirbyteVersion("11.7.8-alpha")));
    assertFalse(new AirbyteVersion(VERSION_123_PROD).greaterThan(new AirbyteVersion(DEV)));
    assertFalse(new AirbyteVersion(DEV).greaterThan(new AirbyteVersion(VERSION_123_PROD)));
  }

  @Test
  void testLessThan() {
    assertFalse(new AirbyteVersion(VERSION_678_OMEGA).lessThan(new AirbyteVersion(VERSION_678_GAMMA)));
    assertTrue(new AirbyteVersion(VERSION_678_ALPHA).lessThan(new AirbyteVersion(VERSION_679_ALPHA)));
    assertTrue(new AirbyteVersion(VERSION_678_ALPHA).lessThan(new AirbyteVersion("6.7.11-alpha")));
    assertFalse(new AirbyteVersion(VERSION_680_ALPHA).lessThan(new AirbyteVersion(VERSION_678_ALPHA)));
    assertFalse(new AirbyteVersion(VERSION_6110_ALPHA).lessThan(new AirbyteVersion(VERSION_678_ALPHA)));
    assertTrue(new AirbyteVersion(VERSION_380_ALPHA).lessThan(new AirbyteVersion(VERSION_678_ALPHA)));
    assertTrue(new AirbyteVersion(VERSION_380_ALPHA).lessThan(new AirbyteVersion("11.7.8-alpha")));
    assertFalse(new AirbyteVersion(VERSION_123_PROD).lessThan(new AirbyteVersion(DEV)));
    assertFalse(new AirbyteVersion(DEV).lessThan(new AirbyteVersion(VERSION_123_PROD)));
  }

  @Test
  void testInvalidVersions() {
    assertThrows(NullPointerException.class, () -> new AirbyteVersion(null));
    assertThrows(IllegalArgumentException.class, () -> new AirbyteVersion("0.6"));
  }

  @Test
  void testSerialize() {
    assertEquals(DEV, new AirbyteVersion(DEV).serialize());

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
    assertFalse(new AirbyteVersion(VERSION_678).checkOnlyPatchVersionIsUpdatedComparedTo(new AirbyteVersion(VERSION_678)));
    assertFalse(new AirbyteVersion("6.9.8").checkOnlyPatchVersionIsUpdatedComparedTo(new AirbyteVersion("6.8.9")));
    assertFalse(new AirbyteVersion("7.7.8").checkOnlyPatchVersionIsUpdatedComparedTo(new AirbyteVersion("6.7.11")));
    assertTrue(new AirbyteVersion("6.7.9").checkOnlyPatchVersionIsUpdatedComparedTo(new AirbyteVersion(VERSION_678)));
  }

}
