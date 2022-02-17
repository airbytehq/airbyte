package io.airbyte.integrations.destination.mysql;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.nullable;
import static org.mockito.Mockito.times;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.db.Databases;
import java.util.Map;
import java.util.Map.Entry;
import org.junit.jupiter.api.Test;
import org.mockito.MockedStatic;
import org.mockito.Mockito;

public class MySQLDestinationTest {

  private static final Map<String, String> DEFAULT_PARAMETERS_WITH_SSL = MoreMaps.merge(
      MySQLDestination.DEFAULT_JDBC_PARAMETERS,
      MySQLDestination.SSL_JDBC_PARAMETERS
  );
  private static final Map<String, String> CUSTOM_PROPERTIES = ImmutableMap.of(
      "key1", "value1",
      "key2", "value2",
      "key3", "value3"
  );

  private MySQLDestination getDestination() {
    final MySQLDestination result = new MySQLDestination();
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
    assertEquals("jdbc:mysql://localhost:1337/db", url);
    verifyJdbcDatabaseIsCreatedWithConnectionProperties(buildConfigNoJdbcParameters(), DEFAULT_PARAMETERS_WITH_SSL);
  }

  @Test
  void testEmptyExtraParams() {
    final JsonNode jdbcConfig = getDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(""));
    final String url = jdbcConfig.get("jdbc_url").asText();
    assertEquals("jdbc:mysql://localhost:1337/db", url);
    verifyJdbcDatabaseIsCreatedWithConnectionProperties(buildConfigNoJdbcParameters(), DEFAULT_PARAMETERS_WITH_SSL);
  }

  @Test
  void testExtraParams() {
    final String extraParam = "key1=value1&key2=value2&key3=value3";
    final JsonNode jdbcConfig = getDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(extraParam));
    final String url = jdbcConfig.get("jdbc_url").asText();
    assertEquals("jdbc:mysql://localhost:1337/db", url);

    verifyJdbcDatabaseIsCreatedWithConnectionProperties(buildConfigWithExtraJdbcParameters(extraParam),
        MoreMaps.merge(CUSTOM_PROPERTIES, DEFAULT_PARAMETERS_WITH_SSL));
  }

  @Test
  void testExtraParamsWithDefaultParameter() {
    final Map<String, String> allDefaultParameters = MoreMaps.merge(MySQLDestination.SSL_JDBC_PARAMETERS,
        MySQLDestination.DEFAULT_JDBC_PARAMETERS);
    for (final Entry<String, String> entry : allDefaultParameters.entrySet()) {
      final String identicalParameter = formatParameter(entry.getKey(), entry.getValue());
      final String overridingParameter = formatParameter(entry.getKey(), "DIFFERENT_VALUE");

      // Do not throw an exception if the values are equal
      assertDoesNotThrow(() ->
          getDestination().getDatabase(buildConfigWithExtraJdbcParameters(identicalParameter))
      );
      final Map<String, String> connectionProperties = MoreMaps.merge(
          ImmutableMap.of(entry.getKey(), entry.getValue()),
          MySQLDestination.DEFAULT_JDBC_PARAMETERS
      );
      verifyJdbcDatabaseIsCreatedWithConnectionProperties(buildConfigWithExtraJdbcParametersWithNoSsl(identicalParameter), connectionProperties);

      // Throw an exception if the values are different
      assertThrows(IllegalArgumentException.class, () ->
          getDestination().getDatabase(buildConfigWithExtraJdbcParameters(overridingParameter))
      );
    }
  }

  @Test
  void testExtraParameterNoSsl() {
    final String extraParam = "key1=value1&key2=value2&key3=value3";
    final JsonNode jdbcConfig = getDestination().toJdbcConfig(buildConfigWithExtraJdbcParametersWithNoSsl(extraParam));
    final String url = jdbcConfig.get("jdbc_url").asText();
    assertEquals("jdbc:mysql://localhost:1337/db", url);

    final Map<String, String> connectionProperties = ImmutableMap.of(
        "key1", "value1",
        "key2", "value2",
        "key3", "value3");
    verifyJdbcDatabaseIsCreatedWithConnectionProperties(buildConfigWithExtraJdbcParametersWithNoSsl(extraParam),
        MoreMaps.merge(connectionProperties, MySQLDestination.DEFAULT_JDBC_PARAMETERS));
  }

  @Test
  void testNoExtraParameterNoSsl() {
    final JsonNode jdbcConfig = getDestination().toJdbcConfig(buildConfigNoExtraJdbcParametersWithoutSsl());
    final String url = jdbcConfig.get("jdbc_url").asText();
    assertEquals("jdbc:mysql://localhost:1337/db", url);

    verifyJdbcDatabaseIsCreatedWithConnectionProperties(buildConfigNoExtraJdbcParametersWithoutSsl(), MySQLDestination.DEFAULT_JDBC_PARAMETERS);
  }

  @Test
  void testInvalidExtraParam() {
    final String extraParam = "key1=value1&sdf&";
    assertThrows(IllegalArgumentException.class, () -> {
      getDestination().getDatabase(buildConfigWithExtraJdbcParameters(extraParam));
    });
  }

  void verifyJdbcDatabaseIsCreatedWithConnectionProperties(final JsonNode jsonNode, final Map<String, String> connectionProperties) {
    try (final MockedStatic<Databases> databases = Mockito.mockStatic(Databases.class)) {
      getDestination().getDatabase(jsonNode);
      databases.verify(() -> Databases.createJdbcDatabase(
              anyString(), nullable(String.class), anyString(), anyString(), Mockito.eq(connectionProperties)),
          times(1));
    }
  }

  String formatParameter(final String key, final String value) {
    return String.format("%s=%s", key, value);
  }
}
