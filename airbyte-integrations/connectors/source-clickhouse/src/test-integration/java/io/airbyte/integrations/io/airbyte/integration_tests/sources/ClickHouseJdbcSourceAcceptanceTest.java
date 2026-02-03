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
   * ClickHouse type with min, max, and typical values. The test will automatically also verify null
   * and zero for each type.
   */
  record LargeIntegerTestCase(String typeName, String min, String max, String typical) {}

  /**
   * Provides test cases for large integer type mapping. These types return as JDBCType.OTHER from the
   * driver and are mapped to NUMERIC by ClickHouseSourceOperations.
   */
  static Stream<Arguments> largeIntegerTypeTestCases() {
    return Stream.of(
        // UInt64: unsigned 64-bit, min=0 (tested as zero), max=2^64-1
        Arguments.of(new LargeIntegerTestCase("UInt64",
            null, // min is 0, covered by zero test
            "18446744073709551615", // max UInt64
            "9223372036854775808")), // typical: max signed Int64 + 1
        // Int128: signed 128-bit
        Arguments.of(new LargeIntegerTestCase("Int128",
            "-170141183460469231731687303715884105728", // min Int128
            "170141183460469231731687303715884105727", // max Int128
            "12345678901234567890")), // typical
        // Int256: signed 256-bit
        Arguments.of(new LargeIntegerTestCase("Int256",
            "-57896044618658097711785492504343953926634992332820282019728792003956564819968", // min
            "57896044618658097711785492504343953926634992332820282019728792003956564819967", // max
            "12345678901234567890123456789012345678901234567890")), // typical
        // UInt128: unsigned 128-bit, min=0 (tested as zero)
        Arguments.of(new LargeIntegerTestCase("UInt128",
            null, // min is 0, covered by zero test
            "340282366920938463463374607431768211455", // max UInt128
            "12345678901234567890")), // typical
        // UInt256: unsigned 256-bit, min=0 (tested as zero)
        Arguments.of(new LargeIntegerTestCase("UInt256",
            null, // min is 0, covered by zero test
            "115792089237316195423570985008687907853269984665640564039457584007913129639935", // max
            "12345678901234567890123456789012345678901234567890"))); // typical
  }

  @ParameterizedTest(name = "{0}")
  @MethodSource("largeIntegerTypeTestCases")
  public void testLargeIntegerTypeMapping(final LargeIntegerTestCase testCase) throws Exception {
    final String tableName = testCase.typeName().toLowerCase() + "_type_test";
    // Use Nullable type to test null values
    testdb.with("CREATE TABLE %s (id UInt32, value Nullable(%s)) ENGINE = MergeTree() ORDER BY id",
        tableName, testCase.typeName());

    // Build test values: null, zero, min (if not null), max, typical
    final List<String> testValues = new ArrayList<>();
    testValues.add(null); // null value
    testValues.add("0"); // zero
    if (testCase.min() != null) {
      testValues.add(testCase.min());
    }
    testValues.add(testCase.max());
    testValues.add(testCase.typical());

    // Build INSERT statement
    final StringBuilder insertValues = new StringBuilder();
    for (int i = 0; i < testValues.size(); i++) {
      if (i > 0) {
        insertValues.append(", ");
      }
      final String value = testValues.get(i);
      insertValues.append("(").append(i + 1).append(", ")
          .append(value == null ? "NULL" : value).append(")");
    }
    testdb.with("INSERT INTO %s VALUES " + insertValues, tableName);

    final List<JsonNode> records = readTable(tableName);
    assertEquals(testValues.size(), records.size());

    // Verify each value
    for (int i = 0; i < testValues.size(); i++) {
      final String expected = testValues.get(i);
      if (expected == null) {
        assertNullValue(records, i + 1, "value");
      } else {
        assertValueEquals(records, i + 1, "value", expected);
      }
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

  private void assertNullValue(final List<JsonNode> records, final int id, final String column) {
    final JsonNode record = records.stream()
        .filter(r -> r.get("id").asInt() == id)
        .findFirst()
        .orElseThrow(() -> new AssertionError("Record with id " + id + " not found"));

    final JsonNode value = record.get(column);
    // Field can be either missing (Java null) or present with null value (JsonNode.isNull())
    assertTrue(value == null || value.isNull(),
        String.format("For id=%d, %s: expected null but got %s", id, column, value));
  }

}
