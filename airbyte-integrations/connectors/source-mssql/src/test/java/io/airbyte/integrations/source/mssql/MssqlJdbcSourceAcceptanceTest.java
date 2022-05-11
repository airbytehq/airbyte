/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import java.sql.JDBCType;

import io.airbyte.protocol.models.AirbyteConnectionStatus;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MSSQLServerContainer;

import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_DB_NAME;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_HOST_OR_PORT;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_PASSWORD;

public class MssqlJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest {

  private static MSSQLServerContainer<?> dbContainer;
  private static JdbcDatabase database;
  private JsonNode config;

  @BeforeAll
  static void init() {
    dbContainer = new MSSQLServerContainer<>("mcr.microsoft.com/mssql/server:2019-latest").acceptLicense();
    dbContainer.start();
  }

  @BeforeEach
  public void setup() throws Exception {
    final JsonNode configWithoutDbName = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", dbContainer.getHost())
        .put("port", dbContainer.getFirstMappedPort())
        .put("username", dbContainer.getUsername())
        .put("password", dbContainer.getPassword())
        .build());

    database = new DefaultJdbcDatabase(
        DataSourceFactory.create(
            configWithoutDbName.get("username").asText(),
            configWithoutDbName.get("password").asText(),
            DatabaseDriver.MSSQLSERVER.getDriverClassName(),
            String.format("jdbc:sqlserver://%s:%d",
                configWithoutDbName.get("host").asText(),
                configWithoutDbName.get("port").asInt())
        )
    );

    final String dbName = Strings.addRandomSuffix("db", "_", 10).toLowerCase();

    database.execute(ctx -> ctx.createStatement().execute(String.format("CREATE DATABASE %s;", dbName)));

    config = Jsons.clone(configWithoutDbName);
    ((ObjectNode) config).put("database", dbName);

    super.setup();
  }

  @AfterAll
  public static void cleanUp() throws Exception {
    database.close();
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
    ((ObjectNode) config).put("password", "fake");
    final AirbyteConnectionStatus actual = source.check(config);
    Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus());
    Assertions.assertEquals(INCORRECT_USERNAME_OR_PASSWORD.getValue(), actual.getMessage());
  }

  @Test
  public void testCheckIncorrectUsernameFailure() throws Exception {
    ((ObjectNode) config).put("username", "fake");
    final AirbyteConnectionStatus actual = source.check(config);
    Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus());
    Assertions.assertEquals(INCORRECT_USERNAME_OR_PASSWORD.getValue(), actual.getMessage());
  }

  @Test
  public void testCheckIncorrectHostFailure() throws Exception {
    ((ObjectNode) config).put("host", "localhost2");
    final AirbyteConnectionStatus actual = source.check(config);
    Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus());
    Assertions.assertEquals(INCORRECT_HOST_OR_PORT.getValue(), actual.getMessage());
  }

  @Test
  public void testCheckIncorrectPortFailure() throws Exception {
    ((ObjectNode) config).put("port", "0000");
    final AirbyteConnectionStatus actual = source.check(config);
    Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus());
    Assertions.assertEquals(INCORRECT_HOST_OR_PORT.getValue(),  actual.getMessage());
  }

  @Test
  public void testCheckIncorrectDataBaseFailure() throws Exception {
    ((ObjectNode) config).put("database", "wrongdatabase");
    final AirbyteConnectionStatus actual = source.check(config);
    Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus());
    Assertions.assertEquals(INCORRECT_DB_NAME.getValue(), actual.getMessage());
  }
}
