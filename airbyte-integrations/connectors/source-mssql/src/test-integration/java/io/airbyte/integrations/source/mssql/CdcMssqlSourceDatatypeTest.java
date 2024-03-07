/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.Database;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.BaseImage;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.ContainerModifier;

public class CdcMssqlSourceDatatypeTest extends AbstractMssqlSourceDatatypeTest {

  @Override
  protected JsonNode getConfig() {
    return testdb.integrationTestConfigBuilder()
        .withCdcReplication()
        .withoutSsl()
        .build();
  }

  @Override
  protected Database setupDatabase() {
    testdb = MsSQLTestDatabase.in(BaseImage.MSSQL_2022, ContainerModifier.AGENT)
        .withCdc();
    return testdb.getDatabase();
  }

  protected void createTables() throws Exception {
    super.createTables();
    for (var test : testDataHolders) {
      testdb.withCdcForTable(test.getNameSpace(), test.getNameWithTestPrefix(), null);
    }
  }

  protected void populateTables() throws Exception {
    super.populateTables();
    for (var test : testDataHolders) {
      testdb.waitForCdcRecords(test.getNameSpace(), test.getNameWithTestPrefix(), test.getValues().size());
    }
  }

  @Override
  public boolean testCatalog() {
    return true;
  }

}
