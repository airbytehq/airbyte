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

import com.google.common.collect.AbstractIterator;
import io.airbyte.commons.concurrency.VoidCallableNoException;
import java.util.Iterator;

/**
 * A {@link ResourceIterator} that will execute its close function when {@link Iterator#hasNext}
 * returns false for the first time.
 *
 * @param <T> type
 */
class AutoCloseIterator<T> extends AbstractIterator<T> implements ResourceIterator<T> {

  private final ResourceIterator<T> internalIterator;
  private final VoidCallableNoException onClose;

  private boolean hasClosed;

  public AutoCloseIterator(ResourceIterator<T> iterator) {
    this.internalIterator = iterator;
    this.onClose = VoidCallableNoException.fromVoidCallable(iterator::close);
  }

  @Override
  protected T computeNext() {
    if (internalIterator.hasNext()) {
      return internalIterator.next();
    } else {
      if (!hasClosed) {
        hasClosed = true;
        onClose.call();
      }
      return endOfData();
    }
  }

  @Override
  public void close() throws Exception {
    internalIterator.close();
  }

}
