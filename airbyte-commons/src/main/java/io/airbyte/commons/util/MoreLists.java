/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.util;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.stream.Stream;

public class MoreLists {

  /**
   * @return returns empty optional if the list is empty or if the last element in the list is null.
   */
  public static <T> Optional<T> last(final List<T> list) {
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
  public static <T> List<T> reversed(final List<T> list) {
    final ArrayList<T> reversed = new ArrayList<>(list);
    Collections.reverse(reversed);
    return reversed;
  }

  /**
   * Concatenate multiple lists into one list.
   *
   * @param lists to concatenate
   * @param <T> type
   * @return a new concatenated list
   */
  @SafeVarargs
  public static <T> List<T> concat(final List<T>... lists) {
    return Stream.of(lists).flatMap(List::stream).toList();
  }

}
