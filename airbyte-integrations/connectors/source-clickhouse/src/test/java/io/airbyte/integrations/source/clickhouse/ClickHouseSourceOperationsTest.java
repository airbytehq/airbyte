/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.clickhouse;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import java.sql.Array;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.Types;
import java.util.Collections;
import org.junit.jupiter.api.Test;

class ClickHouseSourceOperationsTest {

  private final ClickHouseSourceOperations ops = new ClickHouseSourceOperations();

  /**
   * Verifies that copyToJsonField correctly serializes a multi-element integer array. This is the
   * core regression test for the ClickHouse JDBC v2 ArrayResultSet.next() off-by-one bug (#61419).
   * Without the workaround, the CDK's default putArray path would iterate through the buggy
   * ArrayResultSet and throw "No current row" on the phantom extra iteration.
   */
  @Test
  void testCopyToJsonFieldArrayIntegers() throws Exception {
    final ObjectNode json = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
    final ResultSet rs = mockResultSetWithArray("int_arr", new Object[] {1, 2, 3});

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
    final ResultSet rs = mockResultSetWithArray("single_arr", new Object[] {42});

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
