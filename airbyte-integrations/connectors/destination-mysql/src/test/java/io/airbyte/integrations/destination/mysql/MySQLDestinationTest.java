package io.airbyte.integrations.destination.mysql;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import java.util.Map;
import org.junit.Before;
import org.junit.jupiter.api.Test;

public class MySQLDestinationTest {

  private static final Map<String, String> DEFAULT_PARAMETERS_WITH_SSL = MoreMaps.merge(
      MySQLDestination.DEFAULT_JDBC_PARAMETERS,
      MySQLDestination.SSL_JDBC_PARAMETERS
  );

  public static final String JDBC_URL = "jdbc:mysql://localhost:1337/db";
  private MySQLDestination destination;

  private JsonNode buildConfigNoJdbcParameters() {
    return Jsons.jsonNode(ImmutableMap.of(
        "host", "localhost",
        "port", 1337,
        "username", "user",
        "database", "db"
    ));
  }

  private JsonNode buildConfigWithExtraJdbcParameters(final String extraParam) {
    return Jsons.jsonNode(ImmutableMap.of(
        "host", "localhost",
        "port", 1337,
        "username", "user",
        "database", "db",
        "jdbc_url_params", extraParam
    ));
  }

  private JsonNode buildConfigNoExtraJdbcParametersWithoutSsl() {
    return Jsons.jsonNode(ImmutableMap.of(
        "host", "localhost",
        "port", 1337,
        "username", "user",
        "database", "db",
        "ssl", false
    ));
  }

  @Before
  public void setUp() {
    destination = new MySQLDestination();
  }

  @Test
  void testNoExtraParams() {
    final JsonNode config = buildConfigNoJdbcParameters();
    final JsonNode jdbcConfig = destination.toJdbcConfig(config);
    assertEquals(JDBC_URL, jdbcConfig.get("jdbc_url").asText());
  }

  @Test
  void testEmptyExtraParams() {
    final JsonNode jdbcConfig = destination.toJdbcConfig(buildConfigWithExtraJdbcParameters(""));
    assertEquals(JDBC_URL, jdbcConfig.get("jdbc_url").asText());
  }

  @Test
  void testExtraParams() {
    final String extraParam = "key1=value1&key2=value2&key3=value3";
    final JsonNode jdbcConfig = destination.toJdbcConfig(buildConfigWithExtraJdbcParameters(extraParam));
    assertEquals(JDBC_URL, jdbcConfig.get("jdbc_url").asText());
  }

  @Test
  void testDefaultParamsNoSSL() {
    final Map<String, String> defaultProperties = destination.getDefaultConnectionProperties(buildConfigNoExtraJdbcParametersWithoutSsl());
    assertEquals(MySQLDestination.DEFAULT_JDBC_PARAMETERS, defaultProperties);
  }

  @Test
  void testDefaultParamsWithSSL() {
    final Map<String, String> defaultProperties = destination.getDefaultConnectionProperties(buildConfigNoJdbcParameters());
    assertEquals(DEFAULT_PARAMETERS_WITH_SSL, defaultProperties);
  }
}
