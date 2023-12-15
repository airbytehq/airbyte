package io.airbyte.integrations.source.mysql;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.zaxxer.hikari.HikariDataSource;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase.BaseImage;
import java.util.Map;
import javax.sql.DataSource;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MySQLContainer;

public class MySqlDataSourceFactoryTest {
  private static final String CONNECT_TIMEOUT = "connectTimeout";
  private MySQLContainer<?> mySQLContainer = new MySQLContainerFactory().shared(BaseImage.MYSQL_8.reference);
  MySqlSource source = new MySqlSource();
  @Test
  void testCreatingMySQLDataSourceWithConnectionTimeoutSetBelowDefault() {
    mySQLContainer.start();
    final Map<String, String> connectionProperties = Map.of(
        CONNECT_TIMEOUT, "5000");
    final DataSource dataSource = DataSourceFactory.create(
        mySQLContainer.getUsername(),
        mySQLContainer.getPassword(),
        MySqlSource.DRIVER_CLASS,
        mySQLContainer.getJdbcUrl(),
        connectionProperties,
        source.getConnectionTimeout(connectionProperties));
    assertNotNull(dataSource);
    assertEquals(HikariDataSource.class, dataSource.getClass());
    assertEquals(5000, ((HikariDataSource) dataSource).getHikariConfigMXBean().getConnectionTimeout());
  }

  @Test
  void testCreatingMySQLDataSourceWithConnectionTimeoutNotSet() {
    mySQLContainer.start();
    final Map<String, String> connectionProperties = Map.of();
    final DataSource dataSource = DataSourceFactory.create(
        mySQLContainer.getUsername(),
        mySQLContainer.getPassword(),
        MySqlSource.DRIVER_CLASS,
        mySQLContainer.getJdbcUrl(),
        connectionProperties,
        source.getConnectionTimeout(connectionProperties));
    assertNotNull(dataSource);
    assertEquals(HikariDataSource.class, dataSource.getClass());
    assertEquals(60000, ((HikariDataSource) dataSource).getHikariConfigMXBean().getConnectionTimeout());
  }
}
