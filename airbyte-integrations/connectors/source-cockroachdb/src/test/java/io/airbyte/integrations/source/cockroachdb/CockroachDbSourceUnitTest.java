/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.cockroachdb;

import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.commons.json.Jsons;
import org.junit.jupiter.api.Test;

/**
 * Unit tests for CockroachDbSource that don't require a running CockroachDB instance.
 */
class CockroachDbSourceUnitTest {

  @Test
  void testJdbcUrlWithEncodedDatabaseName() {
    // Test with a database name containing special characters that require URL encoding
    final JsonNode config = Jsons.jsonNode(ImmutableMap.of(
        JdbcUtils.HOST_KEY, "localhost",
        JdbcUtils.PORT_KEY, 26257,
        JdbcUtils.USERNAME_KEY, "user",
        JdbcUtils.DATABASE_KEY, "my database/test",
        JdbcUtils.SSL_KEY, false));

    final JsonNode jdbcConfig = new CockroachDbSource().toDatabaseConfig(config);
    final String jdbcUrl = jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText();

    // Space encodes to + and / encodes to %2F
    assertTrue(jdbcUrl.contains("my+database%2Ftest"),
        "Database name should be URL-encoded in JDBC URL, got: " + jdbcUrl);
  }

  @Test
  void testJdbcUrlWithHyphenatedDatabaseName() {
    // Hyphens are unreserved characters and do not need to be encoded
    final JsonNode config = Jsons.jsonNode(ImmutableMap.of(
        JdbcUtils.HOST_KEY, "localhost",
        JdbcUtils.PORT_KEY, 26257,
        JdbcUtils.USERNAME_KEY, "user",
        JdbcUtils.DATABASE_KEY, "test-db",
        JdbcUtils.SSL_KEY, false));

    final JsonNode jdbcConfig = new CockroachDbSource().toDatabaseConfig(config);
    final String jdbcUrl = jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText();

    // Hyphen should remain as-is (not encoded)
    assertTrue(jdbcUrl.contains("/test-db?"),
        "Hyphenated database name should be preserved in JDBC URL, got: " + jdbcUrl);
  }

  @Test
  void testJdbcUrlWithNormalDatabaseName() {
    final JsonNode config = Jsons.jsonNode(ImmutableMap.of(
        JdbcUtils.HOST_KEY, "localhost",
        JdbcUtils.PORT_KEY, 26257,
        JdbcUtils.USERNAME_KEY, "user",
        JdbcUtils.DATABASE_KEY, "normaldb",
        JdbcUtils.SSL_KEY, false));

    final JsonNode jdbcConfig = new CockroachDbSource().toDatabaseConfig(config);
    final String jdbcUrl = jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText();

    assertTrue(jdbcUrl.contains("/normaldb?"),
        "Normal database name should remain unchanged in JDBC URL, got: " + jdbcUrl);
  }

}

