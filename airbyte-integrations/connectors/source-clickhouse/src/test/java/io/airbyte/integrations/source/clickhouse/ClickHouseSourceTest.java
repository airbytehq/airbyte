/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.clickhouse;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.commons.json.Jsons;
import org.junit.jupiter.api.Test;

class ClickHouseSourceTest {

  @Test
  void usesHttpsWithoutLegacySslModeWhenSslIsEnabled() {
    final JsonNode config = baseConfig(true);

    final String jdbcUrl = new ClickHouseSource().toDatabaseConfig(config).get(JdbcUtils.JDBC_URL_KEY).asText();

    assertEquals("jdbc:clickhouse:https://localhost:8123/db", jdbcUrl);
    assertFalse(jdbcUrl.contains("sslmode"));
  }

  @Test
  void appendsJdbcUrlParamsWithoutLegacySslModeWhenSslIsEnabled() {
    final JsonNode config = baseConfig(true, "key1=value1&key2=value2");

    final String jdbcUrl = new ClickHouseSource().toDatabaseConfig(config).get(JdbcUtils.JDBC_URL_KEY).asText();

    assertEquals("jdbc:clickhouse:https://localhost:8123/db?key1=value1&key2=value2", jdbcUrl);
    assertFalse(jdbcUrl.contains("sslmode"));
  }

  @Test
  void filtersLegacySslModeWithSupportedParameter() {
    final JsonNode config = baseConfig(true, "ssl=true&sslmode=STRICT");

    final String jdbcUrl = new ClickHouseSource().toDatabaseConfig(config).get(JdbcUtils.JDBC_URL_KEY).asText();

    assertEquals("jdbc:clickhouse:https://localhost:8123/db?ssl=true", jdbcUrl);
    assertFalse(jdbcUrl.contains("sslmode"));
  }

  @Test
  void omitsJdbcUrlWhenOnlyLegacySslModeIsProvided() {
    final JsonNode config = baseConfig(true, "sslmode=none");

    final String jdbcUrl = new ClickHouseSource().toDatabaseConfig(config).get(JdbcUtils.JDBC_URL_KEY).asText();

    assertEquals("jdbc:clickhouse:https://localhost:8123/db", jdbcUrl);
  }

  @Test
  void filtersLegacySslModeCaseInsensitively() {
    final JsonNode config = baseConfig(true, "SSLMODE=STRICT&socket_timeout=30000");

    final String jdbcUrl = new ClickHouseSource().toDatabaseConfig(config).get(JdbcUtils.JDBC_URL_KEY).asText();

    assertEquals("jdbc:clickhouse:https://localhost:8123/db?socket_timeout=30000", jdbcUrl);
  }

  @Test
  void usesHttpWhenSslIsDisabled() {
    final JsonNode config = baseConfig(false);

    final String jdbcUrl = new ClickHouseSource().toDatabaseConfig(config).get(JdbcUtils.JDBC_URL_KEY).asText();

    assertEquals("jdbc:clickhouse:http://localhost:8123/db", jdbcUrl);
    assertFalse(jdbcUrl.contains("sslmode"));
  }

  @Test
  void assumesHttpsWhenSslIsAbsent() {
    final JsonNode config = Jsons.jsonNode(ImmutableMap.of(
        JdbcUtils.HOST_KEY, "localhost",
        JdbcUtils.PORT_KEY, 8123,
        JdbcUtils.DATABASE_KEY, "db",
        JdbcUtils.USERNAME_KEY, "username",
        JdbcUtils.PASSWORD_KEY, "verysecure"));

    final String jdbcUrl = new ClickHouseSource().toDatabaseConfig(config).get(JdbcUtils.JDBC_URL_KEY).asText();

    assertEquals("jdbc:clickhouse:https://localhost:8123/db", jdbcUrl);
    assertFalse(jdbcUrl.contains("sslmode"));
  }

  private JsonNode baseConfig(final boolean ssl) {
    return baseConfig(ssl, "");
  }

  private JsonNode baseConfig(final boolean ssl, final String jdbcUrlParams) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, "localhost")
        .put(JdbcUtils.PORT_KEY, 8123)
        .put(JdbcUtils.DATABASE_KEY, "db")
        .put(JdbcUtils.USERNAME_KEY, "username")
        .put(JdbcUtils.PASSWORD_KEY, "verysecure")
        .put(JdbcUtils.SSL_KEY, ssl)
        .put(JdbcUtils.JDBC_URL_PARAMS_KEY, jdbcUrlParams)
        .build());
  }

}
