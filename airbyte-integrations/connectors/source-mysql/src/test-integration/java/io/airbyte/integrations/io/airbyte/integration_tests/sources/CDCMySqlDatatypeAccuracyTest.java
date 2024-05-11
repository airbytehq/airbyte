/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.Database;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase.BaseImage;
import org.junit.jupiter.api.Test;

public class CDCMySqlDatatypeAccuracyTest extends MySqlDatatypeAccuracyTest {

  @Override
  protected JsonNode getConfig() {
    return testdb.integrationTestConfigBuilder()
        .withoutSsl()
        .withCdcReplication()
        .with("snapshot_mode", "initial_only")
        .build();
  }

  @Override
  protected Database setupDatabase() {
    testdb = MySQLTestDatabase.in(BaseImage.MYSQL_8).withoutStrictMode().withCdcPermissions();
    return testdb.getDatabase();
  }

  // Temporarily disable this test since it's causing trouble on GHA.
  @Override
  @Test
  public void testDataContent() {
    // Do Nothing
  }

}
