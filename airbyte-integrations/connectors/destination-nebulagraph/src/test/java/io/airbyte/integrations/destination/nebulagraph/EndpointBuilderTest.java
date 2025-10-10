/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.nebulagraph;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("EndpointBuilder")
class EndpointBuilderTest {

  @Test
  void buildSrcDst() {
    EndpointBuilder eb = new EndpointBuilder();
    Map<String, Object> rec = Map.of(
        "a", "x",
        "b", "y",
        "c", 1,
        "d", 2);

    String src = eb.buildSrc(rec, List.of("a", "b"), "|", 128);
    String dst = eb.buildDst(rec, List.of("c", "d"), "-", 128);

    assertEquals("x|y", src);
    assertEquals("1-2", dst);
  }

  @Test
  void buildSrcDstErrors() {
    EndpointBuilder eb = new EndpointBuilder();
    Map<String, Object> recMissing = Map.of("a", "x");

    // missing field
    assertThrows(IllegalArgumentException.class,
        () -> eb.buildSrc(recMissing, List.of("a", "b"), "|", 128));

    // length exceeds
    Map<String, Object> longRec = Map.of("a", "abcd");
    assertThrows(IllegalArgumentException.class,
        () -> eb.buildSrc(longRec, List.of("a"), "", 3));
    assertThrows(IllegalArgumentException.class,
        () -> eb.buildDst(longRec, List.of("a"), "", 3));
  }

  @Test
  void buildRank() {
    EndpointBuilder eb = new EndpointBuilder();
    Map<String, Object> rec = Map.of(
        "r1", 7,
        "r2", "42",
        "r3", "not_a_number");

    assertEquals(0L, eb.buildRank(rec, null));
    assertEquals(7L, eb.buildRank(rec, "r1"));
    assertEquals(42L, eb.buildRank(rec, "r2"));
    assertEquals(0L, eb.buildRank(rec, "r3"));
  }

}
