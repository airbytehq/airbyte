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

package io.airbyte.queue;

import com.google.common.base.Preconditions;
import com.google.common.collect.AbstractIterator;
import com.leansoft.bigqueue.BigQueueImpl;
import com.leansoft.bigqueue.IBigQueue;
import io.airbyte.commons.lang.CloseableQueue;
import java.io.IOException;
import java.nio.file.Path;
import java.util.AbstractQueue;
import java.util.Iterator;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Wraps BigQueueImpl behind Airbyte persistent queue interface. BigQueueImpl is threadsafe.
 */
public class BigQueue extends AbstractQueue<byte[]> implements CloseableQueue<byte[]> {

  private final IBigQueue queue;
  private final AtomicBoolean closed = new AtomicBoolean(false);

  public BigQueue(Path persistencePath, String queueName) throws IOException {
    queue = new BigQueueImpl(persistencePath.toString(), queueName);
  }

  @Override
  public boolean offer(byte[] bytes) {
    Preconditions.checkState(!closed.get());
    try {
      queue.enqueue(bytes);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
    return true;
  }

  @Override
  public byte[] poll() {
    Preconditions.checkState(!closed.get());
    try {
      return queue.dequeue();
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public byte[] peek() {
    Preconditions.checkState(!closed.get());
    try {
      return queue.peek();
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public int size() {
    Preconditions.checkState(!closed.get());
    return Math.toIntExact(queue.size());
  }

  @Override
  public Iterator<byte[]> iterator() {
    Preconditions.checkState(!closed.get());

    return new AbstractIterator<>() {

      @Override
      protected byte[] computeNext() {
        final byte[] poll = poll();
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
    // todo (cgardens) - this barfs out a huge warning. known issue with the lib:
    // https://github.com/bulldog2011/bigqueue/issues/35.
    queue.close();
    queue.gc();
  }

}
