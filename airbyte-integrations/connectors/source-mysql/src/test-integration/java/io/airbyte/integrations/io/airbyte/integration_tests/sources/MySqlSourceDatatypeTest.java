/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.Database;
import io.airbyte.integrations.source.mysql.MySQLContainerFactory;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase;

public class MySqlSourceDatatypeTest extends AbstractMySqlSourceDatatypeTest {

  @Override
  protected JsonNode getConfig() {
    return testdb.integrationTestConfigBuilder()
        .withoutSsl()
        .withStandardReplication()
        .build();
  }

  @Override
  protected Database setupDatabase() {
    final var sharedContainer = new MySQLContainerFactory().shared("mysql:8.0");
    testdb = new MySQLTestDatabase(sharedContainer)
        .withConnectionProperty("zeroDateTimeBehavior", "convertToNull")
        .initialized()
        .withoutStrictMode();
    return testdb.getDatabase();
  }

  @Override
  public boolean testCatalog() {
    return true;
  }

}
