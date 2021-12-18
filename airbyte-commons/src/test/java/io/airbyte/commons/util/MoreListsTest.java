/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.util;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.google.common.collect.Lists;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;

class MoreListsTest {

  @Test
  void testLast2() {
    System.out.println("what i get " + MoreLists.sublistRemoveNFromEnd(List.of(1, 2, 3), 1));
  }

  @Test
  void testSublistToEnd() {
    final List<Integer> testList = List.of(1, 2, 3);
    assertEquals(List.of(1, 2, 3), MoreLists.sublistToEnd(testList, 0));
    assertEquals(List.of(2, 3), MoreLists.sublistToEnd(testList, 1));
    assertEquals(List.of(3), MoreLists.sublistToEnd(testList, 2));
    assertEquals(List.of(), MoreLists.sublistToEnd(testList, 3));
    assertThrows(IllegalArgumentException.class, () -> MoreLists.sublistToEnd(testList, 4));

    final List<Integer> emptyList = List.of();
    assertEquals(List.of(), MoreLists.sublistToEnd(emptyList, 0));
    assertThrows(IllegalArgumentException.class, () -> MoreLists.sublistToEnd(emptyList, 1));
  }

  @Test
  void testSublistRemoveNFromEnd() {
    final List<Integer> testList = List.of(1, 2, 3);
    assertEquals(List.of(1, 2, 3), MoreLists.sublistRemoveNFromEnd(testList, 0));
    assertEquals(List.of(1, 2), MoreLists.sublistRemoveNFromEnd(testList, 1));
    assertEquals(List.of(1), MoreLists.sublistRemoveNFromEnd(testList, 2));
    assertEquals(List.of(), MoreLists.sublistRemoveNFromEnd(testList, 3));
    assertThrows(IllegalArgumentException.class, () -> MoreLists.sublistRemoveNFromEnd(testList, 4));

    final List<Integer> emptyList = List.of();
    assertEquals(List.of(), MoreLists.sublistRemoveNFromEnd(emptyList, 0));
    assertThrows(IllegalArgumentException.class, () -> MoreLists.sublistRemoveNFromEnd(emptyList, 1));
  }

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
    final ArrayList<Integer> originalList = Lists.newArrayList(1, 2, 3);
    assertEquals(List.of(3, 2, 1), MoreLists.reversed(originalList));
    assertEquals(List.of(1, 2, 3), originalList);
  }

}
