/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.zaxxer.hikari.HikariDataSource;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.BaseImage;
import java.util.Map;
import javax.sql.DataSource;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

public class PostgresDataSourceFactoryTest {
  private final String CONNECT_TIMEOUT = "connectTimeout";
  private PostgreSQLContainer container = new PostgresContainerFactory().shared(BaseImage.POSTGRES_16.reference);
  PostgresSource source = new PostgresSource();

  @Test
  void testCreatingDataSourceWithConnectionTimeoutSetAboveDefault() {
    final Map<String, String> connectionProperties = Map.of(
        CONNECT_TIMEOUT, "61");
    final DataSource dataSource = DataSourceFactory.create(
        container.getUsername(),
        container.getPassword(),
        PostgresSource.DRIVER_CLASS,
        container.getJdbcUrl(),
        connectionProperties,
        source.getConnectionTimeout(connectionProperties));
    assertNotNull(dataSource);
    assertEquals(HikariDataSource.class, dataSource.getClass());
    assertEquals(61000, ((HikariDataSource) dataSource).getHikariConfigMXBean().getConnectionTimeout());
  }

  @Test
  void testCreatingPostgresDataSourceWithConnectionTimeoutSetBelowDefault() {
    final Map<String, String> connectionProperties = Map.of(
        CONNECT_TIMEOUT, "30");
    final DataSource dataSource = DataSourceFactory.create(
        container.getUsername(),
        container.getPassword(),
        PostgresSource.DRIVER_CLASS,
        container.getJdbcUrl(),
        connectionProperties,
        source.getConnectionTimeout(connectionProperties));
    assertNotNull(dataSource);
    assertEquals(HikariDataSource.class, dataSource.getClass());
    assertEquals(30000, ((HikariDataSource) dataSource).getHikariConfigMXBean().getConnectionTimeout());
  }

  @Test
  void testCreatingPostgresDataSourceWithConnectionTimeoutNotSet() {
    final Map<String, String> connectionProperties = Map.of();
    final DataSource dataSource = DataSourceFactory.create(
        container.getUsername(),
        container.getPassword(),
        PostgresSource.DRIVER_CLASS,
        container.getJdbcUrl(),
        connectionProperties,
        source.getConnectionTimeout(connectionProperties));
    assertNotNull(dataSource);
    assertEquals(HikariDataSource.class, dataSource.getClass());
    assertEquals(10000, ((HikariDataSource) dataSource).getHikariConfigMXBean().getConnectionTimeout());
  }

}
