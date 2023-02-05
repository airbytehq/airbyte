/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.handlers;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.api.model.generated.HealthCheckRead;
import io.airbyte.config.persistence.ConfigRepository;
import org.junit.jupiter.api.Test;

class HealthCheckHandlerTest {

  @Test
  void testDbHealthSucceed() {
    final var mRepository = mock(ConfigRepository.class);
    when(mRepository.healthCheck()).thenReturn(true);

    final HealthCheckHandler healthCheckHandler = new HealthCheckHandler(mRepository);
    assertEquals(new HealthCheckRead().available(true), healthCheckHandler.health());
  }

  @Test
  void testDbHealthFail() {
    final var mRepository = mock(ConfigRepository.class);
    when(mRepository.healthCheck()).thenReturn(false);

    final HealthCheckHandler healthCheckHandler = new HealthCheckHandler(mRepository);
    assertEquals(new HealthCheckRead().available(false), healthCheckHandler.health());
  }

}
