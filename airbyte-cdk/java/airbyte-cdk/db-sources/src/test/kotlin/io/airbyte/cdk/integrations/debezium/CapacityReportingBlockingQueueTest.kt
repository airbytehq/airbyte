/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium

import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout

class CapacityReportingBlockingQueueTest {

    /** Byte size of a String element is estimated as its character count for these tests. */
    private fun stringQueue(capacity: Int, maxSizeInBytes: Long) =
        CapacityReportingBlockingQueue<String>(capacity, maxSizeInBytes) { it.length.toLong() }

    @Test
    fun tracksByteSizeOnPutAndPoll() {
        val queue = stringQueue(capacity = 10, maxSizeInBytes = 1_000)

        queue.put("hello") // 5 bytes
        queue.put("world!") // 6 bytes
        Assertions.assertEquals(11L, queue.currentByteSizeEstimate)

        Assertions.assertEquals("hello", queue.poll())
        Assertions.assertEquals(6L, queue.currentByteSizeEstimate)

        // The timed poll variant must also decrement the byte accounting.
        Assertions.assertEquals("world!", queue.poll(1, TimeUnit.SECONDS))
        Assertions.assertEquals(0L, queue.currentByteSizeEstimate)
    }

    @Test
    @Timeout(15)
    fun putBlocksWhenByteLimitExceededAndResumesAfterPoll() {
        // Budget is 10 bytes; each element is 6 bytes. The first fits (empty queue); the second
        // would push us to 12 bytes, so it must block until the queue drains below the budget.
        val queue = stringQueue(capacity = 100, maxSizeInBytes = 10)
        queue.put("aaaaaa")

        val started = CountDownLatch(1)
        val completed = CountDownLatch(1)
        val producer =
            Thread {
                started.countDown()
                queue.put("bbbbbb")
                completed.countDown()
            }
        producer.start()
        started.await()

        Assertions.assertFalse(
            completed.await(1, TimeUnit.SECONDS),
            "put() should block while the queue is over its byte budget",
        )
        // The blocked element is not yet accounted for.
        Assertions.assertEquals(6L, queue.currentByteSizeEstimate)

        // Draining one element frees byte budget and should unblock the producer.
        Assertions.assertEquals("aaaaaa", queue.poll())
        Assertions.assertTrue(
            completed.await(5, TimeUnit.SECONDS),
            "put() should resume once a poll() frees byte budget",
        )
        Assertions.assertEquals(6L, queue.currentByteSizeEstimate)
        producer.join(TimeUnit.SECONDS.toMillis(5))
    }

    @Test
    @Timeout(15)
    fun admitsOversizedElementIntoEmptyQueueWithoutBlocking() {
        // A single element larger than the whole budget must still be admitted into an empty queue
        // so the pipeline cannot deadlock.
        val queue = stringQueue(capacity = 100, maxSizeInBytes = 4)

        queue.put("way too big") // 11 bytes > 4 byte budget, but queue is empty
        Assertions.assertEquals(11L, queue.currentByteSizeEstimate)

        Assertions.assertEquals("way too big", queue.poll())
        Assertions.assertEquals(0L, queue.currentByteSizeEstimate)
    }

    @Test
    @Timeout(15)
    fun enforcesCountCapacityAsSecondaryCap() {
        // With an effectively unlimited byte budget, the count-based capacity must still bound the
        // queue exactly as before.
        val queue = stringQueue(capacity = 2, maxSizeInBytes = Long.MAX_VALUE)
        queue.put("a")
        queue.put("b")

        val completed = CountDownLatch(1)
        val producer =
            Thread {
                queue.put("c")
                completed.countDown()
            }
        producer.start()

        Assertions.assertFalse(
            completed.await(1, TimeUnit.SECONDS),
            "put() should block when the count capacity is reached",
        )

        Assertions.assertEquals("a", queue.poll())
        Assertions.assertTrue(
            completed.await(5, TimeUnit.SECONDS),
            "put() should resume once the count capacity frees up",
        )
        producer.join(TimeUnit.SECONDS.toMillis(5))
    }
}
