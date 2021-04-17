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
import com.leansoft.bigqueue.BigQueueImpl;
import com.leansoft.bigqueue.IBigQueue;
import io.airbyte.commons.lang.CloseableQueue;
import java.io.IOException;
import java.nio.file.Path;
import java.util.AbstractQueue;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.util.function.Supplier;

/**
 * Wraps BigQueueImpl behind Airbyte persistent queue interface. BigQueueImpl is threadsafe.
 *
 * Due to the mechanics of how AbstractQueues are accessed. This class uses a
 * {@link ReentrantReadWriteLock} to ensure the underlying queue is preserved in the event this
 * class is logged/printed or it's iterator is accessed.
 *
 * Lock behavior:
 * <li>No other methods can be called if {@link #offer(byte[])} or {@link #iterator()} are called
 * since they modify the queue's contents.</li>
 * <li>{@link #poll()} and {@link #peek()} and {@link #size()} can always be called unless the
 * blocking methods are executing. Although these operations interact with the queue, no logic
 * exists within this class and we safely rely on {@link BigQueueImpl}'s internal locking
 * guarantees for read operations.</li>
 *
 */
public class BigQueue extends AbstractQueue<byte[]> implements CloseableQueue<byte[]> {

  private final IBigQueue queue;
  private final ReadWriteLock lock = new ReentrantReadWriteLock();
  private final AtomicBoolean closed = new AtomicBoolean(false);

  public BigQueue(Path persistencePath, String queueName) throws IOException {
    queue = new BigQueueImpl(persistencePath.toString(), queueName);
  }

  @Override
  public boolean offer(byte[] bytes) {
    Preconditions.checkState(!closed.get());
    return BlockingOp.execute(lock, () -> {
      try {
        queue.enqueue(bytes);
        return true;
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
    });
  }

  @Override
  public byte[] poll() {
    Preconditions.checkState(!closed.get());
    return NonBlockingOp.execute(lock, () -> {
      try {
        return queue.dequeue();
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
    });
  }

  @Override
  public byte[] peek() {
    Preconditions.checkState(!closed.get());
    return NonBlockingOp.execute(lock, () -> {
      try {
        return queue.peek();
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
    });
  }

  @Override
  public int size() {
    Preconditions.checkState(!closed.get());
    return NonBlockingOp.execute(lock, () -> Math.toIntExact(queue.size()));
  }

  /**
   * Logging frameworks call this method when printing out this class. Copy existing elements and
   * reinsert them back into the queue so as not to empty this queue while printing it.
   *
   * When constructing an iterator, no other method is allowed to function to preserve order.
   *
   * Since this reads a disk-based queue into memory, care must be taken when retrieving this queue's
   * iterator. Attempting to return the iterator of a queue that is too big will result in an
   * {@link OutOfMemoryError}.
   */
  @Override
  public Iterator<byte[]> iterator() {
    Preconditions.checkState(!closed.get());
    return BlockingOp.execute(lock, () -> {
      try {
        List<byte[]> elements = new ArrayList<>();
        while (!queue.isEmpty()) {
          elements.add(queue.dequeue());
        }
        for (byte[] e : elements) {
          queue.enqueue(e);
        }
        return elements.iterator();
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
    });
  }

  @Override
  public void close() throws Exception {
    closed.set(true);
    // todo (cgardens) - this barfs out a huge warning. known issue with the lib:
    // https://github.com/bulldog2011/bigqueue/issues/35.
    queue.close();
    queue.gc();
  }

  /**
   * Print size instead of queue contents to avoid any sort of logging complication. Note this does
   * not hold any read locks for simplicity, and queue size cannot be used as a source of truth.
   */
  @Override
  public String toString() {
    return "BigQueue{" +
        "queue=" + queue.hashCode() +
        ", size=" + queue.size() +
        ", closed=" + closed +
        '}';
  }

  private interface NonBlockingOp {

    static <T> T execute(ReadWriteLock lock, Supplier<T> supplier) {
      // ReadLocks always execute unless a WriteLock is held.
      lock.readLock().lock();
      try {
        return supplier.get();
      } catch (Exception e) {
        throw new RuntimeException(e);
      } finally {
        lock.readLock().unlock();
      }
    }

  }

  private interface BlockingOp {

    static <T> T execute(ReadWriteLock lock, Supplier<T> supplier) {
      lock.writeLock().lock();
      try {
        return supplier.get();
      } catch (Exception e) {
        throw new RuntimeException(e);
      } finally {
        lock.writeLock().unlock();
      }
    }

  }

}
