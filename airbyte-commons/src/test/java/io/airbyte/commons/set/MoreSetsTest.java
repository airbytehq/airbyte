/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.set;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.google.common.collect.ImmutableSet;
import java.util.Set;
import org.junit.jupiter.api.Test;

class MoreSetsTest {

  @Test
  void testAssertEqualsVerbose() {
    final Set<Integer> set1 = ImmutableSet.of(1, 2, 3);
    final Set<Integer> set2 = ImmutableSet.of(1, 2, 3);
    final Set<Integer> set3 = ImmutableSet.of(1, 2);

    assertDoesNotThrow(() -> MoreSets.assertEqualsVerbose(set1, set1));
    assertDoesNotThrow(() -> MoreSets.assertEqualsVerbose(set1, set2));
    assertThrows(IllegalArgumentException.class, () -> MoreSets.assertEqualsVerbose(set1, set3));
  }

}
