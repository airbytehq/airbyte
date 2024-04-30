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

public class MssqlDataSourceFactoryTest {

  @Test
  protected void testCreatingDataSourceWithConnectionTimeoutSetBelowDefault() {
    try (var testdb = MsSQLTestDatabase.in(MsSQLTestDatabase.BaseImage.MSSQL_2022)) {
      final Map<String, String> connectionProperties = Map.of("loginTimeout", String.valueOf(5));
      final DataSource dataSource = DataSourceFactory.create(
          testdb.getUserName(),
          testdb.getPassword(),
          testdb.getDatabaseDriver().getDriverClassName(),
          testdb.getJdbcUrl(),
          connectionProperties,
          new MssqlSource().getConnectionTimeoutMssql(connectionProperties));
      assertNotNull(dataSource);
      assertEquals(HikariDataSource.class, dataSource.getClass());
      assertEquals(5000, ((HikariDataSource) dataSource).getHikariConfigMXBean().getConnectionTimeout());
    }
  }

}
