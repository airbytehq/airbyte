package io.airbyte.integrations.destination.mysql;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.spy;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import org.junit.jupiter.api.Test;

public class MySQLDestinationTest {

  private static final ObjectMapper mapper = MoreMappers.initMapper();


  private MySQLDestination getDestination() {
    final MySQLDestination result = spy(MySQLDestination.class);
    //doReturn(destinationPath).when(result).getDestinationPath(any());
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

  private JsonNode buildConfigWithExtraParams() {
    final JsonNode config = Jsons.jsonNode(ImmutableMap.of(
        "host", "localhost",
        "port", 1337,
        "username", "user",
        "database", "db",
        "jdbc_url_params", "key1=value1&key2=value2&key3=value3"
    ));
    return config;
  }

  private JsonNode buildConfigWithSSLParam() {
    final JsonNode config = Jsons.jsonNode(ImmutableMap.of(
        "host", "localhost",
        "port", 1337,
        "username", "user",
        "database", "db",
        "jdbc_url_params", "verifyServerCertificate=false"
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
  void testExtraParams()  {
    JsonNode jdbcConfig = getDestination().toJdbcConfig(buildConfigWithExtraParams());
    String url = jdbcConfig.get("jdbc_url").asText();
    assertEquals("jdbc:mysql://localhost:1337/db?zeroDateTimeBehavior=convertToNull&key1=value1&key2=value2&key3=value3&useSSL=true&requireSSL=true&verifyServerCertificate=false&",
        url);
  }

  @Test
  void testExtraParamsWithSSLParameter()  {
    try {
      JsonNode jdbcConfig = getDestination().toJdbcConfig(buildConfigWithSSLParam());
      String url = jdbcConfig.get("jdbc_url").asText();
      assertEquals("jdbc:mysql://localhost:1337/db?zeroDateTimeBehavior=convertToNull&key1=value1&key2=value2&key3=value3&useSSL=true&requireSSL=true&verifyServerCertificate=false&",
          url);
      //FIXME: why can't I use Test(expected = ?)
      assertTrue(false);
    } catch (RuntimeException e) {
// pass
    }

  }
}
