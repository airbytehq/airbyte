/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.version;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class AirbyteProtocolVersionRangeTest {

  @Test
  void checkRanges() {
    final AirbyteProtocolVersionRange range = new AirbyteProtocolVersionRange(new Version("1.2.3"), new Version("4.3.2"));
    assertTrue(range.isSupported(new Version("2.0.0")));
    assertTrue(range.isSupported(new Version("1.2.3")));
    assertTrue(range.isSupported(new Version("4.3.2")));

    // We should only be requiring major to be within range
    assertTrue(range.isSupported(new Version("1.0.0")));
    assertTrue(range.isSupported(new Version("4.4.0")));

    assertFalse(range.isSupported(new Version("0.2.3")));
    assertFalse(range.isSupported(new Version("5.0.0")));
  }

  @Test
  void checkRangeWithOnlyOneMajor() {
    final AirbyteProtocolVersionRange range = new AirbyteProtocolVersionRange(new Version("2.0.0"), new Version("2.1.2"));

    assertTrue(range.isSupported(new Version("2.0.0")));
    assertTrue(range.isSupported(new Version("2.5.0")));

    assertFalse(range.isSupported(new Version("1.0.0")));
    assertFalse(range.isSupported(new Version("3.0.0")));
  }

}
