/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination_async.buffers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

public class MemoryBoundedLinkedBlockingQueueTest {

  @Test
  void offerAndTakeShouldReturn() throws InterruptedException {
    final MemoryBoundedLinkedBlockingQueue<String> queue = new MemoryBoundedLinkedBlockingQueue<>(1024);

    queue.offer("abc", 6);

    final var item = queue.take();

    assertEquals("abc", item.item());
  }

  @Test
  void testBlocksOnFullMemory() throws InterruptedException {
    final MemoryBoundedLinkedBlockingQueue<String> queue = new MemoryBoundedLinkedBlockingQueue<>(10);
    assertTrue(queue.offer("abc", 6));
    assertFalse(queue.offer("abc", 6));

    assertNotNull(queue.poll(1, TimeUnit.NANOSECONDS));
    assertNull(queue.poll(1, TimeUnit.NANOSECONDS));
  }

  @ParameterizedTest
  @ValueSource(longs = {1024, 100000, 600})
  void getMaxMemoryUsage(final long size) {
    final MemoryBoundedLinkedBlockingQueue<String> queue = new MemoryBoundedLinkedBlockingQueue<>(size);

    assertEquals(0, queue.getCurrentMemoryUsage());
    assertEquals(size, queue.getMaxMemoryUsage());

    queue.addMaxMemory(-100);

    assertEquals(size - 100, queue.getMaxMemoryUsage());

    queue.addMaxMemory(123);

    assertEquals(size - 100 + 123, queue.getMaxMemoryUsage());
  }

}
