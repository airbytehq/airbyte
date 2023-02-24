/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config;

import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs.DeploymentMode;
import io.airbyte.config.Configs.JobErrorReportingStrategy;
import io.airbyte.config.Configs.WorkerEnvironment;
import java.net.URI;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

@SuppressWarnings("PMD.NullAssignment")
class EnvConfigsTest {

  private Map<String, String> envMap;
  private EnvConfigs config;
  private final static String DEV = "dev";

  @BeforeEach
  void setUp() {
    envMap = new HashMap<>();
    config = new EnvConfigs(envMap);
  }

  @Test
  void ensureGetEnvBehavior() {
    assertNull(System.getenv("MY_RANDOM_VAR_1234"));
  }

  @Test
  void testAirbyteVersion() {
    envMap.put(EnvConfigs.AIRBYTE_VERSION, null);
    assertThrows(IllegalArgumentException.class, () -> config.getAirbyteVersion());

    envMap.put(EnvConfigs.AIRBYTE_VERSION, DEV);
    assertEquals(new AirbyteVersion(DEV), config.getAirbyteVersion());
  }
}
