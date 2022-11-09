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
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TeradataDestinationTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(TeradataDestinationTest.class);

  private JsonNode config;
  final TeradataDestination destination = new TeradataDestination();

  private static final String EXPECTED_JDBC_URL = "jdbc:teradata://localhost/";

  private JsonNode buildConfigNoJdbcParameters() {
    return Jsons.jsonNode(ImmutableMap.of(JdbcUtils.HOST_KEY, "localhost", JdbcUtils.USERNAME_KEY, "user",
        JdbcUtils.DATABASE_KEY, "db"));
  }

  private static final String EXPECTED_JDBC_ESCAPED_URL = "jdbc:teradata://localhost/";

  private JsonNode buildConfigEscapingNeeded() {
    return Jsons.jsonNode(ImmutableMap.of(JdbcUtils.HOST_KEY, "localhost", JdbcUtils.USERNAME_KEY, "user",
        JdbcUtils.DATABASE_KEY, "db/foo"));
  }

  private JsonNode buildConfigWithExtraJdbcParameters(final String extraParam) {
    return Jsons.jsonNode(ImmutableMap.of(JdbcUtils.HOST_KEY, "localhost", JdbcUtils.USERNAME_KEY, "user",
        JdbcUtils.DATABASE_KEY, "db", JdbcUtils.JDBC_URL_PARAMS_KEY, extraParam));
  }

  @Test
  void testJdbcUrlAndConfigNoExtraParams() {
    final JsonNode jdbcConfig = new TeradataDestination().toJdbcConfig(buildConfigNoJdbcParameters());
    LOGGER.info(" JDBC URL of JdbcUrl With No Extra Params --  " + jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
    assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
  }

  @Test
  void testJdbcUrlWithEscapedDatabaseName() {
    final JsonNode jdbcConfig = new TeradataDestination().toJdbcConfig(buildConfigEscapingNeeded());
    LOGGER.info(" JDBC URL of JdbcUrl With Escaped DatabaseName test --  " + jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
    assertEquals(EXPECTED_JDBC_ESCAPED_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
  }

  @Test
  void testJdbcUrlEmptyExtraParams() {
    final JsonNode jdbcConfig = new TeradataDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(""));
    LOGGER.info(" JDBC URL of JdbcUrl With Empty params --  " + jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
    assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
  }

  @Test
  void testJdbcUrlExtraParams() {
    final String extraParam = "key1=value1&key2=value2&key3=value3";
    final JsonNode jdbcConfig = new TeradataDestination()
        .toJdbcConfig(buildConfigWithExtraJdbcParameters(extraParam));
    LOGGER.info(" jdbcConfig in testJdbcUrlExtraParams -   " + jdbcConfig);
    LOGGER
        .info(" JDBC URL of JdbcUrl With Escaped DatabaseName test in testJdbcUrlExtraParams -   " + jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
    assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
  }

  @Test
  void testCheckIncorrectPasswordFailure() {
    final var config = buildConfigNoJdbcParameters();
    LOGGER.info(" config in testCheckIncorrectPasswordFailure -   " + config);
    ((ObjectNode) config).put(JdbcUtils.PASSWORD_KEY, "fake");
    ((ObjectNode) config).put(JdbcUtils.SCHEMA_KEY, "public");
    final TeradataDestination destination = new TeradataDestination();
    final var actual = destination.check(config);
    LOGGER.info(" Status msg of testCheckIncorrectPasswordFailure -   " + actual.getMessage());
    assertTrue(actual.getMessage().contains("SQLState 08S01"));
  }

  @Test
  public void testCheckIncorrectUsernameFailure() {
    final var config = buildConfigNoJdbcParameters();
    LOGGER.info(" config in testCheckIncorrectUsernameFailure -   " + config);
    ((ObjectNode) config).put(JdbcUtils.USERNAME_KEY, "");
    ((ObjectNode) config).put(JdbcUtils.SCHEMA_KEY, "public");
    final TeradataDestination destination = new TeradataDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    LOGGER.info(" Status msg of testCheckIncorrectUsernameFailure -   " + status.getMessage());
    assertTrue(status.getMessage().contains("SQLState 08S01"));
  }

  @Test
  public void testCheckIncorrectHostFailure() {
    final var config = buildConfigNoJdbcParameters();
    LOGGER.info(" config in testCheckIncorrectHostFailure -   " + config);
    ((ObjectNode) config).put(JdbcUtils.HOST_KEY, "localhost2");
    ((ObjectNode) config).put(JdbcUtils.SCHEMA_KEY, "public");
    final TeradataDestination destination = new TeradataDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    LOGGER.info(" Status msg of testCheckIncorrectHostFailure -   " + status.getMessage());
    assertTrue(status.getMessage().contains("SQLState 08S01"));
  }

  @Test
  public void testCheckIncorrectDataBaseFailure() {
    final var config = buildConfigNoJdbcParameters();
    LOGGER.info(" config in testCheckIncorrectDataBaseFailure -   " + config);
    ((ObjectNode) config).put(JdbcUtils.DATABASE_KEY, "wrongdatabase");
    ((ObjectNode) config).put(JdbcUtils.SCHEMA_KEY, "public");
    final TeradataDestination destination = new TeradataDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    LOGGER.info(" Status msg of testCheckIncorrectDataBaseFailure -   " + status.getMessage());
    System.out.println(" Status msg of testCheckIncorrectDataBaseFailure -   " + status.getMessage());
    assertTrue(status.getMessage().contains("SQLState 08S01"));
  }

}
