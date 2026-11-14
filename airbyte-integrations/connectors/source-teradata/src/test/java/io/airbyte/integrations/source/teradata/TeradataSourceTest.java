/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.teradata;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.commons.json.Jsons;
import java.util.Map;
import org.junit.jupiter.api.Test;

class TeradataSourceTest {

  private final TeradataSource source = new TeradataSource();

  @Test
  void jdbcUrlWithPortUsesDbsPortParameter() {
    final JsonNode config = Jsons.jsonNode(Map.of(
        JdbcUtils.HOST_KEY, "td.example.com",
        JdbcUtils.PORT_KEY, 1025,
        JdbcUtils.DATABASE_KEY, "db",
        JdbcUtils.USERNAME_KEY, "user"));

    final JsonNode jdbcConfig = source.toDatabaseConfig(config);

    assertEquals("jdbc:teradata://td.example.com/DBS_PORT=1025", jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
    assertEquals("db", jdbcConfig.get(JdbcUtils.SCHEMA_KEY).asText());
  }

  @Test
  void jdbcUrlWithoutPort() {
    final JsonNode config = Jsons.jsonNode(Map.of(
        JdbcUtils.HOST_KEY, "td.example.com",
        JdbcUtils.DATABASE_KEY, "db",
        JdbcUtils.USERNAME_KEY, "user"));

    assertEquals("jdbc:teradata://td.example.com/", source.toDatabaseConfig(config).get(JdbcUtils.JDBC_URL_KEY).asText());
  }

}
