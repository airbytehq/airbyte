/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import java.sql.JDBCType;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MSSQLServerContainer;

public class MssqlJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest {

  protected static final String USERNAME_WITHOUT_PERMISSION = "new_user";
  protected static final String PASSWORD_WITHOUT_PERMISSION = "password_3435!";
  private static MSSQLServerContainer<?> dbContainer;
  private JsonNode config;

  @BeforeAll
  static void init() {
    // In mssql, timestamp is generated automatically, so we need to use
    // the datetime type instead so that we can set the value manually.
    COL_TIMESTAMP_TYPE = "DATETIME";

    dbContainer = new MSSQLServerContainer<>("mcr.microsoft.com/mssql/server:2019-latest").acceptLicense();
    dbContainer.start();
  }

  @BeforeEach
  public void setup() throws Exception {
    final JsonNode configWithoutDbName = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, dbContainer.getHost())
        .put(JdbcUtils.PORT_KEY, dbContainer.getFirstMappedPort())
        .put(JdbcUtils.USERNAME_KEY, dbContainer.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, dbContainer.getPassword())
        .build());

    final DataSource dataSource = DataSourceFactory.create(
        configWithoutDbName.get(JdbcUtils.USERNAME_KEY).asText(),
        configWithoutDbName.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.MSSQLSERVER.getDriverClassName(),
        String.format("jdbc:sqlserver://%s:%d",
            configWithoutDbName.get(JdbcUtils.HOST_KEY).asText(),
            configWithoutDbName.get(JdbcUtils.PORT_KEY).asInt()));

    try {
      final JdbcDatabase database = new DefaultJdbcDatabase(dataSource);

      final String dbName = Strings.addRandomSuffix("db", "_", 10).toLowerCase();

      database.execute(ctx -> ctx.createStatement().execute(String.format("CREATE DATABASE %s;", dbName)));

      config = Jsons.clone(configWithoutDbName);
      ((ObjectNode) config).put(JdbcUtils.DATABASE_KEY, dbName);

      super.setup();
    } finally {
      DataSourceFactory.close(dataSource);
    }
  }

  @AfterAll
  public static void cleanUp() throws Exception {
    dbContainer.close();
  }

  @Override
  public boolean supportsSchemas() {
    return true;
  }

  @Override
  public JsonNode getConfig() {
    return Jsons.clone(config);
  }

  @Override
  public AbstractJdbcSource<JDBCType> getJdbcSource() {
    return new MssqlSource();
  }

  @Override
  public String getDriverClass() {
    return MssqlSource.DRIVER_CLASS;
  }

  @Test
  void testCheckIncorrectPasswordFailure() throws Exception {
    ((ObjectNode) config).put(JdbcUtils.PASSWORD_KEY, "fake");
    final AirbyteConnectionStatus status = source.check(config);
    Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: S0001; Error code: 18456;"));
  }

  @Test
  public void testCheckIncorrectUsernameFailure() throws Exception {
    ((ObjectNode) config).put(JdbcUtils.USERNAME_KEY, "fake");
    final AirbyteConnectionStatus status = source.check(config);
    Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: S0001; Error code: 18456;"));
  }

  @Test
  public void testCheckIncorrectHostFailure() throws Exception {
    ((ObjectNode) config).put(JdbcUtils.HOST_KEY, "localhost2");
    final AirbyteConnectionStatus status = source.check(config);
    Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: 08S01;"));
  }

  @Test
  public void testCheckIncorrectPortFailure() throws Exception {
    ((ObjectNode) config).put(JdbcUtils.PORT_KEY, "0000");
    final AirbyteConnectionStatus status = source.check(config);
    Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: 08S01;"));
  }

  @Test
  public void testCheckIncorrectDataBaseFailure() throws Exception {
    ((ObjectNode) config).put(JdbcUtils.DATABASE_KEY, "wrongdatabase");
    final AirbyteConnectionStatus status = source.check(config);
    Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: S0001; Error code: 4060;"));
  }

  @Test
  public void testUserHasNoPermissionToDataBase() throws Exception {
    database.execute(ctx -> ctx.createStatement()
        .execute(String.format("CREATE LOGIN %s WITH PASSWORD = '%s'; ", USERNAME_WITHOUT_PERMISSION, PASSWORD_WITHOUT_PERMISSION)));
    ((ObjectNode) config).put(JdbcUtils.USERNAME_KEY, USERNAME_WITHOUT_PERMISSION);
    ((ObjectNode) config).put(JdbcUtils.PASSWORD_KEY, PASSWORD_WITHOUT_PERMISSION);
    final AirbyteConnectionStatus status = source.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: S0001; Error code: 4060;"));
  }

}
