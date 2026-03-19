/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.clickhouse;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.protocol.models.JsonSchemaType;
import java.sql.JDBCType;
import org.junit.jupiter.api.Test;

class ClickHouseSourceOperationsTest {

  private final ClickHouseSourceOperations operations = new ClickHouseSourceOperations();

  @Test
  void testTemporalTypesWithFormatHints() {
    assertEquals(JsonSchemaType.STRING_DATE, operations.getAirbyteType(JDBCType.DATE));
    assertEquals(JsonSchemaType.STRING_TIME_WITHOUT_TIMEZONE, operations.getAirbyteType(JDBCType.TIME));
    assertEquals(JsonSchemaType.STRING_TIME_WITH_TIMEZONE, operations.getAirbyteType(JDBCType.TIME_WITH_TIMEZONE));
    assertEquals(JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE, operations.getAirbyteType(JDBCType.TIMESTAMP));
    assertEquals(JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE, operations.getAirbyteType(JDBCType.TIMESTAMP_WITH_TIMEZONE));
  }

  @Test
  void testNumericTypes() {
    assertEquals(JsonSchemaType.BOOLEAN, operations.getAirbyteType(JDBCType.BOOLEAN));
    assertEquals(JsonSchemaType.BOOLEAN, operations.getAirbyteType(JDBCType.BIT));
    assertEquals(JsonSchemaType.INTEGER, operations.getAirbyteType(JDBCType.INTEGER));
    assertEquals(JsonSchemaType.INTEGER, operations.getAirbyteType(JDBCType.BIGINT));
    assertEquals(JsonSchemaType.INTEGER, operations.getAirbyteType(JDBCType.SMALLINT));
    assertEquals(JsonSchemaType.INTEGER, operations.getAirbyteType(JDBCType.TINYINT));
    assertEquals(JsonSchemaType.NUMBER, operations.getAirbyteType(JDBCType.FLOAT));
    assertEquals(JsonSchemaType.NUMBER, operations.getAirbyteType(JDBCType.DOUBLE));
    assertEquals(JsonSchemaType.NUMBER, operations.getAirbyteType(JDBCType.DECIMAL));
    assertEquals(JsonSchemaType.NUMBER, operations.getAirbyteType(JDBCType.NUMERIC));
    assertEquals(JsonSchemaType.NUMBER, operations.getAirbyteType(JDBCType.REAL));
  }

  @Test
  void testOtherTypes() {
    assertEquals(JsonSchemaType.STRING, operations.getAirbyteType(JDBCType.VARCHAR));
    assertEquals(JsonSchemaType.STRING_BASE_64, operations.getAirbyteType(JDBCType.BLOB));
    assertEquals(JsonSchemaType.STRING_BASE_64, operations.getAirbyteType(JDBCType.BINARY));
    assertEquals(JsonSchemaType.ARRAY, operations.getAirbyteType(JDBCType.ARRAY));
    assertEquals(JsonSchemaType.STRING, operations.getAirbyteType(JDBCType.OTHER));
  }

  @Test
  void testCursorTypes() {
    assertTrue(operations.isCursorType(JDBCType.TIMESTAMP));
    assertTrue(operations.isCursorType(JDBCType.DATE));
    assertTrue(operations.isCursorType(JDBCType.INTEGER));
    assertTrue(operations.isCursorType(JDBCType.BIGINT));
    assertTrue(operations.isCursorType(JDBCType.VARCHAR));
    assertFalse(operations.isCursorType(JDBCType.BLOB));
    assertFalse(operations.isCursorType(JDBCType.ARRAY));
  }

}
