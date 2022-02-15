package io.airbyte.integrations.destination.mysql;

import static org.junit.jupiter.api.Assertions.assertEquals;

import static org.junit.jupiter.api.Assertions.assertTrue;
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

  private JsonNode buildConfigNoExtraParams() {
    final JsonNode config = Jsons.jsonNode(ImmutableMap.of(
        "host", "localhost",
        "port", 1337,
        "username", "user",
        "database", "db"
    ));
    return config;
  }

  private JsonNode buildConfigWithExtraParam(String extraParam) {
    final JsonNode config = Jsons.jsonNode(ImmutableMap.of(
        "host", "localhost",
        "port", 1337,
        "username", "user",
        "database", "db",
        "jdbc_url_params", extraParam
    ));
    return config;
  }

  private JsonNode buildConfigWithExtraParamWithoutSSL(String extraParam) {
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

  @Test
  void testNoExtraParams()  {
    JsonNode jdbcConfig = getDestination().toJdbcConfig(buildConfigNoExtraParams());
    String url = jdbcConfig.get("jdbc_url").asText();
    assertEquals("jdbc:mysql://localhost:1337/db?zeroDateTimeBehavior=convertToNull&useSSL=true&requireSSL=true&verifyServerCertificate=false&",url);
  }

  @Test
  void testEmptyExtraParams()  {
    JsonNode jdbcConfig = getDestination().toJdbcConfig(buildConfigWithExtraParam(""));
    String url = jdbcConfig.get("jdbc_url").asText();
    assertEquals("jdbc:mysql://localhost:1337/db?zeroDateTimeBehavior=convertToNull&useSSL=true&requireSSL=true&verifyServerCertificate=false&",url);
  }

  @Test
  void testExtraParams()  {
    String extraParam = "key1=value1&key2=value2&key3=value3";
    JsonNode jdbcConfig = getDestination().toJdbcConfig(buildConfigWithExtraParam(extraParam));
    String url = jdbcConfig.get("jdbc_url").asText();
    assertEquals("jdbc:mysql://localhost:1337/db?zeroDateTimeBehavior=convertToNull&key1=value1&key2=value2&key3=value3&useSSL=true&requireSSL=true&verifyServerCertificate=false&",
        url);
  }

  @Test
  void testExtraParamsWithSSLParameter()  {
    for (Entry<String, String> entry: MySQLDestination.getSSLParameters().entrySet()) {
      String extraParam = MySQLDestination.formatParameter(entry.getKey(), entry.getValue());
      try {
        getDestination().toJdbcConfig(buildConfigWithExtraParam(extraParam));
        //FIXME: why can't I use Test(expected = ?)
        assertTrue(false);
      } catch (RuntimeException e) {
        // pass
      }
    }
  }

  @Test
  void testExtraParamsWithSSLParameterButNoSSL()  {
    for (Entry<String, String> entry: MySQLDestination.getSSLParameters().entrySet()) {
      String extraParam = MySQLDestination.formatParameter(entry.getKey(), entry.getValue());
      JsonNode jdbcConfig = getDestination().toJdbcConfig(buildConfigWithExtraParamWithoutSSL(extraParam));
      String url = jdbcConfig.get("jdbc_url").asText();
      String expected = String.format("jdbc:mysql://localhost:1337/db?zeroDateTimeBehavior=convertToNull&%s&", extraParam);
      assertEquals(expected,
          url);
    }
  }
}
