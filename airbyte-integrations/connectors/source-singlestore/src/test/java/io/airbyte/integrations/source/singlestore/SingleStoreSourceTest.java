/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.singlestore;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.commons.json.Jsons;
import org.junit.jupiter.api.Test;

public class SingleStoreSourceTest {

  private static final String EXPECTED_JDBC_ESCAPED_URL = "jdbc:singlestore://localhost:1111/db%2Ffoo?";

  public SingleStoreSource source() {
    return new SingleStoreSource();
  }

  @Test
  void testJdbcUrlWithEscapedDatabaseName() {
    final JsonNode jdbcConfig = source().toDatabaseConfig(buildConfigEscapingNeeded());
    assertNotNull(jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
    assertTrue(
        jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText().startsWith(EXPECTED_JDBC_ESCAPED_URL));
  }

  @Test
  void testJdbcUrlWithSslParameters() {
    final JsonNode jdbcConfig = source().toDatabaseConfig(Jsons.jsonNode(
        ImmutableMap.of(JdbcUtils.HOST_KEY, "localhost", JdbcUtils.PORT_KEY, 3306,
            JdbcUtils.USERNAME_KEY, "user", JdbcUtils.DATABASE_KEY, "db", JdbcUtils.SSL_MODE_KEY,
            Jsons.jsonNode(ImmutableMap.of("mode", "verify-full", "client_key", "test_client_key",
                "client_key_password", "password")))));
    String jdbcUrl = jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText();
    assertEquals(
        "jdbc:singlestore://localhost:3306/db?yearIsDateType=false&tinyInt1isBit=false&_connector_name=Airbyte Source Connector&sslMode=VERIFY_FULL",
        jdbcUrl);
  }

  private JsonNode buildConfigEscapingNeeded() {
    return Jsons.jsonNode(ImmutableMap.of(JdbcUtils.HOST_KEY, "localhost", JdbcUtils.PORT_KEY, 1111,
        JdbcUtils.USERNAME_KEY, "user", JdbcUtils.DATABASE_KEY, "db/foo"));
  }

}
