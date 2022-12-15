/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.map;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.google.common.collect.ImmutableMap;
import java.util.Map;
import org.junit.jupiter.api.Test;

class MoreMapsTest {

  @Test
  void testMerge() {
    final Map<String, Integer> map1 = ImmutableMap.of("a", 3, "b", 2);
    final Map<String, Integer> map2 = ImmutableMap.of("a", 1);

    assertEquals(ImmutableMap.of("a", 1, "b", 2), MoreMaps.merge(map1, map2));
  }

}
