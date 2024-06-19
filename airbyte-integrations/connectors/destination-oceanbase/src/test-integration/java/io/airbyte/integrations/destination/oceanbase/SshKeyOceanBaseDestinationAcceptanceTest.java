/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oceanbase;

import org.junit.jupiter.api.Disabled;

import java.nio.file.Path;

@Disabled
public class SshKeyOceanBaseDestinationAcceptanceTest extends SshOceanBaseDestinationAcceptanceTest {

  @Override
  public Path getConfigFilePath() {
    return Path.of("secrets/ssh-key-config.json");
  }

}
