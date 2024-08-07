/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.Database;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase.BaseImage;

public class CdcInitialSnapshotMySqlSourceDatatypeTest extends AbstractMySqlSourceDatatypeTest {

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

  @Override
  public boolean testCatalog() {
    return true;
  }

}
