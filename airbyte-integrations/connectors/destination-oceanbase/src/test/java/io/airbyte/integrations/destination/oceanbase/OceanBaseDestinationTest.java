/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oceanbase;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.commons.json.Jsons;
import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class OceanBaseDestinationTest {

  public static final String JDBC_URL = "jdbc:oceanbase://localhost:1337";

  private JsonNode buildConfigNoJdbcParameters() {
    return Jsons.jsonNode(ImmutableMap.of(
            JdbcUtils.HOST_KEY, "localhost",
            JdbcUtils.PORT_KEY, 1337,
            JdbcUtils.USERNAME_KEY, "user",
            JdbcUtils.DATABASE_KEY, "db"));
  }

  private JsonNode buildConfigWithExtraJdbcParameters(final String extraParam) {
    return Jsons.jsonNode(ImmutableMap.of(
            JdbcUtils.HOST_KEY, "localhost",
            JdbcUtils.PORT_KEY, 1337,
            JdbcUtils.USERNAME_KEY, "user",
            JdbcUtils.DATABASE_KEY, "db",
            JdbcUtils.JDBC_URL_PARAMS_KEY, extraParam));
  }

  private JsonNode buildConfigNoExtraJdbcParametersWithoutSsl() {
    return Jsons.jsonNode(ImmutableMap.of(
            JdbcUtils.HOST_KEY, "localhost",
            JdbcUtils.PORT_KEY, 1337,
            JdbcUtils.USERNAME_KEY, "user",
            JdbcUtils.DATABASE_KEY, "db",
            JdbcUtils.SSL_KEY, false));
  }

  @Test
  void testNoExtraParams() {
    final JsonNode config = buildConfigNoJdbcParameters();
    final JsonNode jdbcConfig = new OceanBaseDestination().toJdbcConfig(config);
    assertEquals(JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
  }

  @Test
  void testEmptyExtraParams() {
    final JsonNode jdbcConfig = new OceanBaseDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(""));
    assertEquals(JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
  }

  @Test
  void testExtraParams() {
    final String extraParam = "key1=value1&key2=value2&key3=value3";
    final JsonNode jdbcConfig = new OceanBaseDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(extraParam));
    assertEquals(JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
  }

  @Test
  void testDefaultParamsNoSSL() {
    final Map<String, String> defaultProperties = new OceanBaseDestination().getDefaultConnectionProperties(buildConfigNoExtraJdbcParametersWithoutSsl());
    assertEquals(OceanBaseDestination.DEFAULT_JDBC_PARAMETERS, defaultProperties);
  }

  @Test
  void testDefaultParamsWithSSL() {
    final Map<String, String> defaultProperties = new OceanBaseDestination().getDefaultConnectionProperties(buildConfigNoJdbcParameters());
    assertEquals(OceanBaseDestination.DEFAULT_SSL_JDBC_PARAMETERS, defaultProperties);
  }



}
