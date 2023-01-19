/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.util;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.List;
import org.junit.jupiter.api.Test;

class MoreListsTest {

  @Test
  void testConcat() {
    final List<List<Integer>> lists = List.of(List.of(1, 2, 3), List.of(4, 5, 6), List.of(7, 8, 9));
    final List<Integer> expected = List.of(1, 2, 3, 4, 5, 6, 7, 8, 9);
    final List<Integer> actual = MoreLists.concat(lists.get(0), lists.get(1), lists.get(2));
    assertEquals(expected, actual);
  }

  @Test
  void testGetOrNull() {
    assertThrows(NullPointerException.class, () -> MoreLists.getOrNull(null, 0));
    assertEquals(1, MoreLists.getOrNull(List.of(1, 2, 3), 0));
    assertEquals(2, MoreLists.getOrNull(List.of(1, 2, 3), 1));
    assertEquals(3, MoreLists.getOrNull(List.of(1, 2, 3), 2));
    assertNull(MoreLists.getOrNull(List.of(1, 2, 3), 3));
  }

}
