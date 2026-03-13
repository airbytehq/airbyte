/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.clickhouse;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.clickhouse.data.ClickHouseColumn;
import com.clickhouse.jdbc.types.ArrayResultSet;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import java.sql.Array;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.sql.Types;
import java.util.Collections;
import org.junit.jupiter.api.Test;

class ClickHouseSourceOperationsTest {

  private final ClickHouseSourceOperations ops = new ClickHouseSourceOperations();

  /**
   * Proves the off-by-one bug exists in the real ClickHouse JDBC v2 driver's ArrayResultSet.next().
   * For an N-element array, next() returns true N+1 times instead of N, and the extra iteration
   * throws "No current row" when any column is read. This test uses the real driver class directly,
   * not mocks.
   */
  @Test
  void testDriverArrayResultSetBugExists() throws SQLException {
    final Integer[] data = {10, 20, 30};
    final ArrayResultSet buggyRs =
        new ArrayResultSet(data, ClickHouseColumn.parse("v Array(Int32)").get(0));

    // The standard JDBC iteration pattern triggers the bug:
    // next() returns true a 4th time for a 3-element array, then getString() throws.
    int count = 0;
    while (buggyRs.next()) {
      count++;
      if (count > data.length) {
        // On the phantom extra iteration, reading any column throws "No current row"
        assertThrows(SQLException.class, () -> buggyRs.getString(2),
            "Expected 'No current row' on phantom iteration #" + count);
        break;
      }
    }
    assertTrue(count > data.length,
        "next() should have returned true more than " + data.length + " times (bug proof)");
  }

  /**
   * Verifies that copyToJsonField correctly serializes a multi-element integer array by using
   * Array.getArray() instead of Array.getResultSet(), thus bypassing the driver bug. The mock
   * provides both getArray() (returns Object[]) and getResultSet() (returns the real buggy
   * ArrayResultSet). If the workaround were removed and the parent's putArray were used instead, this
   * test would fail with "No current row".
   */
  @Test
  void testCopyToJsonFieldArrayIntegers() throws Exception {
    final ObjectNode json = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
    final ResultSet rs = mockResultSetWithArrayAndBuggyResultSet("int_arr",
        new Object[] {1, 2, 3}, new Integer[] {1, 2, 3});

    ops.copyToJsonField(rs, 1, json);

    final JsonNode arrayNode = json.get("int_arr");
    assertTrue(arrayNode.isArray());
    assertEquals(3, arrayNode.size());
    assertEquals("1", arrayNode.get(0).asText());
    assertEquals("2", arrayNode.get(1).asText());
    assertEquals("3", arrayNode.get(2).asText());
  }

  /**
   * Verifies that a single-element array is handled correctly.
   */
  @Test
  void testCopyToJsonFieldArraySingleElement() throws Exception {
    final ObjectNode json = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
    final ResultSet rs = mockResultSetWithArrayAndBuggyResultSet("single_arr",
        new Object[] {42}, new Integer[] {42});

    ops.copyToJsonField(rs, 1, json);

    final JsonNode arrayNode = json.get("single_arr");
    assertTrue(arrayNode.isArray());
    assertEquals(1, arrayNode.size());
    assertEquals("42", arrayNode.get(0).asText());
  }

  /**
   * Verifies that an empty array produces an empty JSON array.
   */
  @Test
  void testCopyToJsonFieldArrayEmpty() throws Exception {
    final ObjectNode json = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
    final ResultSet rs = mockResultSetWithArray("empty_arr", new Object[] {});

    ops.copyToJsonField(rs, 1, json);

    final JsonNode arrayNode = json.get("empty_arr");
    assertTrue(arrayNode.isArray());
    assertEquals(0, arrayNode.size());
  }

  /**
   * Verifies that null elements within an array are preserved as JSON nulls.
   */
  @Test
  void testCopyToJsonFieldArrayWithNulls() throws Exception {
    final ObjectNode json = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
    final ResultSet rs = mockResultSetWithArray("nullable_arr", new Object[] {"a", null, "c"});

    ops.copyToJsonField(rs, 1, json);

    final JsonNode arrayNode = json.get("nullable_arr");
    assertTrue(arrayNode.isArray());
    assertEquals(3, arrayNode.size());
    assertEquals("a", arrayNode.get(0).asText());
    assertTrue(arrayNode.get(1).isNull());
    assertEquals("c", arrayNode.get(2).asText());
  }

  /**
   * Verifies that string arrays are serialized correctly.
   */
  @Test
  void testCopyToJsonFieldArrayStrings() throws Exception {
    final ObjectNode json = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
    final ResultSet rs = mockResultSetWithArray("str_arr", new Object[] {"hello", "world"});

    ops.copyToJsonField(rs, 1, json);

    final JsonNode arrayNode = json.get("str_arr");
    assertTrue(arrayNode.isArray());
    assertEquals(2, arrayNode.size());
    assertEquals("hello", arrayNode.get(0).asText());
    assertEquals("world", arrayNode.get(1).asText());
  }

  /**
   * Creates a mock ResultSet where the Array mock provides both getArray() (Object[] for the
   * workaround) and getResultSet() (real buggy ArrayResultSet). If the copyToJsonField workaround
   * were removed, the parent CDK's putArray would call getResultSet() and hit the off-by-one bug.
   */
  private ResultSet mockResultSetWithArrayAndBuggyResultSet(final String columnName,
                                                            final Object[] elements,
                                                            final Integer[] typedElements)
      throws Exception {
    final ResultSetMetaData metadata = mock(ResultSetMetaData.class);
    when(metadata.getColumnType(1)).thenReturn(Types.ARRAY);
    when(metadata.getColumnName(1)).thenReturn(columnName);

    // Wire up the real buggy ArrayResultSet so getResultSet() returns the driver's broken impl
    final ArrayResultSet buggyResultSet =
        new ArrayResultSet(typedElements, ClickHouseColumn.parse("v Array(Int32)").get(0));

    final Array sqlArray = mock(Array.class);
    when(sqlArray.getArray()).thenReturn(elements);
    when(sqlArray.getResultSet()).thenReturn(buggyResultSet);

    final ResultSet rs = mock(ResultSet.class);
    when(rs.getMetaData()).thenReturn(metadata);
    when(rs.getArray(1)).thenReturn(sqlArray);

    return rs;
  }

  /**
   * Creates a simple mock ResultSet with an Array column (getArray() only, no getResultSet()).
   */
  private ResultSet mockResultSetWithArray(final String columnName, final Object[] elements)
      throws Exception {
    final ResultSetMetaData metadata = mock(ResultSetMetaData.class);
    when(metadata.getColumnType(1)).thenReturn(Types.ARRAY);
    when(metadata.getColumnName(1)).thenReturn(columnName);

    final Array sqlArray = mock(Array.class);
    when(sqlArray.getArray()).thenReturn(elements);

    final ResultSet rs = mock(ResultSet.class);
    when(rs.getMetaData()).thenReturn(metadata);
    when(rs.getArray(1)).thenReturn(sqlArray);

    return rs;
  }

}
