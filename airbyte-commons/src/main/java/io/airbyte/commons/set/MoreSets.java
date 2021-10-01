/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.set;

import com.google.common.base.Preconditions;
import com.google.common.collect.Sets;
import java.util.HashSet;
import java.util.Set;

public class MoreSets {

  public static <T> void assertEqualsVerbose(final Set<T> set1, final Set<T> set2) {
    Preconditions.checkNotNull(set1);
    Preconditions.checkNotNull(set2);

    Preconditions.checkArgument(set1.equals(set2), String.format(
        "Sets are not the same. Elements in set 1 and not in set 2: %s.  Elements in set 2 and not in set 1: %s",
        Sets.difference(set1, set2), Sets.difference(set2, set1)));
  }

  /**
   * Remove subtract all of the records in one set from another.
   *
   * @param minuend - set being subtracted from
   * @param subtrahend - set with values to subtract
   * @param <T> - type of the set
   * @return - difference -- original set (minuend) with all of the items that were present in the
   *         subtrahend removed (if they were present).
   */
  public static <T> Set<T> subtract(final Set<T> minuend, final Set<T> subtrahend) {
    final HashSet<T> difference = new HashSet<>(minuend);
    difference.removeAll(subtrahend);
    return difference;
  }

}
