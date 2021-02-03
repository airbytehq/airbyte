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
import java.util.function.Supplier;

/**
 * A {@link AutoCloseableIterator} that calls the provided supplier the first time
 * {@link AutoCloseableIterator#hasNext} or {@link AutoCloseableIterator#next} is called. If
 * {@link AutoCloseableIterator#hasNext} or {@link AutoCloseableIterator#next} are never called,
 * then the supplier will never be called. This means if the iterator is closed in this state, the
 * close function on the input iterator will not be called. The assumption here is that if nothing
 * is ever supplied, then there is nothing to close.
 *
 * @param <T> type
 */
class LazyAutoCloseableIterator<T> extends AbstractIterator<T> implements AutoCloseableIterator<T> {

  private final Supplier<AutoCloseableIterator<T>> iteratorSupplier;

  private boolean hasSupplied;
  private AutoCloseableIterator<T> internalIterator;

  public LazyAutoCloseableIterator(Supplier<AutoCloseableIterator<T>> iteratorSupplier) {
    Preconditions.checkNotNull(iteratorSupplier);
    this.iteratorSupplier = iteratorSupplier;
    this.hasSupplied = false;
  }

  @Override
  protected T computeNext() {
    if (!hasSupplied) {
      internalIterator = iteratorSupplier.get();
      Preconditions.checkNotNull(internalIterator, "Supplied iterator was null.");
      hasSupplied = true;
    }

    if (internalIterator.hasNext()) {
      return internalIterator.next();
    } else {
      return endOfData();
    }
  }

  @Override
  public void close() throws Exception {
    if (internalIterator != null) {
      internalIterator.close();
    }
  }

}
