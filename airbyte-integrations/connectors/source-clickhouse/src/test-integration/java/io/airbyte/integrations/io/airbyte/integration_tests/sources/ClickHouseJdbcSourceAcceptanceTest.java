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
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
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
   * Test case record for parameterized large integer type mapping tests. Each test case defines a
   * ClickHouse type and a list of test values to verify correct mapping.
   */
  record LargeIntegerTestCase(String typeName, List<String> testValues) {}

  /**
   * Provides test cases for large integer type mapping. These types return as JDBCType.OTHER from the
   * driver and are mapped to NUMERIC by ClickHouseSourceOperations.
   */
  static Stream<Arguments> largeIntegerTypeTestCases() {
    return Stream.of(
        Arguments.of(new LargeIntegerTestCase("UInt64", List.of(
            "0", // zero
            "9223372036854775807", // max signed Int64
            "9223372036854775808", // max signed Int64 + 1 (overflow)
            "18446744073709551615" // max UInt64
        ))),
        Arguments.of(new LargeIntegerTestCase("Int128", List.of(
            "0", // zero
            "12345678901234567890", // positive
            "-12345678901234567890", // negative
            "170141183460469231731687303715884105727", // max Int128
            "-170141183460469231731687303715884105728" // min Int128
        ))),
        Arguments.of(new LargeIntegerTestCase("Int256", List.of(
            "0", // zero
            "12345678901234567890123456789012345678901234567890", // positive
            "-12345678901234567890123456789012345678901234567890" // negative
        ))),
        Arguments.of(new LargeIntegerTestCase("UInt128", List.of(
            "0", // zero
            "12345678901234567890", // typical
            "340282366920938463463374607431768211455" // max UInt128
        ))),
        Arguments.of(new LargeIntegerTestCase("UInt256", List.of(
            "0", // zero
            "12345678901234567890123456789012345678901234567890" // typical
        ))));
  }

  @ParameterizedTest(name = "{0}")
  @MethodSource("largeIntegerTypeTestCases")
  public void testLargeIntegerTypeMapping(final LargeIntegerTestCase testCase) throws Exception {
    final String tableName = testCase.typeName().toLowerCase() + "_type_test";
    testdb.with("CREATE TABLE %s (id UInt32, value %s) ENGINE = MergeTree() ORDER BY id",
        tableName, testCase.typeName());

    // Build INSERT statement with all test values
    final List<String> testValues = testCase.testValues();
    final StringBuilder insertValues = new StringBuilder();
    for (int i = 0; i < testValues.size(); i++) {
      if (i > 0) {
        insertValues.append(", ");
      }
      insertValues.append("(").append(i + 1).append(", ").append(testValues.get(i)).append(")");
    }
    testdb.with("INSERT INTO %s VALUES " + insertValues, tableName);

    final List<JsonNode> records = readTable(tableName);
    assertEquals(testValues.size(), records.size());

    // Verify each value
    for (int i = 0; i < testValues.size(); i++) {
      assertValueEquals(records, i + 1, "value", testValues.get(i));
    }
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

  private void assertValueEquals(final List<JsonNode> records,
                                 final int id,
                                 final String column,
                                 final String expected) {
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
