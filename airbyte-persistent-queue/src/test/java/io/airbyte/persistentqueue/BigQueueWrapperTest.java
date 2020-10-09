package io.airbyte.persistentqueue;


import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.common.base.Charsets;
import com.google.common.collect.Lists;
import java.io.IOException;
import java.nio.file.Files;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class BigQueueWrapperTest {

  private CloseableInputQueue<byte[]> queue;

  @BeforeEach
  void setup() throws IOException {
    queue = new BigQueueWrapper(Files.createTempDirectory("qtest"), "test");
  }

  @AfterEach
  void teardown() throws Exception {
    queue.close();
  }

  @Test
  void testSize() {
    assertEquals(0, queue.size());
    queue.offer(toBytes("hello"));
    assertEquals(1, queue.size());
    queue.offer(toBytes("hello"));
    assertEquals(2, queue.size());
  }

  @Test
  void testIterator() throws Exception {
    queue.offer(toBytes("hello"));
    queue.offer(toBytes("goodbye"));
    queue.closeInput();

    final List<String> expected = Lists.newArrayList("hello", "goodbye");
    final List<String> actual = queue.stream().map(val -> val != null ? new String(val, Charsets.UTF_8) : null).collect(Collectors.toList());

    assertEquals(expected, actual);
  }

  @Test
  void testPollHasValueInputClosedFalse() {
    queue.offer(toBytes("hello"));
    assertEquals("hello", new String(Objects.requireNonNull(queue.poll()), Charsets.UTF_8));
  }

  @Test
  void testPollHasValueInputClosed() {
    queue.offer(toBytes("hello"));
    queue.closeInput();
    assertEquals("hello", new String(Objects.requireNonNull(queue.poll()), Charsets.UTF_8));
  }

  @Test
  void testPollHasValueFalseInputClosed() {
    queue.closeInput();
    assertNull(queue.poll());
  }

  @Test
  void testPollHasValueFalseInputClosedFalse() throws InterruptedException {
    final AtomicBoolean hasAttempted = new AtomicBoolean(false);
    final AtomicReference<String> output = new AtomicReference<>();

    Thread getterThread = new Thread(() -> {
      hasAttempted.set(true);
      output.set(new String(Objects.requireNonNull(queue.poll()), Charsets.UTF_8));
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

      queue.offer(toBytes("hello"));
      queue.closeInput();
    });
    setterThread.start();

    setterThread.join(1000);
    getterThread.join(1000);

    assertTrue(hasAttempted.get());
    assertEquals("hello", output.get());

  }

  private static byte[] toBytes(String string) {
    return string.getBytes(Charsets.UTF_8);
  }

}