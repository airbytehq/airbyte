/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.integrations.standardtest.source.TestDataHolder;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.BaseImage;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.ContainerModifier;
import org.junit.jupiter.api.Disabled;

@Disabled
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

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    super.setupEnvironment(environment);
    enableCdcOnAllTables();
  }

  private void enableCdcOnAllTables() {
    for (TestDataHolder testDataHolder : testDataHolders) {
      testdb.withCdcForTable(testDataHolder.getNameSpace(), testDataHolder.getNameWithTestPrefix(), null);
    }
  }

  @Override
  public boolean testCatalog() {
    return true;
  }

}
