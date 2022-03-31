/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.api.model.HealthCheckRead;
import org.junit.jupiter.api.Test;

class HealthCheckHandlerTest {

  @Test
  void testDbHealth() {
    final HealthCheckHandler healthCheckHandler = new HealthCheckHandler();
    assertEquals(new HealthCheckRead().available(true), healthCheckHandler.health());
  }

}
