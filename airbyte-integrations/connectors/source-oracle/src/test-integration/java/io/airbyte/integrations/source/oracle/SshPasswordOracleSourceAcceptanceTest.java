/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle;

import java.nio.file.Path;

public class SshPasswordOracleSourceAcceptanceTest extends AbstractSshOracleSourceAcceptanceTest {

  @Override
  public Path getConfigFilePath() {
    return Path.of("secrets/ssh-pwd-config.json");
  }

}
