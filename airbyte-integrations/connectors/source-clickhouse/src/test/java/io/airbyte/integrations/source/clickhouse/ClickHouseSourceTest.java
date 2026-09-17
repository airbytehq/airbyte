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
    return Jsons.jsonNode(ImmutableMap.of(
        JdbcUtils.HOST_KEY, "localhost",
        JdbcUtils.PORT_KEY, 8123,
        JdbcUtils.DATABASE_KEY, "db",
        JdbcUtils.USERNAME_KEY, "username",
        JdbcUtils.PASSWORD_KEY, "verysecure",
        JdbcUtils.SSL_KEY, ssl,
        JdbcUtils.JDBC_URL_PARAMS_KEY, jdbcUrlParams));
  }

}
