/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.commons.version.AirbyteVersion;
import org.junit.jupiter.api.Test;

class ServerAppTest {

  @Test
  void testIsLegalUpgradePredicate() {
    // starting from no previous version is always legal.
    assertTrue(ServerApp.isLegalUpgrade(null, new AirbyteVersion("0.17.1-alpha")));
    assertTrue(ServerApp.isLegalUpgrade(null, new AirbyteVersion("0.32.0-alpha")));
    assertTrue(ServerApp.isLegalUpgrade(null, new AirbyteVersion("0.32.1-alpha")));
    assertTrue(ServerApp.isLegalUpgrade(null, new AirbyteVersion("0.33.1-alpha")));
    // starting from a version that is pre-breaking migration cannot go past the breaking migration.
    assertTrue(ServerApp.isLegalUpgrade(new AirbyteVersion("0.17.0-alpha"), new AirbyteVersion("0.17.1-alpha")));
    assertTrue(ServerApp.isLegalUpgrade(new AirbyteVersion("0.17.0-alpha"), new AirbyteVersion("0.18.0-alpha")));
    assertTrue(ServerApp.isLegalUpgrade(new AirbyteVersion("0.17.0-alpha"), new AirbyteVersion("0.32.0-alpha")));
    assertFalse(ServerApp.isLegalUpgrade(new AirbyteVersion("0.17.0-alpha"), new AirbyteVersion("0.32.1-alpha")));
    assertFalse(ServerApp.isLegalUpgrade(new AirbyteVersion("0.17.0-alpha"), new AirbyteVersion("0.33.0-alpha")));
    // any migration starting at the breaking migration or after it can upgrade to anything.
    assertTrue(ServerApp.isLegalUpgrade(new AirbyteVersion("0.32.0-alpha"), new AirbyteVersion("0.32.1-alpha")));
    assertTrue(ServerApp.isLegalUpgrade(new AirbyteVersion("0.32.0-alpha"), new AirbyteVersion("0.33.0-alpha")));
    assertTrue(ServerApp.isLegalUpgrade(new AirbyteVersion("0.32.1-alpha"), new AirbyteVersion("0.32.1-alpha")));
    assertTrue(ServerApp.isLegalUpgrade(new AirbyteVersion("0.32.1-alpha"), new AirbyteVersion("0.33.0-alpha")));
    assertTrue(ServerApp.isLegalUpgrade(new AirbyteVersion("0.33.0-alpha"), new AirbyteVersion("0.33.1-alpha")));
    assertTrue(ServerApp.isLegalUpgrade(new AirbyteVersion("0.33.0-alpha"), new AirbyteVersion("0.34.0-alpha")));
  }

}
