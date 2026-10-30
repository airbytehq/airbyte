/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.redshift;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.jdbc.JdbcConstants;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.JsonSchemaType;
import java.lang.reflect.Proxy;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

class RedshiftSourceOperationsTypeTest {

  private final RedshiftSourceOperations operations = new RedshiftSourceOperations();

  // Column metadata as returned by the Redshift JDBC driver's DatabaseMetaData.getColumns().
  private static JsonNode columnMetadata(final JDBCType dataType, final String typeName) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcConstants.INTERNAL_SCHEMA_NAME, "public")
        .put(JdbcConstants.INTERNAL_TABLE_NAME, "temporal_types")
        .put(JdbcConstants.INTERNAL_COLUMN_NAME, "col")
        .put(JdbcConstants.INTERNAL_COLUMN_TYPE, String.valueOf(dataType.getVendorTypeNumber()))
        .put(JdbcConstants.INTERNAL_COLUMN_TYPE_NAME, typeName)
        .build());
  }

  private JsonSchemaType discoveredType(final JDBCType dataType, final String typeName) {
    return operations.getAirbyteType(operations.getDatabaseFieldType(columnMetadata(dataType, typeName)));
  }

  @Test
  void testTemporalColumnsDiscoveredWithFormatHints() {
    assertEquals(JsonSchemaType.STRING_DATE, discoveredType(JDBCType.DATE, "date"));
    assertEquals(JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE, discoveredType(JDBCType.TIMESTAMP, "timestamp"));
    // The driver reports timestamptz as TIMESTAMP; it must still be discovered as a timezone-aware
    // type.
    assertEquals(JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE, discoveredType(JDBCType.TIMESTAMP, "timestamptz"));
  }

  @Test
  void testTimestamptzRemappedToTimestampWithTimezone() {
    assertEquals(JDBCType.TIMESTAMP_WITH_TIMEZONE, operations.getDatabaseFieldType(columnMetadata(JDBCType.TIMESTAMP, "timestamptz")));
    assertEquals(JDBCType.TIMESTAMP, operations.getDatabaseFieldType(columnMetadata(JDBCType.TIMESTAMP, "timestamp")));
    assertTrue(operations.isCursorType(JDBCType.TIMESTAMP_WITH_TIMEZONE));
  }

  @Test
  void testNonTemporalTypesUnchanged() {
    assertEquals(JsonSchemaType.INTEGER, discoveredType(JDBCType.INTEGER, "int4"));
    assertEquals(JsonSchemaType.INTEGER, discoveredType(JDBCType.BIGINT, "int8"));
    assertEquals(JsonSchemaType.NUMBER, discoveredType(JDBCType.NUMERIC, "numeric"));
    assertEquals(JsonSchemaType.NUMBER, discoveredType(JDBCType.DOUBLE, "float8"));
    assertEquals(JsonSchemaType.BOOLEAN, discoveredType(JDBCType.BIT, "bool"));
    assertEquals(JsonSchemaType.STRING, discoveredType(JDBCType.VARCHAR, "varchar"));
    // time and timetz are reported as OTHER by the driver and stay plain strings.
    assertEquals(JsonSchemaType.STRING, discoveredType(JDBCType.OTHER, "time"));
    assertEquals(JsonSchemaType.STRING, discoveredType(JDBCType.OTHER, "timetz"));
  }

  @Test
  void testTimestamptzCursorBoundAsInstant() throws Exception {
    final AtomicReference<Object> bound = new AtomicReference<>();
    final PreparedStatement statement = (PreparedStatement) Proxy.newProxyInstance(
        PreparedStatement.class.getClassLoader(),
        new Class<?>[] {PreparedStatement.class},
        (proxy, method, args) -> {
          if (method.getName().startsWith("set")) {
            bound.set(args[1]);
          }
          return null;
        });

    operations.setCursorField(statement, 1, JDBCType.TIMESTAMP_WITH_TIMEZONE, "2024-01-15T03:45:30.123456-08:00");

    assertEquals(Timestamp.from(Instant.parse("2024-01-15T11:45:30.123456Z")), bound.get());
  }

}
