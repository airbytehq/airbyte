/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle;

import java.nio.file.Path;

public class SshKeyOracleSourceAcceptanceTest extends AbstractSshOracleSourceAcceptanceTest {

  @Override
  public Path getConfigFilePath() {
    return Path.of("secrets/ssh-key-config.json");
  }

}
