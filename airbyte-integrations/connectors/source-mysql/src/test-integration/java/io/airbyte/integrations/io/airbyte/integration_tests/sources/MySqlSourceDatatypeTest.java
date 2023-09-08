/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;


import java.nio.file.Path;


public class MySqlSourceDatatypeTest extends AbstractMySqlSourceDatatypeTest {

  @Override
  protected Path getConfigFilePath() {
    return  Path.of("secrets/mysql-source-datatype-test-config.json");
  }

}
