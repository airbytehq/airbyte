/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import java.nio.file.Files;
import java.nio.file.Paths;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TeradataDestinationTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(TeradataDestinationTest.class);

  private JsonNode config;
  final TeradataDestination destination = new TeradataDestination();

  private static String EXPECTED_JDBC_URL = "jdbc:teradata://localhost/";
  private static String EXPECTED_JDBC_ESCAPED_URL = "jdbc:teradata://localhost/";

  private String getUserName() {
    return config.get(JdbcUtils.USERNAME_KEY).asText();
  }

  private String getPassword() {
    return config.get(JdbcUtils.PASSWORD_KEY).asText();
  }

  private String getHostName() {
    return config.get(JdbcUtils.HOST_KEY).asText();
  }

  private JsonNode buildConfigNoJdbcParameters() {
    return Jsons.jsonNode(ImmutableMap.of(JdbcUtils.HOST_KEY, config.get(JdbcUtils.HOST_KEY).asText(),
        JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText(), JdbcUtils.DATABASE_KEY,
        config.get(JdbcUtils.PASSWORD_KEY).asText()));
  }

  @BeforeEach
  void setup() {

    try {
      this.config = Jsons.clone(Jsons.deserialize(Files.readString(Paths.get("secrets/config.json"))));
      this.EXPECTED_JDBC_URL = String.format("jdbc:teradata://%s/", config.get(JdbcUtils.HOST_KEY).asText());
      this.EXPECTED_JDBC_ESCAPED_URL = String.format("jdbc:teradata://%s/",
          config.get(JdbcUtils.HOST_KEY).asText());
    } catch (Exception e) {
      AirbyteTraceMessageUtility.emitSystemErrorTrace(e, "setup failed");
    }
  }

  @AfterAll
  static void cleanUp() {}

  private JsonNode buildConfigEscapingNeeded() {
    return Jsons.jsonNode(ImmutableMap.of(JdbcUtils.HOST_KEY, getHostName(), JdbcUtils.USERNAME_KEY, getUserName(),
        JdbcUtils.DATABASE_KEY, "db/foo"));
  }

  private JsonNode buildConfigWithExtraJdbcParameters(final String extraParam) {
    return Jsons.jsonNode(ImmutableMap.of(JdbcUtils.HOST_KEY, getHostName(), JdbcUtils.USERNAME_KEY, getUserName(),
        JdbcUtils.DATABASE_KEY, "db", JdbcUtils.JDBC_URL_PARAMS_KEY, extraParam));
  }

  @Test
  void testJdbcUrlAndConfigNoExtraParams() {
    final JsonNode jdbcConfig = new TeradataDestination().toJdbcConfig(buildConfigNoJdbcParameters());
    assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
  }

  @Test
  void testJdbcUrlWithEscapedDatabaseName() {
    final JsonNode jdbcConfig = new TeradataDestination().toJdbcConfig(buildConfigEscapingNeeded());
    assertEquals(EXPECTED_JDBC_ESCAPED_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
  }

  @Test
  void testJdbcUrlEmptyExtraParams() {
    final JsonNode jdbcConfig = new TeradataDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(""));
    assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
  }

  @Test
  void testJdbcUrlExtraParams() {
    final String extraParam = "key1=value1&key2=value2&key3=value3";
    final JsonNode jdbcConfig = new TeradataDestination()
        .toJdbcConfig(buildConfigWithExtraJdbcParameters(extraParam));
    assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
  }

  @Test
  void testCheckIncorrectPasswordFailure() {
    final var config = buildConfigNoJdbcParameters();
    ((ObjectNode) config).put(JdbcUtils.PASSWORD_KEY, "fake");
    ((ObjectNode) config).put(JdbcUtils.SCHEMA_KEY, "public");
    final TeradataDestination destination = new TeradataDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    // State code: 28000; Error code: 8017; Message: [Teradata Database] [TeraJDBC
    // 17.20.00.12] [Error 8017] [SQLState 28000] The UserId, Password or Account is
    // invalid."}}
    assertTrue(status.getMessage().contains("SQLState 28000"));
  }

  @Test
  public void testCheckIncorrectUsernameFailure() {
    final var config = buildConfigNoJdbcParameters();
    LOGGER.info(" config in testCheckIncorrectUsernameFailure -   " + config);
    ((ObjectNode) config).put(JdbcUtils.USERNAME_KEY, "dummy");
    ((ObjectNode) config).put(JdbcUtils.SCHEMA_KEY, "public");
    final TeradataDestination destination = new TeradataDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    // State code: 28000; Error code: 8017; Message: [Teradata Database] [TeraJDBC
    // 17.20.00.12] [Error 8017] [SQLState 28000] The UserId, Password or Account is
    // invalid."}}
    assertTrue(status.getMessage().contains("SQLState 28000"));
  }

  @Test
  public void testCheckIncorrectHostFailure() {
    final var config = buildConfigNoJdbcParameters();
    ((ObjectNode) config).put(JdbcUtils.HOST_KEY, "localhost2");
    ((ObjectNode) config).put(JdbcUtils.SCHEMA_KEY, "public");
    final TeradataDestination destination = new TeradataDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    assertTrue(status.getMessage().contains("SQLState 08S01"));
  }

  @Test
  public void testCheckIncorrectDataBaseFailure() {
    final var config = buildConfigNoJdbcParameters();
    ((ObjectNode) config).put(JdbcUtils.DATABASE_KEY, "wrongdatabase");
    ((ObjectNode) config).put(JdbcUtils.SCHEMA_KEY, "public");
    final TeradataDestination destination = new TeradataDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    // State code: 28000; Error code: 8017; Message: [Teradata Database] [TeraJDBC
    // 17.20.00.12] [Error 8017] [SQLState 28000] The UserId, Password or Account is
    // invalid."}}
    assertTrue(status.getMessage().contains("SQLState 28000"));
  }

}
