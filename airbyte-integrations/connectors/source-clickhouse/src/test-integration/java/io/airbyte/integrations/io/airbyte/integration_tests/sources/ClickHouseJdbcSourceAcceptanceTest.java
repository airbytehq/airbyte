/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static io.airbyte.cdk.db.jdbc.JdbcUtils.JDBC_URL_KEY;
import static io.airbyte.integrations.source.clickhouse.ClickHouseSource.SSL_MODE;
import static java.time.temporal.ChronoUnit.SECONDS;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.clickhouse.ClickHouseSource;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.SyncMode;
import java.math.BigInteger;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.testcontainers.clickhouse.ClickHouseContainer;
import org.testcontainers.containers.wait.strategy.Wait;

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
    final ClickHouseContainer db = new ClickHouseContainer("clickhouse/clickhouse-server:24.8")
        .withUsername("default")
        .withPassword("test")
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

  /**
   * Integration tests to validate that ClickHouse large integer types are correctly mapped.
   * These types return as JDBCType.OTHER from the driver and are mapped to NUMERIC by
   * ClickHouseSourceOperations. Each type is tested in a separate table for clarity.
   */

  @Test
  public void testUInt64TypeMapping() throws Exception {
    final String tableName = "uint64_type_test";
    testdb.with("CREATE TABLE %s (id UInt32, value UInt64) ENGINE = MergeTree() ORDER BY id", tableName);

    // Test cases: input value -> expected output
    final String zero = "0";
    final String maxSigned = "9223372036854775807";  // Max signed Int64
    final String overflowSigned = "9223372036854775808";  // Max signed Int64 + 1
    final String maxUnsigned = "18446744073709551615";  // Max UInt64

    testdb.with("INSERT INTO %s VALUES (1, %s), (2, %s), (3, %s), (4, %s)",
        tableName, zero, maxSigned, overflowSigned, maxUnsigned);

    final List<JsonNode> records = readTable(tableName);
    assertEquals(4, records.size());

    assertValueEquals(records, 1, "value", zero);
    assertValueEquals(records, 2, "value", maxSigned);
    assertValueEquals(records, 3, "value", overflowSigned);
    assertValueEquals(records, 4, "value", maxUnsigned);
  }

  @Test
  public void testInt128TypeMapping() throws Exception {
    final String tableName = "int128_type_test";
    testdb.with("CREATE TABLE %s (id UInt32, value Int128) ENGINE = MergeTree() ORDER BY id", tableName);

    // Test cases: input value -> expected output
    final String zero = "0";
    final String positive = "12345678901234567890";
    final String negative = "-12345678901234567890";
    final String maxInt128 = "170141183460469231731687303715884105727";
    final String minInt128 = "-170141183460469231731687303715884105728";

    testdb.with("INSERT INTO %s VALUES (1, %s), (2, %s), (3, %s), (4, %s), (5, %s)",
        tableName, zero, positive, negative, maxInt128, minInt128);

    final List<JsonNode> records = readTable(tableName);
    assertEquals(5, records.size());

    assertValueEquals(records, 1, "value", zero);
    assertValueEquals(records, 2, "value", positive);
    assertValueEquals(records, 3, "value", negative);
    assertValueEquals(records, 4, "value", maxInt128);
    assertValueEquals(records, 5, "value", minInt128);
  }

  @Test
  public void testInt256TypeMapping() throws Exception {
    final String tableName = "int256_type_test";
    testdb.with("CREATE TABLE %s (id UInt32, value Int256) ENGINE = MergeTree() ORDER BY id", tableName);

    // Test cases: input value -> expected output
    final String zero = "0";
    final String positive = "12345678901234567890123456789012345678901234567890";
    final String negative = "-12345678901234567890123456789012345678901234567890";

    testdb.with("INSERT INTO %s VALUES (1, %s), (2, %s), (3, %s)",
        tableName, zero, positive, negative);

    final List<JsonNode> records = readTable(tableName);
    assertEquals(3, records.size());

    assertValueEquals(records, 1, "value", zero);
    assertValueEquals(records, 2, "value", positive);
    assertValueEquals(records, 3, "value", negative);
  }

  @Test
  public void testUInt128TypeMapping() throws Exception {
    final String tableName = "uint128_type_test";
    testdb.with("CREATE TABLE %s (id UInt32, value UInt128) ENGINE = MergeTree() ORDER BY id", tableName);

    // Test cases: input value -> expected output
    final String zero = "0";
    final String typical = "12345678901234567890";
    final String maxUInt128 = "340282366920938463463374607431768211455";

    testdb.with("INSERT INTO %s VALUES (1, %s), (2, %s), (3, %s)",
        tableName, zero, typical, maxUInt128);

    final List<JsonNode> records = readTable(tableName);
    assertEquals(3, records.size());

    assertValueEquals(records, 1, "value", zero);
    assertValueEquals(records, 2, "value", typical);
    assertValueEquals(records, 3, "value", maxUInt128);
  }

  @Test
  public void testUInt256TypeMapping() throws Exception {
    final String tableName = "uint256_type_test";
    testdb.with("CREATE TABLE %s (id UInt32, value UInt256) ENGINE = MergeTree() ORDER BY id", tableName);

    // Test cases: input value -> expected output
    final String zero = "0";
    final String typical = "12345678901234567890123456789012345678901234567890";

    testdb.with("INSERT INTO %s VALUES (1, %s), (2, %s)",
        tableName, zero, typical);

    final List<JsonNode> records = readTable(tableName);
    assertEquals(2, records.size());

    assertValueEquals(records, 1, "value", zero);
    assertValueEquals(records, 2, "value", typical);
  }

  private List<JsonNode> readTable(final String tableName) throws Exception {
    final AirbyteCatalog catalog = source().discover(config());
    final AirbyteStream stream = catalog.getStreams().stream()
        .filter(s -> s.getName().equals(tableName))
        .findFirst()
        .orElseThrow(() -> new AssertionError("Table " + tableName + " not found in catalog"));

    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(
        new AirbyteCatalog().withStreams(List.of(stream)));
    configuredCatalog.getStreams().get(0).setSyncMode(SyncMode.FULL_REFRESH);

    final List<AirbyteMessage> messages = new ArrayList<>();
    try (var iterator = source().read(config(), configuredCatalog, null)) {
      while (iterator.hasNext()) {
        messages.add(iterator.next());
      }
    }

    return messages.stream()
        .filter(m -> m.getType() == AirbyteMessage.Type.RECORD)
        .map(m -> m.getRecord().getData())
        .collect(Collectors.toList());
  }

  private void assertValueEquals(final List<JsonNode> records, final int id,
                                  final String column, final String expected) {
    final JsonNode record = records.stream()
        .filter(r -> r.get("id").asInt() == id)
        .findFirst()
        .orElseThrow(() -> new AssertionError("Record with id " + id + " not found"));

    assertNotNull(record.get(column), column + " should not be null for id " + id);
    final BigInteger expectedValue = new BigInteger(expected);
    final BigInteger actualValue = new BigInteger(record.get(column).asText());
    assertEquals(expectedValue, actualValue,
        String.format("For id=%d, %s: expected %s but got %s", id, column, expected, actualValue));
  }

}
