package io.airbyte.integrations.destination.mysql;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.spy;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
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
        "database", "db"
    ));
    return config;
  }

  private JsonNode buildConfigWithExtraJdbcParameters(final String extraParam) {
    final JsonNode config = Jsons.jsonNode(ImmutableMap.of(
        "host", "localhost",
        "port", 1337,
        "username", "user",
        "database", "db",
        "jdbc_url_params", extraParam
    ));
    return config;
  }

  private JsonNode buildConfigWithExtraJdbcParametersWithNoSsl(final String extraParam) {
    final JsonNode config = Jsons.jsonNode(ImmutableMap.of(
        "host", "localhost",
        "port", 1337,
        "username", "user",
        "database", "db",
        "ssl", false,
        "jdbc_url_params", extraParam
    ));
    return config;
  }

  private JsonNode buildConfigNoExtraJdbcParametersWithoutSsl() {
    final JsonNode config = Jsons.jsonNode(ImmutableMap.of(
        "host", "localhost",
        "port", 1337,
        "username", "user",
        "database", "db",
        "ssl", false
    ));
    return config;
  }

  @Test
  void testNoExtraParams() {
    final JsonNode jdbcConfig = getDestination().toJdbcConfig(buildConfigNoJdbcParameters());
    final String url = jdbcConfig.get("jdbc_url").asText();
    assertEquals("jdbc:mysql://localhost:1337/db?verifyServerCertificate=false&zeroDateTimeBehavior=convertToNull&requireSSL=true&useSSL=true&", url);
  }

  @Test
  void testEmptyExtraParams() {
    final JsonNode jdbcConfig = getDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(""));
    final String url = jdbcConfig.get("jdbc_url").asText();
    assertEquals("jdbc:mysql://localhost:1337/db?verifyServerCertificate=false&zeroDateTimeBehavior=convertToNull&requireSSL=true&useSSL=true&", url);
  }

  @Test
  void testExtraParams() {
    final String extraParam = "key1=value1&key2=value2&key3=value3";
    final JsonNode jdbcConfig = getDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(extraParam));
    final String url = jdbcConfig.get("jdbc_url").asText();
    assertEquals(
        "jdbc:mysql://localhost:1337/db?key1=value1&key2=value2&key3=value3&verifyServerCertificate=false&zeroDateTimeBehavior=convertToNull&requireSSL=true&useSSL=true&",
        url);
  }

  @Test
  void testExtraParamsWithDefaultParameter() {
    for (final Entry<String, String> entry : MySQLDestination.SSL_JDBC_PARAMETERS.entrySet()) {
      final String extraParam = MySQLDestination.formatParameter(entry.getKey(), entry.getValue());
      assertThrows(RuntimeException.class, () ->
          getDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(extraParam))
      );
    }

    for (final Entry<String, String> entry : MySQLDestination.DEFAULT_JDBC_PARAMETERS.entrySet()) {
      final String extraParam = MySQLDestination.formatParameter(entry.getKey(), entry.getValue());
      assertThrows(RuntimeException.class, () ->
          getDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(extraParam))
      );
    }
  }

  @Test
  void testExtraParameterNoSsl() {
    final String extraParam = "key1=value1&key2=value2&key3=value3";
    final JsonNode jdbcConfig = getDestination().toJdbcConfig(buildConfigWithExtraJdbcParametersWithNoSsl(extraParam));
    final String url = jdbcConfig.get("jdbc_url").asText();
    assertEquals(
        "jdbc:mysql://localhost:1337/db?key1=value1&key2=value2&key3=value3&zeroDateTimeBehavior=convertToNull&",
        url);
  }

  @Test
  void testNoExtraParameterNoSsl() {
    final JsonNode jdbcConfig = getDestination().toJdbcConfig(buildConfigNoExtraJdbcParametersWithoutSsl());
    final String url = jdbcConfig.get("jdbc_url").asText();
    assertEquals(
        "jdbc:mysql://localhost:1337/db?zeroDateTimeBehavior=convertToNull&",
        url);
  }

  @Test
  void testInvalidExtraParam() {
    final String extraParam = "key1=value1&sdf&";
    assertThrows(RuntimeException.class, () -> {
      getDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(extraParam));
    });
  }
}
