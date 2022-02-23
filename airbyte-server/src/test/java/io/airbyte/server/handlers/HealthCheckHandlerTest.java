/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.api.model.HealthCheckRead;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Collections;
import org.junit.jupiter.api.Test;

class HealthCheckHandlerTest {

  @Test
  void testDbHealth() throws IOException, JsonValidationException {
    final ConfigRepository configRepository = mock(ConfigRepository.class);
    final HealthCheckHandler healthCheckHandler = new HealthCheckHandler(configRepository);

    // check db healthy
    when(configRepository.listStandardWorkspaces(true)).thenReturn(Collections.singletonList(new StandardWorkspace()));
    assertEquals(new HealthCheckRead().db(true), healthCheckHandler.health());

    doThrow(IOException.class).when(configRepository).listStandardWorkspaces(true);
    assertEquals(new HealthCheckRead().db(false), healthCheckHandler.health());
  }

}
