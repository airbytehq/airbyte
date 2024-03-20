/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static io.airbyte.cdk.db.jdbc.JdbcUtils.JDBC_URL_KEY;
import static io.airbyte.integrations.source.clickhouse.ClickHouseSource.SSL_MODE;
import static java.time.temporal.ChronoUnit.SECONDS;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.clickhouse.ClickHouseSource;
import java.time.Duration;
import java.util.List;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.testcontainers.clickhouse.ClickHouseContainer;
import org.testcontainers.containers.wait.strategy.Wait;

@Disabled
public class ClickHouseJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest<ClickHouseSource, ClickHouseTestDatabase> {

  @BeforeAll
  static void init() {
    CREATE_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "CREATE TABLE %s (%s Array(UInt32)) ENGINE = MergeTree ORDER BY tuple();";
    INSERT_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "INSERT INTO %s VALUES([12, 13, 0, 1]);";
    CREATE_TABLE_WITH_NULLABLE_CURSOR_TYPE_QUERY = "CREATE TABLE %s (%s Nullable(VARCHAR(20))) ENGINE = MergeTree ORDER BY tuple();";
    INSERT_TABLE_WITH_NULLABLE_CURSOR_TYPE_QUERY = "INSERT INTO %s VALUES('Hello world :)');";
  }

  @Override
  public boolean supportsSchemas() {
    return false;
  }

  @Override
  protected JsonNode config() {
    return Jsons.clone(testdb.configBuilder().build());
  }

  @Override
  protected ClickHouseTestDatabase createTestDatabase() {
    final ClickHouseContainer db = new ClickHouseContainer("clickhouse/clickhouse-server:22.5")
        .waitingFor(Wait.forHttp("/ping").forPort(8123)
            .forStatusCode(200).withStartupTimeout(Duration.of(60, SECONDS)));
    db.start();
    return new ClickHouseTestDatabase(db).initialized();
  }

  @Override
  public String createTableQuery(final String tableName, final String columnClause, final String primaryKeyClause) {
    // ClickHouse requires Engine to be mentioned as part of create table query.
    // Refer : https://clickhouse.tech/docs/en/engines/table-engines/ for more information
    return String.format("CREATE TABLE %s(%s) %s",
        tableName, columnClause, primaryKeyClause.equals("") ? "Engine = TinyLog"
            : "ENGINE = MergeTree() ORDER BY " + primaryKeyClause + " PRIMARY KEY "
                + primaryKeyClause);
  }

  @Override
  public String primaryKeyClause(final List<String> columns) {
    if (columns.isEmpty()) {
      return "";
    }

    final StringBuilder clause = new StringBuilder();
    clause.append("(");
    for (int i = 0; i < columns.size(); i++) {
      clause.append(columns.get(i));
      if (i != (columns.size() - 1)) {
        clause.append(",");
      }
    }
    clause.append(")");
    return clause.toString();
  }

  @Override
  protected ClickHouseSource source() {
    return new ClickHouseSource();
  }

  @Test
  public void testEmptyExtraParamsWithSsl() {
    final String extraParam = "";
    JsonNode config = buildConfigWithExtraJdbcParameters(extraParam, true);
    final JsonNode jdbcConfig = new ClickHouseSource().toDatabaseConfig(config);
    JsonNode jdbcUrlNode = jdbcConfig.get(JDBC_URL_KEY);
    assertNotNull(jdbcUrlNode);
    String actualJdbcUrl = jdbcUrlNode.asText();
    assertTrue(actualJdbcUrl.endsWith("?" + SSL_MODE));
  }

  @Test
  public void testEmptyExtraParamsWithoutSsl() {
    final String extraParam = "";
    JsonNode config = buildConfigWithExtraJdbcParameters(extraParam, false);
    final JsonNode jdbcConfig = new ClickHouseSource().toDatabaseConfig(config);
    JsonNode jdbcUrlNode = jdbcConfig.get(JDBC_URL_KEY);
    assertNotNull(jdbcUrlNode);
    String actualJdbcUrl = jdbcUrlNode.asText();
    assertTrue(actualJdbcUrl.endsWith(config.get("database").asText()));
  }

  @Test
  public void testExtraParamsWithSsl() {
    final String extraParam = "key1=value1&key2=value2&key3=value3";
    JsonNode config = buildConfigWithExtraJdbcParameters(extraParam, true);
    final JsonNode jdbcConfig = new ClickHouseSource().toDatabaseConfig(config);
    JsonNode jdbcUrlNode = jdbcConfig.get(JDBC_URL_KEY);
    assertNotNull(jdbcUrlNode);
    String actualJdbcUrl = jdbcUrlNode.asText();
    assertTrue(actualJdbcUrl.endsWith(getFullExpectedValue(extraParam, SSL_MODE)));
  }

  @Test
  public void testExtraParamsWithoutSsl() {
    final String extraParam = "key1=value1&key2=value2&key3=value3";
    JsonNode config = buildConfigWithExtraJdbcParameters(extraParam, false);
    final JsonNode jdbcConfig = new ClickHouseSource().toDatabaseConfig(config);
    JsonNode jdbcUrlNode = jdbcConfig.get(JDBC_URL_KEY);
    assertNotNull(jdbcUrlNode);
    String actualJdbcUrl = jdbcUrlNode.asText();
    assertTrue(actualJdbcUrl.endsWith("?" + extraParam));
  }

  private String getFullExpectedValue(String extraParam, String sslMode) {
    StringBuilder expected = new StringBuilder();
    return expected.append("?").append(sslMode).append("&").append(extraParam).toString();
  }

  private JsonNode buildConfigWithExtraJdbcParameters(String extraParam, boolean isSsl) {

    return Jsons.jsonNode(com.google.common.collect.ImmutableMap.of(
        "host", "localhost",
        "port", 8123,
        "database", "db",
        "username", "username",
        "password", "verysecure",
        "jdbc_url_params", extraParam,
        "ssl", isSsl));
  }

}
