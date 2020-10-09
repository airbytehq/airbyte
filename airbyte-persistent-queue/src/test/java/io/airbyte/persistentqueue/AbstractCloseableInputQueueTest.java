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
  OFFER CONTRACT
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
  POLL CONTRACT
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
      while(!hasAttempted.get()) {
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
  ITERATOR CONTRACT
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
  CLOSED CONTRACT
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

  private static class TestQueue extends AbstractCloseableInputQueue<String>{
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