/*
 * Copyright (c) 2020 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import java.nio.file.Path;

public class SshPasswordMssqlSourceAcceptanceTest extends AbstractSshMssqlSourceAcceptanceTest {

  @Override
  public Path getConfigFilePath() {
    return Path.of("secrets/ssh-pwd-config.json");
  }

}
