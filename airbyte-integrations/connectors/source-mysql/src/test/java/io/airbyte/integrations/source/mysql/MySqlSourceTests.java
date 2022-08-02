/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import java.sql.Connection;
import java.sql.DriverManager;
import java.util.Properties;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.MySQLContainer;
import org.testcontainers.containers.output.Slf4jLogConsumer;

public class MySqlSourceTests {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlSourceTests.class);

  private static final String TEST_USER = "test";
  private static final String TEST_PASSWORD = "test";

  @Test
  public void testSettingTimezones() throws Exception {
    // start DB
    try (final MySQLContainer<?> container = new MySQLContainer<>("mysql:8.0")
        .withUsername(TEST_USER)
        .withPassword(TEST_PASSWORD)
        .withEnv("MYSQL_ROOT_HOST", "%")
        .withEnv("MYSQL_ROOT_PASSWORD", TEST_PASSWORD)
        .withEnv("TZ", "Europe/Moscow")
        .withLogConsumer(new Slf4jLogConsumer(LOGGER))) {

      container.start();

      final Properties properties = new Properties();
      properties.putAll(ImmutableMap.of("user", "root", JdbcUtils.PASSWORD_KEY, TEST_PASSWORD, "serverTimezone", "Europe/Moscow"));
      DriverManager.getConnection(container.getJdbcUrl(), properties);
      final String dbName = Strings.addRandomSuffix("db", "_", 10);
      final JsonNode config = getConfig(container, dbName, "serverTimezone=Europe/Moscow");

      try (final Connection connection = DriverManager.getConnection(container.getJdbcUrl(), properties)) {
        connection.createStatement().execute("GRANT ALL PRIVILEGES ON *.* TO '" + TEST_USER + "'@'%';\n");
        connection.createStatement().execute("CREATE DATABASE " + config.get(JdbcUtils.DATABASE_KEY).asText());
      }
      final AirbyteConnectionStatus check = new MySqlSource().check(config);
      assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, check.getStatus());
    }
  }

  private static JsonNode getConfig(final MySQLContainer dbContainer, final String dbName, final String jdbcParams) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, dbContainer.getHost())
        .put(JdbcUtils.PORT_KEY, dbContainer.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, dbName)
        .put(JdbcUtils.USERNAME_KEY, TEST_USER)
        .put(JdbcUtils.PASSWORD_KEY, TEST_PASSWORD)
        .put(JdbcUtils.JDBC_URL_PARAMS_KEY, jdbcParams)
        .build());
  }

}
