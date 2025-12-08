/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.nebulagraph;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("StatementBuilder")
class StatementBuilderTest {

  @Test
  void escapingQAndQs() {
    StatementBuilder sb = new StatementBuilder();

    // q: backtick escaping
    assertEquals("`a``b`", sb.q("a`b"));

    // qs: string literal escaping and NULL handling
    String s = "a\"b\\c\n\r\t"; // a"b\c\n\r\t
    String expected = "\"a\\\"b\\\\c\\n\\r\\t\""; // "a\"b\\c\n\r\t"
    assertEquals(expected, sb.qs(s));
    assertEquals("NULL", sb.qs(null));
  }

  @Test
  void formatVidAndValuesFragment() {
    StatementBuilder sb = new StatementBuilder();
    List<Object> values = Arrays.asList("str\"q", 1L, true, null);
    String fragment = sb.formatVidAndValues("vid-001", values);
    // Expect: "vid-001":("str\"q",1,true,NULL)
    assertEquals("\"vid-001\":(\"str\\\"q\",1,true,NULL)", fragment);
  }

  @Test
  void formatEdgeEndpointsAndValuesFragment() {
    StatementBuilder sb = new StatementBuilder();
    List<Object> values = List.of("json", 123, false);
    String fragment = sb.formatEdgeEndpointsAndValues("src-1", "dst-2", 5L, values);
    // Expect: "src-1"->"dst-2"@5:("json",123,false)
    assertEquals("\"src-1\"->\"dst-2\"@5:(\"json\",123,false)", fragment);
  }

  @Test
  void buildInsertVertexValues() {
    StatementBuilder sb = new StatementBuilder();
    List<String> cols = List.of("_airbyte_data", "_airbyte_emitted_at");

    List<String> tuples = new ArrayList<>();
    tuples.add(sb.formatVidAndValues("v1", List.of("{\\\"k\\\":1}", 111L)));
    tuples.add(sb.formatVidAndValues("v2", List.of("{\\\"k\\\":2}", 222L)));

    String sql = sb.buildInsertVertexValues("users", cols, tuples);
    String expected = "INSERT VERTEX `users` (`_airbyte_data`,`_airbyte_emitted_at`)\n" +
        "VALUES\n" +
        "\"v1\":(\"{\\\\\\\"k\\\\\\\":1}\",111),\n  " +
        "\"v2\":(\"{\\\\\\\"k\\\\\\\":2}\",222);";

    assertEquals(expected, sql);
  }

  @Test
  void buildUpsertVertexContainsExpectedSet() {
    StatementBuilder sb = new StatementBuilder();
    List<String> cols = List.of("_airbyte_data", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_loaded_at");
    List<Object> vals = List.of("json", "ab1", 1L, 2L);

    String sql = sb.buildUpsertVertex("users", "v1", cols, vals);

    assertTrue(sql.startsWith("UPSERT VERTEX ON `users` \"v1\"\nSET "));
    assertTrue(sql.contains("`_airbyte_data`=\"json\""));
    assertTrue(sql.contains("`_airbyte_ab_id`=\"ab1\""));
    assertTrue(sql.contains("`_airbyte_emitted_at`=1"));
    assertTrue(sql.contains("`_airbyte_loaded_at`=2"));
    assertTrue(sql.endsWith(";"));
  }

  @Test
  void buildInsertEdgeValues() {
    StatementBuilder sb = new StatementBuilder();
    List<String> cols = List.of("_airbyte_data", "_airbyte_emitted_at");

    List<String> tuples = new ArrayList<>();
    tuples.add(sb.formatEdgeEndpointsAndValues("s1", "d1", 0L, List.of("json1", 111L)));
    tuples.add(sb.formatEdgeEndpointsAndValues("s2", "d2", 5L, List.of("json2", 222L)));

    String sql = sb.buildInsertEdgeValues("orders_edge", cols, tuples);
    String expected = "INSERT EDGE `orders_edge` (`_airbyte_data`,`_airbyte_emitted_at`)\n" +
        "VALUES\n" +
        "\"s1\"->\"d1\"@0:(\"json1\",111),\n  " +
        "\"s2\"->\"d2\"@5:(\"json2\",222);";

    assertEquals(expected, sql);
  }

  @Test
  void buildInsertValuesErrorBranches() {
    StatementBuilder sb = new StatementBuilder();
    // vertex: empty cols
    assertThrows(IllegalArgumentException.class,
        () -> sb.buildInsertVertexValues("users", List.of(), List.of(sb.formatVidAndValues("v", List.of(1)))));
    // vertex: empty rows
    assertThrows(IllegalArgumentException.class,
        () -> sb.buildInsertVertexValues("users", List.of("c1"), List.of()));
    // edge: empty cols
    assertThrows(IllegalArgumentException.class,
        () -> sb.buildInsertEdgeValues("e", List.of(), List.of(sb.formatEdgeEndpointsAndValues("s", "d", 0, List.of(1)))));
    // edge: empty rows
    assertThrows(IllegalArgumentException.class,
        () -> sb.buildInsertEdgeValues("e", List.of("c1"), List.of()));
  }

  @Test
  void upsertEdgeHappyAndMismatchError() {
    StatementBuilder sb = new StatementBuilder();
    List<String> cols = List.of("c1", "c2");
    List<Object> vals = List.of("v1", 2L);
    String sql = sb.buildUpsertEdge("rel", "s", "d", 9L, cols, vals);
    assertTrue(sql.startsWith("UPSERT EDGE ON `rel` \"s\"->\"d\"@9\nSET "));
    assertTrue(sql.contains("`c1`=\"v1\""));
    assertTrue(sql.contains("`c2`=2"));
    assertTrue(sql.endsWith(";"));

    // mismatch cols/values
    assertThrows(IllegalArgumentException.class,
        () -> sb.buildUpsertEdge("rel", "s", "d", 0L, List.of("c1", "c2"), List.of(1L)));
  }

  @Test
  void upsertVertexMismatchErrorAndNullGuards() {
    StatementBuilder sb = new StatementBuilder();
    // mismatch cols/values
    assertThrows(IllegalArgumentException.class,
        () -> sb.buildUpsertVertex("tag", "vid", List.of("c1", "c2"), List.of(1L)));
    // null src/dst/vid guards
    assertThrows(IllegalArgumentException.class,
        () -> sb.buildUpsertVertex("tag", null, List.of("c1"), List.of(1L)));
    assertThrows(IllegalArgumentException.class,
        () -> sb.buildUpsertEdge("e", null, "d", 0L, List.of("c1"), List.of(1L)));
    assertThrows(IllegalArgumentException.class,
        () -> sb.buildUpsertEdge("e", "s", null, 0L, List.of("c1"), List.of(1L)));
  }

}
