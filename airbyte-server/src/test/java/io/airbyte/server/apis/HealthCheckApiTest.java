/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.api.model.generated.HealthCheckRead;
import io.airbyte.commons.server.handlers.HealthCheckHandler;
import org.junit.jupiter.api.Test;

class HealthCheckApiTest {

  @Test
  void testImportDefinitions() {
    final HealthCheckHandler healthCheckHandler = mock(HealthCheckHandler.class);
    when(healthCheckHandler.health())
        .thenReturn(new HealthCheckRead().available(
            false));

    final HealthApiController configurationApi = new HealthApiController(healthCheckHandler);

    assertFalse(configurationApi.getHealthCheck().getAvailable());
  }

}
