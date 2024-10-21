/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import java.nio.file.Path;

public class SshKeyMySqlSourceAcceptanceTest extends AbstractSshMySqlSourceAcceptanceTest {

  @Override
  public Path getConfigFilePath() {
    return Path.of("secrets/ssh-key-repl-config.json");
  }

}
