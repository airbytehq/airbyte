/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.standardtest.source;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.zaxxer.hikari.HikariDataSource;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import java.util.Map;
import javax.sql.DataSource;
import org.testcontainers.containers.JdbcDatabaseContainer;

abstract public class DataSourceFactoryTest<T extends JdbcDatabaseContainer<T>> {

  protected void testCreatingDataSourceWithConnectionTimeoutSetBelowDefault(T container, int defaultTimeout, String timeoutKey, int explicitTimeout) {
    final DataSource dataSource = DataSourceFactory.create(
        container.getUsername(),
        container.getPassword(),
        container.getDriverClassName(),
        container.getJdbcUrl(),
        Map.of(timeoutKey, String.valueOf(explicitTimeout)));
    assertNotNull(dataSource);
    assertEquals(HikariDataSource.class, dataSource.getClass());
    assertEquals(defaultTimeout, ((HikariDataSource) dataSource).getHikariConfigMXBean().getConnectionTimeout());
  }

}
