/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.util;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.google.common.collect.Lists;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;

class MoreListsTest {

  @Test
  void testLast() {
    assertEquals(Optional.of(3), MoreLists.last(List.of(1, 2, 3)));
    assertEquals(Optional.empty(), MoreLists.last(List.of()));

    List<Integer> ints = new ArrayList<>();
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
