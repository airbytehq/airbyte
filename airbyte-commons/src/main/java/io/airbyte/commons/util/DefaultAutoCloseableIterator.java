/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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

  public DefaultAutoCloseableIterator(Iterator<T> iterator, VoidCallable onClose) {
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
