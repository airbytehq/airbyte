/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql;

import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_BUCKET_NAME;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_DB_NAME;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_HOST_OR_PORT;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_PASSWORD;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.util.Map;

import io.airbyte.protocol.models.AirbyteConnectionStatus;
import org.junit.jupiter.api.Test;

public class MySQLDestinationTest {

  public static final String JDBC_URL = "jdbc:mysql://localhost:1337/db";

  private JsonNode buildConfigNoJdbcParameters() {
    return Jsons.jsonNode(ImmutableMap.of(
        "host", "localhost",
        "port", 1337,
        "username", "user",
        "database", "db"));
  }

  private JsonNode buildConfigWithExtraJdbcParameters(final String extraParam) {
    return Jsons.jsonNode(ImmutableMap.of(
        "host", "localhost",
        "port", 1337,
        "username", "user",
        "database", "db",
        "jdbc_url_params", extraParam));
  }

  private JsonNode buildConfigNoExtraJdbcParametersWithoutSsl() {
    return Jsons.jsonNode(ImmutableMap.of(
        "host", "localhost",
        "port", 1337,
        "username", "user",
        "database", "db",
        "ssl", false));
  }

  @Test
  void testNoExtraParams() {
    final JsonNode config = buildConfigNoJdbcParameters();
    final JsonNode jdbcConfig = new MySQLDestination().toJdbcConfig(config);
    assertEquals(JDBC_URL, jdbcConfig.get("jdbc_url").asText());
  }

  @Test
  void testEmptyExtraParams() {
    final JsonNode jdbcConfig = new MySQLDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(""));
    assertEquals(JDBC_URL, jdbcConfig.get("jdbc_url").asText());
  }

  @Test
  void testExtraParams() {
    final String extraParam = "key1=value1&key2=value2&key3=value3";
    final JsonNode jdbcConfig = new MySQLDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(extraParam));
    assertEquals(JDBC_URL, jdbcConfig.get("jdbc_url").asText());
  }

  @Test
  void testDefaultParamsNoSSL() {
    final Map<String, String> defaultProperties = new MySQLDestination().getDefaultConnectionProperties(buildConfigNoExtraJdbcParametersWithoutSsl());
    assertEquals(MySQLDestination.DEFAULT_JDBC_PARAMETERS, defaultProperties);
  }

  @Test
  void testDefaultParamsWithSSL() {
    final Map<String, String> defaultProperties = new MySQLDestination().getDefaultConnectionProperties(buildConfigNoJdbcParameters());
    assertEquals(MySQLDestination.DEFAULT_SSL_JDBC_PARAMETERS, defaultProperties);
  }

  @Test
  void testCheckIncorrectPasswordFailure() {
    var config = buildConfigNoJdbcParameters();
    ((ObjectNode) config).put("password", "fake");
    var destination = new MySQLDestination();
    var actual = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus(), INCORRECT_USERNAME_OR_PASSWORD.getValue());
  }

  @Test
  public void testCheckIncorrectUsernameFailure() {
    var config = buildConfigNoJdbcParameters();
    ((ObjectNode) config).put("username", "");
    var destination = new MySQLDestination();
    final AirbyteConnectionStatus actual = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus(), INCORRECT_USERNAME_OR_PASSWORD.getValue());
  }

  @Test
  public void testCheckIncorrectHostFailure() {
    var config = buildConfigNoJdbcParameters();
    ((ObjectNode) config).put("host", "localhost2");
    var destination = new MySQLDestination();
    final AirbyteConnectionStatus actual = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus(), INCORRECT_BUCKET_NAME.getValue());
  }

  @Test
  public void testCheckIncorrectPortFailure() {
    var config = buildConfigNoJdbcParameters();
    ((ObjectNode) config).put("port", "0000");
    var destination = new MySQLDestination();
    final AirbyteConnectionStatus actual = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus(), INCORRECT_HOST_OR_PORT.getValue());
  }

  @Test
  public void testCheckIncorrectDataBaseFailure() {
    var config = buildConfigNoJdbcParameters();
    ((ObjectNode) config).put("database", "wrongdatabase");
    var destination = new MySQLDestination();
    final AirbyteConnectionStatus actual = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus(), INCORRECT_DB_NAME.getValue());
  }

}
