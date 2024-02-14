/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.Database;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.BaseImage;

public class MssqlSourceDatatypeTest extends AbstractMssqlSourceDatatypeTest {

  @Override
  protected Database setupDatabase() {
    testdb = MsSQLTestDatabase.in(BaseImage.MSSQL_2022);
    return testdb.getDatabase();
  }

  @Override
  protected JsonNode getConfig() {
    return testdb.integrationTestConfigBuilder()
        .withoutSsl()
        .build();
  }

  @Override
  public boolean testCatalog() {
    return true;
  }

}
