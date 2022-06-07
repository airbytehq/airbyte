/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.factory;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

import com.zaxxer.hikari.HikariDataSource;
import java.util.Map;
import javax.sql.DataSource;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link DataSourceFactory} class.
 */
class DataSourceFactoryTest extends CommonFactoryTest {

  @Test
  void testCreatingADataSourceWithJdbcUrl() {
    final String username = container.getUsername();
    final String password = container.getPassword();
    final String driverClassName = container.getDriverClassName();
    final String jdbcUrl = container.getJdbcUrl();

    final DataSource dataSource = DataSourceFactory.create(username, password, driverClassName, jdbcUrl);
    assertNotNull(dataSource);
    assertEquals(HikariDataSource.class, dataSource.getClass());
    assertEquals(10, ((HikariDataSource) dataSource).getHikariConfigMXBean().getMaximumPoolSize());
  }

  @Test
  void testCreatingADataSourceWithJdbcUrlAndConnectionProperties() {
    final String username = container.getUsername();
    final String password = container.getPassword();
    final String driverClassName = container.getDriverClassName();
    final String jdbcUrl = container.getJdbcUrl();
    final Map<String, String> connectionProperties = Map.of("foo", "bar");

    final DataSource dataSource = DataSourceFactory.create(username, password, driverClassName, jdbcUrl, connectionProperties);
    assertNotNull(dataSource);
    assertEquals(HikariDataSource.class, dataSource.getClass());
    assertEquals(10, ((HikariDataSource) dataSource).getHikariConfigMXBean().getMaximumPoolSize());
  }

  @Test
  void testCreatingADataSourceWithHostAndPort() {
    final String username = container.getUsername();
    final String password = container.getPassword();
    final String driverClassName = container.getDriverClassName();
    final String host = container.getHost();
    final Integer port = container.getFirstMappedPort();
    final String database = container.getDatabaseName();

    final DataSource dataSource = DataSourceFactory.create(username, password, host, port, database, driverClassName);
    assertNotNull(dataSource);
    assertEquals(HikariDataSource.class, dataSource.getClass());
    assertEquals(10, ((HikariDataSource) dataSource).getHikariConfigMXBean().getMaximumPoolSize());
  }

  @Test
  void testCreatingADataSourceWithHostPortAndConnectionProperties() {
    final String username = container.getUsername();
    final String password = container.getPassword();
    final String driverClassName = container.getDriverClassName();
    final String host = container.getHost();
    final Integer port = container.getFirstMappedPort();
    final String database = container.getDatabaseName();
    final Map<String, String> connectionProperties = Map.of("foo", "bar");

    final DataSource dataSource = DataSourceFactory.create(username, password, host, port, database, driverClassName, connectionProperties);
    assertNotNull(dataSource);
    assertEquals(HikariDataSource.class, dataSource.getClass());
    assertEquals(10, ((HikariDataSource) dataSource).getHikariConfigMXBean().getMaximumPoolSize());
  }

  @Test
  void testCreatingAnInvalidDataSourceWithHostAndPort() {
    final String username = container.getUsername();
    final String password = container.getPassword();
    final String driverClassName = "Unknown";
    final String host = container.getHost();
    final Integer port = container.getFirstMappedPort();
    final String database = container.getDatabaseName();

    assertThrows(RuntimeException.class, () -> {
      DataSourceFactory.create(username, password, host, port, database, driverClassName);
    });
  }

  @Test
  void testCreatingAPostgresqlDataSource() {
    final String username = container.getUsername();
    final String password = container.getPassword();
    final String host = container.getHost();
    final Integer port = container.getFirstMappedPort();
    final String database = container.getDatabaseName();

    final DataSource dataSource = DataSourceFactory.createPostgres(username, password, host, port, database);
    assertNotNull(dataSource);
    assertEquals(HikariDataSource.class, dataSource.getClass());
    assertEquals(10, ((HikariDataSource) dataSource).getHikariConfigMXBean().getMaximumPoolSize());
  }

  @Test
  void testClosingADataSource() {
    final HikariDataSource dataSource1 = mock(HikariDataSource.class);
    Assertions.assertDoesNotThrow(() -> DataSourceFactory.close(dataSource1));
    verify(dataSource1, times(1)).close();

    final DataSource dataSource2 = mock(DataSource.class);
    Assertions.assertDoesNotThrow(() -> DataSourceFactory.close(dataSource2));

    Assertions.assertDoesNotThrow(() -> DataSourceFactory.close(null));
  }

}
