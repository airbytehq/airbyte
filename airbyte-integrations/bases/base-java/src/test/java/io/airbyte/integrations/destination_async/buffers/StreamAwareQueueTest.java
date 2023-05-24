/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.buffers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;

import io.airbyte.protocol.models.v0.AirbyteMessage;
import org.junit.jupiter.api.Test;

public class StreamAwareQueueTest {

  @Test
  void test() throws InterruptedException {
    final StreamAwareQueue queue = new StreamAwareQueue(1024);

    assertEquals(0, queue.getCurrentMemoryUsage());
    assertNull(queue.getTimeOfLastMessage().orElse(null));

    queue.offer(new AirbyteMessage(), 6, 1);
    queue.offer(new AirbyteMessage(), 6, 2);
    queue.offer(new AirbyteMessage(), 6, 3);

    assertEquals(18, queue.getCurrentMemoryUsage());
    assertNotNull(queue.getTimeOfLastMessage().orElse(null));

    queue.take();
    queue.take();
    queue.take();

    assertEquals(0, queue.getCurrentMemoryUsage());
    assertNotNull(queue.getTimeOfLastMessage().orElse(null));
  }

}
