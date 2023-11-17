/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.factory.DSLContextFactory;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.cdk.integrations.util.HostPortResolver;
import io.airbyte.commons.json.Jsons;
import java.util.Map;
import org.jooq.DSLContext;
import org.testcontainers.containers.MSSQLServerContainer;

public class MssqlSourceDatatypeTest extends AbstractMssqlSourceDatatypeTest {

  @Override
  protected Database setupDatabase() {
    testdb = MsSQLTestDatabase.in("mcr.microsoft.com/mssql/server:2022-RTM-CU2-ubuntu-20.04");
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
