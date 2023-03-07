/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;

import io.airbyte.config.EnvConfigs;
import io.airbyte.persistence.job.models.JobRunConfig;
import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class EventListenersTest {

  private Map<String, String> envVars;
  private EnvConfigs configs;
  private JobRunConfig jobRunConfig;

  @BeforeEach
  void setup() {
    envVars = new HashMap<String, String>();
    configs = mock(EnvConfigs.class);
    jobRunConfig = mock(JobRunConfig.class);
  }

  @Test
  void setEnvVars() {
    envVars = Map.of(
        // should be set as it is part of the ENV_VARS_TO_TRANSFER
        EnvConfigs.WORKER_ENVIRONMENT, "worker-environment",
        // should not be set as it is not part of ENV_VARS_TO_TRANSFER
        "RANDOM_ENV", "random-env");

    final var properties = new HashMap<String, String>();
    final var listeners = new EventListeners(envVars, configs, jobRunConfig, (name, value) -> {
      properties.put(name, value);
      return null;
    });

    listeners.setEnvVars(null);
    assertEquals(1, properties.size());
    assertEquals("worker-environment", properties.get(EnvConfigs.WORKER_ENVIRONMENT));
  }

}
