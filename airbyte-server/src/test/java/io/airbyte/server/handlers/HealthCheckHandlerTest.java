/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.api.model.HealthCheckRead;
import io.airbyte.config.persistence.ConfigRepository;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

class HealthCheckHandlerTest {

  @Test
  void testDbHealthSucceed() {
    final var mRepository = Mockito.mock(ConfigRepository.class);
    Mockito.when(mRepository.healthCheck()).thenReturn(true);

    final HealthCheckHandler healthCheckHandler = new HealthCheckHandler(mRepository);
    assertEquals(new HealthCheckRead().available(true), healthCheckHandler.health());
  }

  @Test
  void testDbHealtFailh() {
    final var mRepository = Mockito.mock(ConfigRepository.class);
    Mockito.when(mRepository.healthCheck()).thenReturn(false);

    final HealthCheckHandler healthCheckHandler = new HealthCheckHandler(mRepository);
    assertEquals(new HealthCheckRead().available(false), healthCheckHandler.health());
  }

}
