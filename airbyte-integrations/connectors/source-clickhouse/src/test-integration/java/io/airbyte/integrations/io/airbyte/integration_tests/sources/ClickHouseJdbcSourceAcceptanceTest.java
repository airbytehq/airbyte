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
   * Integration test to validate that ClickHouse large integer types (UInt64, Int128, Int256,
   * UInt128, UInt256) are correctly mapped and can be read with proper values. These types return as
   * JDBCType.OTHER from the driver and are mapped to NUMERIC by ClickHouseSourceOperations.
   */
  @Test
  public void testLargeIntegerTypeMapping() throws Exception {
    // Create a table with all large integer types that return as JDBCType.OTHER
    final String tableName = "large_integer_types_test";
    testdb.with("CREATE TABLE %s ("
        + "id UInt32, "
        + "uint64_col UInt64, "
        + "int128_col Int128, "
        + "int256_col Int256, "
        + "uint128_col UInt128, "
        + "uint256_col UInt256"
        + ") ENGINE = MergeTree() ORDER BY id", tableName);

    // Insert test values including edge cases (max values, typical values, zero)
    // UInt64 max: 18446744073709551615
    // Int128/Int256/UInt128/UInt256 can hold much larger values
    testdb.with("INSERT INTO %s VALUES "
        + "(1, 18446744073709551615, 170141183460469231731687303715884105727, 0, 0, 0), "
        + "(2, 0, -170141183460469231731687303715884105728, 12345678901234567890, 340282366920938463463374607431768211455, 0), "
        + "(3, 9223372036854775808, 0, 0, 0, 115792089237316195423570985008687907853269984665640564039457584007913129639935)",
        tableName);

    // Discover the catalog and verify the table is found
    final AirbyteCatalog catalog = source().discover(config());
    final AirbyteStream stream = catalog.getStreams().stream()
        .filter(s -> s.getName().equals(tableName))
        .findFirst()
        .orElseThrow(() -> new AssertionError("Table " + tableName + " not found in catalog"));

    // Configure catalog for full refresh read
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(
        new AirbyteCatalog().withStreams(List.of(stream)));
    configuredCatalog.getStreams().get(0).setSyncMode(SyncMode.FULL_REFRESH);

    // Read all records
    final List<AirbyteMessage> messages = new ArrayList<>();
    try (var iterator = source().read(config(), configuredCatalog, null)) {
      while (iterator.hasNext()) {
        messages.add(iterator.next());
      }
    }

    // Filter to just record messages
    final List<JsonNode> records = messages.stream()
        .filter(m -> m.getType() == AirbyteMessage.Type.RECORD)
        .map(m -> m.getRecord().getData())
        .collect(Collectors.toList());

    // Verify we got all 3 rows
    assertEquals(3, records.size(), "Expected 3 records from large_integer_types_test table");

    // Verify the values are correctly read (they should be represented as numbers/strings)
    // The exact representation depends on how the CDK handles NUMERIC types
    for (JsonNode record : records) {
      assertNotNull(record.get("uint64_col"), "uint64_col should not be null");
      assertNotNull(record.get("int128_col"), "int128_col should not be null");
      assertNotNull(record.get("int256_col"), "int256_col should not be null");
      assertNotNull(record.get("uint128_col"), "uint128_col should not be null");
      assertNotNull(record.get("uint256_col"), "uint256_col should not be null");
    }

    // Verify specific values for the first row (UInt64 max value)
    final JsonNode row1 = records.stream()
        .filter(r -> r.get("id").asInt() == 1)
        .findFirst()
        .orElseThrow();
    // UInt64 max value should be readable
    final BigInteger uint64Max = new BigInteger("18446744073709551615");
    final BigInteger actualUint64 = new BigInteger(row1.get("uint64_col").asText());
    assertEquals(uint64Max, actualUint64, "UInt64 max value should be correctly read");
  }

}
