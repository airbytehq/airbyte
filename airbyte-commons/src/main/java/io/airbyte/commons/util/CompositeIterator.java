/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.util;

import com.google.common.base.Preconditions;
import com.google.common.collect.AbstractIterator;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Composes multiple {@link AutoCloseableIterator}s. For each internal iterator, after the first
 * time its {@link Iterator#hasNext} function returns false, the composite iterator will call
 * {@link AutoCloseableIterator#close()} on that internal iterator.
 *
 * <p>
 * {@link CompositeIterator}s should be closed. Calling {@link CompositeIterator#close()} will
 * attempt to close each internal iterator as well. Thus the close method on each internal iterator
 * should be idempotent as it is will likely be called multiple times.
 * </p>
 * <p>
 * {@link CompositeIterator#close()} gives the guarantee that it will call close on each internal
 * iterator once (even if any of the iterators throw an exception). After it has attempted to close
 * each one once, {@link CompositeIterator} will rethrow the _first_ exception that it encountered
 * while closing internal iterators. If multiple internal iterators throw exceptions, only the first
 * exception will be rethrown, though the others will be logged.
 * </p>
 *
 * @param <T> type
 */
public final class CompositeIterator<T> extends AbstractIterator<T> implements AutoCloseableIterator<T> {

  private static final Logger LOGGER = LoggerFactory.getLogger(CompositeIterator.class);

  private final List<AutoCloseableIterator<T>> iterators;

  private int i;
  private boolean hasClosed;

  CompositeIterator(final List<AutoCloseableIterator<T>> iterators) {
    Preconditions.checkNotNull(iterators);

    this.iterators = iterators;
    this.i = 0;
    this.hasClosed = false;
  }

  @Override
  protected T computeNext() {
    assertHasNotClosed();

    if (iterators.isEmpty()) {
      return endOfData();
    }

    // 1. search for an iterator that hasNext.
    // 2. close each iterator we encounter those that do not.
    // 3. if there are none, we are done.
    while (!currentIterator().hasNext()) {
      try {
        currentIterator().close();
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }

      if (i + 1 < iterators.size()) {
        i++;
      } else {
        return endOfData();
      }
    }

    return currentIterator().next();
  }

  private AutoCloseableIterator<T> currentIterator() {
    return iterators.get(i);
  }

  @Override
  public void close() throws Exception {
    hasClosed = true;

    final List<Exception> exceptions = new ArrayList<>();
    for (final AutoCloseableIterator<T> iterator : iterators) {
      try {
        iterator.close();
      } catch (final Exception e) {
        LOGGER.error("exception while closing", e);
        exceptions.add(e);
      }
    }

    if (!exceptions.isEmpty()) {
      throw exceptions.get(0);
    }
  }

  private void assertHasNotClosed() {
    Preconditions.checkState(!hasClosed);
  }

}
