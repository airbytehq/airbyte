/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async.buffers

import java.util.concurrent.TimeUnit
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

class MemoryBoundedLinkedBlockingQueueTest {
    @Test
    @Throws(InterruptedException::class)
    internal fun offerAndTakeShouldReturn() {
        val queue = MemoryBoundedLinkedBlockingQueue<String>(1024)
        queue.offer("abc", 6)
        val item = queue.take()

        assertEquals("abc", item.item)
    }

    @Test
    @Throws(InterruptedException::class)
    internal fun testBlocksOnFullMemory() {
        val queue = MemoryBoundedLinkedBlockingQueue<String>(10)
        assertTrue(queue.offer("abc", 6))
        assertFalse(queue.offer("abc", 6))
        assertNotNull(queue.poll(1, TimeUnit.NANOSECONDS))
        assertNull(queue.poll(1, TimeUnit.NANOSECONDS))
    }

    @ParameterizedTest
    @ValueSource(longs = [1024, 100000, 600])
    internal fun getMaxMemoryUsage(size: Long) {
        val queue = MemoryBoundedLinkedBlockingQueue<String>(size)

        assertEquals(0, queue.getCurrentMemoryUsage())
        assertEquals(size, queue.getMaxMemoryUsage())

        queue.addMaxMemory(-100)

        assertEquals(size - 100, queue.getMaxMemoryUsage())

        queue.addMaxMemory(123)

        assertEquals(size - 100 + 123, queue.getMaxMemoryUsage())
    }
}
