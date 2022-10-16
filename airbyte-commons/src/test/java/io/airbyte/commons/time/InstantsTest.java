/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.time;

import static org.junit.jupiter.api.Assertions.*;

import java.time.Instant;
import org.junit.jupiter.api.Test;

class InstantsTest {

  @Test
  void testMillisToSeconds() {
    final Instant now = Instant.now();
    assertEquals(now.getEpochSecond(), Instants.toSeconds(now.toEpochMilli()));
  }

}
