/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.zaxxer.hikari.HikariDataSource;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import java.util.Map;
import javax.sql.DataSource;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MSSQLServerContainer;

public class MssqlDataSourceFactoryTest {

  @Test
  protected void testCreatingDataSourceWithConnectionTimeoutSetBelowDefault() {
    final MSSQLServerContainer container = new MsSQLContainerFactory().shared("mcr.microsoft.com/mssql/server:2019-latest");
    final Map<String, String> connectionProperties = Map.of("loginTimeout", String.valueOf(5));
    final DataSource dataSource = DataSourceFactory.create(
        container.getUsername(),
        container.getPassword(),
        container.getDriverClassName(),
        container.getJdbcUrl(),
        connectionProperties,
        new MssqlSource().getConnectionTimeoutMssql(connectionProperties));
    assertNotNull(dataSource);
    assertEquals(HikariDataSource.class, dataSource.getClass());
    assertEquals(5000, ((HikariDataSource) dataSource).getHikariConfigMXBean().getConnectionTimeout());
  }

}
