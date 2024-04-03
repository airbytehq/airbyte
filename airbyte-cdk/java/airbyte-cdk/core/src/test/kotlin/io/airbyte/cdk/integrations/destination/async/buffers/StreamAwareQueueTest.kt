/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async.buffers

import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

class StreamAwareQueueTest {
    @Test
    @Throws(InterruptedException::class)
    internal fun test() {
        val queue = StreamAwareQueue(1024)

        assertEquals(0, queue.getCurrentMemoryUsage())
        assertNull(queue.getTimeOfLastMessage().orElse(null))

        queue.offer(PartialAirbyteMessage(), 6, 1)
        queue.offer(PartialAirbyteMessage(), 6, 2)
        queue.offer(PartialAirbyteMessage(), 6, 3)

        assertEquals(18, queue.getCurrentMemoryUsage())
        assertNotNull(queue.getTimeOfLastMessage().orElse(null))

        queue.take()
        queue.take()
        queue.take()

        assertEquals(0, queue.getCurrentMemoryUsage())
        // This should be null because the queue is empty
        assertTrue(
            queue.getTimeOfLastMessage().isEmpty,
            "Expected empty optional; got " + queue.getTimeOfLastMessage(),
        )
    }

    @ParameterizedTest
    @ValueSource(longs = [1024, 100000, 600])
    internal fun getMaxMemoryUsage(size: Long) {
        val queue = StreamAwareQueue(size)

        assertEquals(0, queue.getCurrentMemoryUsage())
        assertEquals(size, queue.getMaxMemoryUsage())

        queue.addMaxMemory(-100)

        assertEquals(size - 100, queue.getMaxMemoryUsage())

        queue.addMaxMemory(123)

        assertEquals(size - 100 + 123, queue.getMaxMemoryUsage())
    }

    @Test
    internal fun isEmpty() {
        val queue = StreamAwareQueue(1024)

        assertTrue(queue.isEmpty())

        queue.offer(PartialAirbyteMessage(), 10, 1)

        assertFalse(queue.isEmpty())

        queue.offer(PartialAirbyteMessage(), 10, 1)
        queue.offer(PartialAirbyteMessage(), 10, 1)
        queue.offer(PartialAirbyteMessage(), 10, 1)

        assertFalse(queue.isEmpty())

        queue.poll()
        queue.poll()
        queue.poll()
        queue.poll()

        assertTrue(queue.isEmpty())
    }
}
