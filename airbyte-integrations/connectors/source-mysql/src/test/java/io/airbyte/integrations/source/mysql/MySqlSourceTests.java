package io.airbyte.integrations.source.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import org.apache.commons.lang3.RandomStringUtils;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MySQLContainer;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Properties;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class MySqlSourceTests {

  private static final String TEST_USER = "test";
  private static final String TEST_PASSWORD = "test";
  private static MySQLContainer<?> container;

  private JsonNode config;
  private Database database;

  @Test
  public void testSettingTimezones() throws Exception {
    // start DB
    container = new MySQLContainer<>("mysql:8.0")
        .withUsername(TEST_USER)
        .withPassword(TEST_PASSWORD)
        .withEnv("MYSQL_ROOT_HOST", "%")
        .withEnv("MYSQL_ROOT_PASSWORD", TEST_PASSWORD)
        .withEnv("TZ", "Europe/Moscow");
    container.start();
    Properties properties = new Properties();
    properties.putAll(ImmutableMap.of("user", "root", "password", TEST_PASSWORD, "serverTimezone", "Europe/Moscow"));
    DriverManager.getConnection(container.getJdbcUrl(), properties);
    String dbName = "db_" + RandomStringUtils.randomAlphabetic(10);
    config = getConfig(container, dbName, "serverTimezone=Europe/Moscow");

    try(Connection connection = DriverManager.getConnection(container.getJdbcUrl(), properties)){
      connection.createStatement().execute("GRANT ALL PRIVILEGES ON *.* TO '" + TEST_USER + "'@'%';\n");
      connection.createStatement().execute("CREATE DATABASE " + config.get("database").asText());
    }
    AirbyteConnectionStatus check = new MySqlSource().check(config);
    assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, check.getStatus());

    // cleanup
    container.close();
  }

  private static JsonNode getConfig(MySQLContainer dbContainer, String dbName, String jdbcParams) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", dbContainer.getHost())
        .put("port", dbContainer.getFirstMappedPort())
        .put("database", dbName)
        .put("username", TEST_USER)
        .put("password", TEST_PASSWORD)
        .put("jdbc_url_params", jdbcParams)
        .build());
  }
}
