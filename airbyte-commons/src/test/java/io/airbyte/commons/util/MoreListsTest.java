/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.util;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;

class MoreListsTest {

  @Test
  void testLast() {
    assertEquals(Optional.of(3), MoreLists.last(List.of(1, 2, 3)));
    assertEquals(Optional.empty(), MoreLists.last(List.of()));

    final List<Integer> ints = new ArrayList<>();
    ints.add(1);
    ints.add(2);
    ints.add(null);
    assertEquals(Optional.empty(), MoreLists.last(ints));
  }

  @Test
  void testReverse() {
    final List<Integer> originalList = List.of(1, 2, 3);
    assertEquals(List.of(3, 2, 1), MoreLists.reversed(originalList));
    assertEquals(List.of(1, 2, 3), originalList);
  }

  @Test
  void testConcat() {
    final List<List<Integer>> lists = List.of(List.of(1, 2, 3), List.of(4, 5, 6), List.of(7, 8, 9));
    final List<Integer> expected = List.of(1, 2, 3, 4, 5, 6, 7, 8, 9);
    final List<Integer> actual = MoreLists.concat(lists.get(0), lists.get(1), lists.get(2));
    assertEquals(expected, actual);
  }

  @Test
  void testAdd() {
    final List<Integer> originalList = List.of(1, 2, 3);

    assertEquals(List.of(1, 2, 3, 4), MoreLists.add(originalList, 4));
    // verify original list was not mutated.
    assertEquals(List.of(1, 2, 3), originalList);
  }

}
