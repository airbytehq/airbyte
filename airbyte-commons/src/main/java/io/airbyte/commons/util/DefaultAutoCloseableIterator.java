/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.util;

import com.google.common.base.Preconditions;
import com.google.common.collect.AbstractIterator;
import io.airbyte.commons.concurrency.VoidCallable;
import java.util.Iterator;

/**
 * The canonical {@link AutoCloseableIterator}. The default behavior guarantees that the provided
 * close functional will be called no more than one time.
 *
 * @param <T> type
 */
class DefaultAutoCloseableIterator<T> extends AbstractIterator<T> implements AutoCloseableIterator<T> {

  private final Iterator<T> iterator;
  private final VoidCallable onClose;

  private boolean hasClosed;

  public DefaultAutoCloseableIterator(final Iterator<T> iterator, final VoidCallable onClose) {
    Preconditions.checkNotNull(iterator);
    Preconditions.checkNotNull(onClose);

    this.iterator = iterator;
    this.onClose = onClose;
    this.hasClosed = false;
  }

  @Override
  protected T computeNext() {
    assertHasNotClosed();

    if (iterator.hasNext()) {
      return iterator.next();
    } else {
      return endOfData();
    }
  }

  @Override
  public void close() throws Exception {
    if (!hasClosed) {
      hasClosed = true;
      onClose.call();
    }
  }

  private void assertHasNotClosed() {
    Preconditions.checkState(!hasClosed);
  }

}
