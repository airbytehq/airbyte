/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence.split_secrets;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class SecretCoordinateTest {

  @Test
  void testGetFullCoordinate() {
    final var coordinate = new SecretCoordinate("some_base", 1);
    assertEquals("some_base_v1", coordinate.getFullCoordinate());
  }

}
