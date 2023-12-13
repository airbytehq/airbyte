/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import io.airbyte.cdk.integrations.standardtest.source.DataSourceFactoryTest;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MSSQLServerContainer;

public class MssqlDataSourceFactoryTest {

  @Test
  protected void testCreatingDataSourceWithConnectionTimeoutSetBelowDefault() {
    DataSourceFactoryTest.<MSSQLServerContainer<?>>testCreatingDataSourceWithConnectionTimeoutSetBelowDefault(
        new MsSQLContainerFactory().shared("mcr.microsoft.com/mssql/server:2019-latest"),
        5000, "loginTimeout", 5);
  }

}
