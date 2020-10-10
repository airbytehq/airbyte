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

package io.airbyte.persistentqueue;

import com.google.common.base.Preconditions;
import com.google.common.collect.AbstractIterator;
import java.util.AbstractQueue;
import java.util.Iterator;
import java.util.concurrent.atomic.AtomicBoolean;

public abstract class AbstractCloseableInputQueue<E> extends AbstractQueue<E> implements CloseableInputQueue<E> {

  protected final AtomicBoolean inputClosed = new AtomicBoolean(false);
  protected final AtomicBoolean closed = new AtomicBoolean(false);

  protected abstract boolean enqueueInternal(E element);

  protected abstract E pollInternal();

  /**
   * Adds an element to the queue.
   *
   * @param element - element to enqueue.
   * @return true if enqueue successful, otherwise false.
   * @throws IllegalStateException if invoked after {@link CloseableInputQueue#closeInput()}
   */
  @Override
  public boolean offer(E element) {
    Preconditions.checkState(!closed.get());
    Preconditions.checkState(!inputClosed.get());
    Preconditions.checkNotNull(element);
    return enqueueInternal(element);
  }

  /*
   * (non javadoc comment to avoid autoformatting making this impossible to read). Blocking call to
   * dequeue an element. | hasValue | inputClosed | behavior |
   * ---------------------------------------- | true | false | return val | | false | false | block
   * until | | true | true | return val | | false | true | return null |
   *
   * @return a value from the queue or null if the queue is empty and will not receive anymore data.
   */
  @Override
  public E poll() {
    Preconditions.checkState(!closed.get());
    // if the queue is closed, always stop.
    while (!closed.get()) {
      final E dequeue = pollInternal();

      // if we find a value, always return it.
      if (dequeue != null) {
        return dequeue;
      }

      // if there is nothing in the queue and there will be no more values, end.
      if (dequeue == null && inputClosed.get()) {
        return null;
      }

      // if not value but could be more, sleep then try again.
      try {
        Thread.sleep(1000);
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      }
    }
    return null;
  }

  @Override
  public void closeInput() {
    inputClosed.set(true);
  }

  protected abstract void closeInternal() throws Exception;

  @Override
  public Iterator<E> iterator() {
    Preconditions.checkState(!closed.get());

    return new AbstractIterator<>() {

      @Override
      protected E computeNext() {
        final E poll = poll();
        if (poll == null) {
          return endOfData();
        }
        return poll;
      }

    };
  }

  @Override
  public void close() throws Exception {
    closed.set(true);
    closeInternal();
  }

}
