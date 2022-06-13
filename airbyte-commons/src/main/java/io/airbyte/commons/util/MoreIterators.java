/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.util;

import com.google.common.collect.AbstractIterator;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
import java.util.function.Supplier;

public class MoreIterators {

  /**
   * Create an iterator from elements
   *
   * @param elements element to put in iterator
   * @param <T> type
   * @return iterator with all elements
   */
  public static <T> Iterator<T> of(final T... elements) {
    return Arrays.asList(elements).iterator();
  }

  /**
   * Create a list from an iterator
   *
   * @param iterator iterator to convert
   * @param <T> type
   * @return list
   */
  public static <T> List<T> toList(final Iterator<T> iterator) {
    final List<T> list = new ArrayList<>();
    while (iterator.hasNext()) {
      list.add(iterator.next());
    }
    return list;
  }

  /**
   * Create a set from an iterator
   *
   * @param iterator iterator to convert
   * @param <T> type
   * @return set
   */
  public static <T> Set<T> toSet(final Iterator<T> iterator) {
    final Set<T> set = new HashSet<>();
    while (iterator.hasNext()) {
      set.add(iterator.next());
    }
    return set;
  }

  public static <T> Iterator<T> singletonIteratorFromSupplier(final Supplier<T> supplier) {
    return new AbstractIterator<T>() {

      private boolean hasSupplied = false;

      @Override
      protected T computeNext() {
        if (!hasSupplied) {
          hasSupplied = true;
          return supplier.get();
        } else {
          return endOfData();
        }
      }

    };
  }

}
