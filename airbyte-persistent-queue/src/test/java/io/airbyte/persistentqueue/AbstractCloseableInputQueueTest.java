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

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.common.collect.Lists;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * Test the contract of {@link AbstractCloseableInputQueueTest} state machine.
 */
class AbstractCloseableInputQueueTest {

  private CloseableInputQueue<String> queue;

  @BeforeEach
  void setup() {
    queue = new TestQueue();
  }

  /*
   * OFFER CONTRACT
   */
  @Test
  void testOfferInputClosedFalse() {
    assertDoesNotThrow(() -> queue.offer("hello"));
  }

  @Test
  void testOfferInputClosed() {
    queue.closeInput();
    assertThrows(IllegalStateException.class, () -> queue.offer("hello"));
  }

  /*
   * POLL CONTRACT
   */
  @Test
  void testPollHasValueInputClosedFalse() {
    queue.offer("hello");
    assertEquals("hello", queue.poll());
  }

  @Test
  void testPollHasValueInputClosed() {
    queue.offer("hello");
    queue.closeInput();
    assertEquals("hello", queue.poll());
  }

  @Test
  void testPollHasValueFalseInputClosed() {
    queue.closeInput();
    assertNull(queue.poll());
  }

  @SuppressWarnings("BusyWait")
  @Test
  void testPollHasValueFalseInputClosedFalse() throws InterruptedException {
    final AtomicBoolean hasAttempted = new AtomicBoolean(false);
    final AtomicReference<String> output = new AtomicReference<>();

    Thread getterThread = new Thread(() -> {
      hasAttempted.set(true);
      output.set(queue.poll());
    });
    getterThread.start();

    final Thread setterThread = new Thread(() -> {
      while (!hasAttempted.get()) {
        try {
          Thread.sleep(10);
        } catch (InterruptedException e) {
          throw new RuntimeException(e);
        }
      }

      assertTrue(hasAttempted.get());
      assertNull(output.get());

      queue.offer("hello");
      queue.closeInput();
    });
    setterThread.start();

    setterThread.join(1000);
    getterThread.join(1000);

    assertTrue(hasAttempted.get());
    assertEquals("hello", output.get());
  }

  /*
   * ITERATOR CONTRACT
   */
  @Test
  void testIterator() {
    queue.offer("hello");
    queue.offer("goodbye");
    queue.closeInput();

    final List<String> expected = Lists.newArrayList("hello", "goodbye");
    final List<String> actual = new ArrayList<>(queue);

    assertEquals(expected, actual);
  }

  /*
   * CLOSED CONTRACT
   */
  @Test
  void testClosed() throws Exception {
    queue.close();
    assertDoesNotThrow(() -> queue.close());
    assertDoesNotThrow(() -> queue.closeInput());
    assertThrows(IllegalStateException.class, () -> queue.offer("hello"));
    assertThrows(IllegalStateException.class, () -> queue.poll());
    assertThrows(IllegalStateException.class, () -> queue.iterator());
  }

  private static class TestQueue extends AbstractCloseableInputQueue<String> {

    private final List<String> list = new ArrayList<>();

    @Override
    protected boolean enqueueInternal(String element) {
      list.add(0, element);
      return true;
    }

    @Override
    protected String pollInternal() {
      return list.size() == 0 ? null : list.remove(list.size() - 1);
    }

    @Override
    protected void closeInternal() {
      // no op
    }

    @Override
    public int size() {
      return list.size();
    }

    @Override
    public String peek() {
      return list.size() == 0 ? null : list.get(list.size() - 1);
    }

  }

}
