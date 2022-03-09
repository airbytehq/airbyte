/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.queue;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.common.base.Charsets;
import io.airbyte.commons.lang.CloseableQueue;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Objects;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class OnDiskQueueTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(OnDiskQueueTest.class);
  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");
  private CloseableQueue<byte[]> queue;
  private Path queueRoot;

  @BeforeEach
  void setup() throws IOException {
    queueRoot = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), "test");
    queue = new OnDiskQueue(queueRoot, "test");
  }

  @AfterEach
  void teardown() throws Exception {
    queue.close();
  }

  @Test
  void testPoll() {
    queue.offer(toBytes("hello"));
    assertEquals("hello", new String(Objects.requireNonNull(queue.poll()), Charsets.UTF_8));
  }

  @Test
  void testPeek() {
    queue.offer(toBytes("hello"));
    assertEquals("hello", new String(Objects.requireNonNull(queue.peek()), Charsets.UTF_8));
    assertEquals("hello", new String(Objects.requireNonNull(queue.peek()), Charsets.UTF_8));
    assertEquals("hello", new String(Objects.requireNonNull(queue.poll()), Charsets.UTF_8));
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
  void testClosed() throws Exception {
    queue.close();
    assertDoesNotThrow(() -> queue.close());
    assertThrows(IllegalStateException.class, () -> queue.offer(toBytes("hello")));
    assertThrows(IllegalStateException.class, () -> queue.poll());
  }

  @Test
  void testCleanupOnEmpty() throws Exception {
    assertTrue(Files.exists(queueRoot));

    queue.offer(toBytes("hello"));
    queue.poll();
    queue.close();

    assertFalse(Files.exists(queueRoot));
  }

  @Test
  void testCleanupOnNotEmpty() throws Exception {
    assertTrue(Files.exists(queueRoot));

    queue.offer(toBytes("hello"));
    queue.close();

    assertFalse(Files.exists(queueRoot));
  }

  @SuppressWarnings("SameParameterValue")
  private static byte[] toBytes(final String string) {
    return string.getBytes(Charsets.UTF_8);
  }

}
