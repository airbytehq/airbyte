/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql;

import java.nio.file.Path;

public class SshPasswordMySQLDestinationAcceptanceTest extends SshMySQLDestinationAcceptanceTest {

  @Override
  public Path getConfigFilePath() {
    return Path.of("secrets/ssh-pwd-config.json");
  }

}
