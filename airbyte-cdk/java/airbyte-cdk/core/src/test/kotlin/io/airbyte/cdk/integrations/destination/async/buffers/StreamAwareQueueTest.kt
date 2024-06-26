/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async.buffers

import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

class StreamAwareQueueTest {
    @Test
    @Throws(InterruptedException::class)
    internal fun test() {
        val queue = StreamAwareQueue(1024)

        Assertions.assertEquals(0, queue.currentMemoryUsage)
        Assertions.assertNull(queue.getTimeOfLastMessage().orElse(null))

        queue.offer(PartialAirbyteMessage(), 6, 1)
        queue.offer(PartialAirbyteMessage(), 6, 2)
        queue.offer(PartialAirbyteMessage(), 6, 3)

        Assertions.assertEquals(18, queue.currentMemoryUsage)
        Assertions.assertNotNull(queue.getTimeOfLastMessage().orElse(null))

        queue.take()
        queue.take()
        queue.take()

        Assertions.assertEquals(0, queue.currentMemoryUsage)
        // This should be null because the queue is empty
        Assertions.assertTrue(
            queue.getTimeOfLastMessage().isEmpty,
            "Expected empty optional; got " + queue.getTimeOfLastMessage(),
        )
    }

    @ParameterizedTest
    @ValueSource(longs = [1024, 100000, 600])
    internal fun getMaxMemoryUsage(size: Long) {
        val queue = StreamAwareQueue(size)

        Assertions.assertEquals(0, queue.currentMemoryUsage)
        Assertions.assertEquals(size, queue.maxMemoryUsage)

        queue.addMaxMemory(-100)

        Assertions.assertEquals(size - 100, queue.maxMemoryUsage)

        queue.addMaxMemory(123)

        Assertions.assertEquals(size - 100 + 123, queue.maxMemoryUsage)
    }

    @Test
    internal fun isEmpty() {
        val queue = StreamAwareQueue(1024)

        Assertions.assertTrue(queue.isEmpty)

        queue.offer(PartialAirbyteMessage(), 10, 1)

        Assertions.assertFalse(queue.isEmpty)

        queue.offer(PartialAirbyteMessage(), 10, 1)
        queue.offer(PartialAirbyteMessage(), 10, 1)
        queue.offer(PartialAirbyteMessage(), 10, 1)

        Assertions.assertFalse(queue.isEmpty)

        queue.poll()
        queue.poll()
        queue.poll()
        queue.poll()

        Assertions.assertTrue(queue.isEmpty)
    }
}
