/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import java.nio.file.Path;

public class SshPasswordMySqlSourceAcceptanceTest extends AbstractSshMySqlSourceAcceptanceTest {

  @Override
  public Path getConfigFilePath() {
    return Path.of("secrets/ssh-pwd-repl-config.json");
  }

}
