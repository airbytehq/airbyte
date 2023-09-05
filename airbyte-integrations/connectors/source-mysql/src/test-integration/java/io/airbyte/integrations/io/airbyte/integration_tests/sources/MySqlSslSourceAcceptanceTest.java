/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;


import java.nio.file.Path;


public class MySqlSslSourceAcceptanceTest extends MySqlSourceAcceptanceTest {

  @Override
  public Path getConfigFilePath() {
    return Path.of("secrets/mysql-ssl-source-acceptance-test-config.json");
  }
}
