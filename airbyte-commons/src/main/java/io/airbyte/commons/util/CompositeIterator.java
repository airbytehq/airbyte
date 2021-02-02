package io.airbyte.commons.util;

import com.google.common.collect.AbstractIterator;
import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public final class CompositeIterator<T> extends AbstractIterator<T> implements AutoCloseableIterator<T> {
  private static final Logger LOGGER = LoggerFactory.getLogger(CompositeIterator.class);

  private final List<AutoCloseableIterator<T>> iterators;
  private int i = 0;

  CompositeIterator(List<AutoCloseableIterator<T>> iterators) {
    this.iterators = iterators;
  }

  @Override
  protected T computeNext() {
    if (iterators.isEmpty()) {
      return endOfData();
    }

    // 1. search for an iterator that hasNext.
    // 2. close each iterator we encounter those that do not.
    // 3. if there are none, we are done.
    while(!currentIterator().hasNext()) {
      try {
        currentIterator().close();
      } catch (Exception e) {
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
    final List<Exception> exceptions = new ArrayList<>();
    for (AutoCloseableIterator<T> iterator : iterators) {
      try {
        iterator.close();
      } catch (Exception e) {
        LOGGER.error("exception while closing", e);
        exceptions.add(e);
      }
    }

    if (!exceptions.isEmpty()) {
      throw exceptions.get(0);
    }
  }
}
