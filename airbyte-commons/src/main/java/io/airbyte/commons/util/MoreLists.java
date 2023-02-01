/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.util;

import com.google.common.base.Preconditions;
import java.util.List;
import java.util.stream.Stream;

public class MoreLists {

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

  public static <T> T getOrNull(final List<T> list, final int index) {
    Preconditions.checkNotNull(list);
    if (list.size() > index) {
      return list.get(index);
    } else {
      return null;
    }
  }

}
