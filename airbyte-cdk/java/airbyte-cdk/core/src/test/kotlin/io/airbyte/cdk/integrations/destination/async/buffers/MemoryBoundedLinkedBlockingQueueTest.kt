/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async.buffers

import java.util.concurrent.TimeUnit
import org.junit.jupiter.api.Assertions
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

        Assertions.assertEquals("abc", item.item)
    }

    @Test
    @Throws(InterruptedException::class)
    internal fun testBlocksOnFullMemory() {
        val queue = MemoryBoundedLinkedBlockingQueue<String>(10)
        Assertions.assertTrue(queue.offer("abc", 6))
        Assertions.assertFalse(queue.offer("abc", 6))

        Assertions.assertNotNull(queue.poll(1, TimeUnit.NANOSECONDS))
        Assertions.assertNull(queue.poll(1, TimeUnit.NANOSECONDS))
    }

    @ParameterizedTest
    @ValueSource(longs = [1024, 100000, 600])
    internal fun getMaxMemoryUsage(size: Long) {
        val queue = MemoryBoundedLinkedBlockingQueue<String>(size)

        Assertions.assertEquals(0, queue.currentMemoryUsage)
        Assertions.assertEquals(size, queue.maxMemoryUsage)

        queue.addMaxMemory(-100)

        Assertions.assertEquals(size - 100, queue.maxMemoryUsage)

        queue.addMaxMemory(123)

        Assertions.assertEquals(size - 100 + 123, queue.maxMemoryUsage)
    }
}
