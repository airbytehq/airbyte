/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.util;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;

public class MoreLists {

  /**
   * @return returns empty optional if the list is empty or if the last element in the list is null.
   */
  public static <T> Optional<T> last(List<T> list) {
    if (list.isEmpty()) {
      return Optional.empty();
    }
    return Optional.ofNullable(list.get(list.size() - 1));
  }

  /**
   * Reverses a list by creating a new list with the same elements of the input list and then
   * reversing it. The input list will not be altered.
   *
   * @param list to reverse
   * @param <T> type
   * @return new list with elements of original reversed.
   */
  public static <T> List<T> reversed(List<T> list) {
    final ArrayList<T> reversed = new ArrayList<>(list);
    Collections.reverse(reversed);
    return reversed;
  }

}
