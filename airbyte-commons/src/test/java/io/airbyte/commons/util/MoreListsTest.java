/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.util;

import static org.junit.jupiter.api.Assertions.assertEquals;

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

}
