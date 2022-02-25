/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.spy;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import java.util.Map;
import java.util.Map.Entry;
import org.junit.jupiter.api.Test;

public class MySQLDestinationTest {

  private MySQLDestination getDestination() {
    final MySQLDestination result = spy(MySQLDestination.class);
    return result;
  }

  private JsonNode buildConfigNoJdbcParameters() {
    final JsonNode config = Jsons.jsonNode(ImmutableMap.of(
        "host", "localhost",
        "port", 1337,
        "username", "user",
        "database", "db"));
    return config;
  }

  private JsonNode buildConfigWithExtraJdbcParameters(final String extraParam) {
    final JsonNode config = Jsons.jsonNode(ImmutableMap.of(
        "host", "localhost",
        "port", 1337,
        "username", "user",
        "database", "db",
        "jdbc_url_params", extraParam));
    return config;
  }

  private JsonNode buildConfigWithExtraJdbcParametersWithNoSsl(final String extraParam) {
    final JsonNode config = Jsons.jsonNode(ImmutableMap.of(
        "host", "localhost",
        "port", 1337,
        "username", "user",
        "database", "db",
        "ssl", false,
        "jdbc_url_params", extraParam));
    return config;
  }

  private JsonNode buildConfigNoExtraJdbcParametersWithoutSsl() {
    final JsonNode config = Jsons.jsonNode(ImmutableMap.of(
        "host", "localhost",
        "port", 1337,
        "username", "user",
        "database", "db",
        "ssl", false));
    return config;
  }

  @Test
  void testNoExtraParams() {
    final JsonNode jdbcConfig = getDestination().toJdbcConfig(buildConfigNoJdbcParameters());
    final String url = jdbcConfig.get("jdbc_url").asText();
    assertEquals("jdbc:mysql://localhost:1337/db?verifyServerCertificate=false&zeroDateTimeBehavior=convertToNull&requireSSL=true&useSSL=true", url);
  }

  @Test
  void testEmptyExtraParams() {
    final JsonNode jdbcConfig = getDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(""));
    final String url = jdbcConfig.get("jdbc_url").asText();
    assertEquals("jdbc:mysql://localhost:1337/db?verifyServerCertificate=false&zeroDateTimeBehavior=convertToNull&requireSSL=true&useSSL=true", url);
  }

  @Test
  void testExtraParams() {
    final String extraParam = "key1=value1&key2=value2&key3=value3";
    final JsonNode jdbcConfig = getDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(extraParam));
    final String url = jdbcConfig.get("jdbc_url").asText();
    assertEquals(
        "jdbc:mysql://localhost:1337/db?key1=value1&key2=value2&key3=value3&verifyServerCertificate=false&zeroDateTimeBehavior=convertToNull&requireSSL=true&useSSL=true",
        url);
  }

  @Test
  void testExtraParamsWithDefaultParameter() {
    final Map<String, String> allDefaultParameters = MoreMaps.merge(MySQLDestination.SSL_JDBC_PARAMETERS,
        MySQLDestination.DEFAULT_JDBC_PARAMETERS);
    for (final Entry<String, String> entry : allDefaultParameters.entrySet()) {
      final String identicalParameter = MySQLDestination.formatParameter(entry.getKey(), entry.getValue());
      final String overridingParameter = MySQLDestination.formatParameter(entry.getKey(), "DIFFERENT_VALUE");

      // Do not throw an exception if the values are equal
      assertDoesNotThrow(() -> getDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(identicalParameter)).get("jdbc_url").asText());
      // Throw an exception if the values are different
      assertThrows(IllegalArgumentException.class, () -> getDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(overridingParameter)));
    }
  }

  @Test
  void testExtraParameterNoSsl() {
    final String extraParam = "key1=value1&key2=value2&key3=value3";
    final JsonNode jdbcConfig = getDestination().toJdbcConfig(buildConfigWithExtraJdbcParametersWithNoSsl(extraParam));
    final String url = jdbcConfig.get("jdbc_url").asText();
    assertEquals(
        "jdbc:mysql://localhost:1337/db?key1=value1&key2=value2&key3=value3&zeroDateTimeBehavior=convertToNull",
        url);
  }

  @Test
  void testNoExtraParameterNoSsl() {
    final JsonNode jdbcConfig = getDestination().toJdbcConfig(buildConfigNoExtraJdbcParametersWithoutSsl());
    final String url = jdbcConfig.get("jdbc_url").asText();
    assertEquals(
        "jdbc:mysql://localhost:1337/db?zeroDateTimeBehavior=convertToNull",
        url);
  }

  @Test
  void testInvalidExtraParam() {
    final String extraParam = "key1=value1&sdf&";
    assertThrows(IllegalArgumentException.class, () -> {
      getDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(extraParam));
    });
  }

}
