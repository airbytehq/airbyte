/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination_async.buffers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

public class StreamAwareQueueTest {

  @Test
  void test() throws InterruptedException {
    final StreamAwareQueue queue = new StreamAwareQueue(1024);

    assertEquals(0, queue.getCurrentMemoryUsage());
    assertNull(queue.getTimeOfLastMessage().orElse(null));

    queue.offer(new PartialAirbyteMessage(), 6, 1);
    queue.offer(new PartialAirbyteMessage(), 6, 2);
    queue.offer(new PartialAirbyteMessage(), 6, 3);

    assertEquals(18, queue.getCurrentMemoryUsage());
    assertNotNull(queue.getTimeOfLastMessage().orElse(null));

    queue.take();
    queue.take();
    queue.take();

    assertEquals(0, queue.getCurrentMemoryUsage());
    // This should be null because the queue is empty
    assertTrue(queue.getTimeOfLastMessage().isEmpty(), "Expected empty optional; got " + queue.getTimeOfLastMessage());
  }

  @ParameterizedTest
  @ValueSource(longs = {1024, 100000, 600})
  void getMaxMemoryUsage(final long size) {
    final StreamAwareQueue queue = new StreamAwareQueue(size);

    assertEquals(0, queue.getCurrentMemoryUsage());
    assertEquals(size, queue.getMaxMemoryUsage());

    queue.addMaxMemory(-100);

    assertEquals(size - 100, queue.getMaxMemoryUsage());

    queue.addMaxMemory(123);

    assertEquals(size - 100 + 123, queue.getMaxMemoryUsage());
  }

  @Test
  void isEmpty() {
    final StreamAwareQueue queue = new StreamAwareQueue(1024);

    assertTrue(queue.isEmpty());

    queue.offer(new PartialAirbyteMessage(), 10, 1);

    assertFalse(queue.isEmpty());

    queue.offer(new PartialAirbyteMessage(), 10, 1);
    queue.offer(new PartialAirbyteMessage(), 10, 1);
    queue.offer(new PartialAirbyteMessage(), 10, 1);

    assertFalse(queue.isEmpty());

    queue.poll();
    queue.poll();
    queue.poll();
    queue.poll();

    assertTrue(queue.isEmpty());
  }

}
