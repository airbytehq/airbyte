/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import io.airbyte.cdk.integrations.destination.async.buffers.BufferDequeue
import io.airbyte.cdk.integrations.destination.async.buffers.MemoryAwareMessageBatch
import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.state.FlushFailure
import io.airbyte.cdk.integrations.destination.async.state.GlobalAsyncStateManager
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.Optional
import java.util.concurrent.CountDownLatch
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger
import java.util.function.Consumer
import java.util.stream.Stream
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito
import org.mockito.kotlin.any

/**
 * Tests for [FlushWorkers], specifically the double-dispatch guard in retrieveWork().
 *
 * Verifies that a single scheduling cycle never dispatches two workers for the same stream, which
 * could cause S3 key collisions and silent data loss. See:
 * https://github.com/airbytehq/airbyte/issues/76263
 */
class FlushWorkersTest {

    private val SIZE_50MB = (50 * 1024 * 1024).toLong()
    private val SIZE_150MB = (150 * 1024 * 1024).toLong()

    private val STREAM1 = StreamDescriptor().withNamespace("ns").withName("stream1")

    private lateinit var bufferDequeue: BufferDequeue
    private lateinit var outputRecordCollector: Consumer<AirbyteMessage>
    private lateinit var flushFailure: FlushFailure
    private lateinit var stateManager: GlobalAsyncStateManager

    @BeforeEach
    internal fun setup() {
        bufferDequeue = Mockito.mock(BufferDequeue::class.java)
        @Suppress("UNCHECKED_CAST")
        outputRecordCollector = Mockito.mock(Consumer::class.java) as Consumer<AirbyteMessage>
        flushFailure = FlushFailure()
        stateManager = Mockito.mock(GlobalAsyncStateManager::class.java)
    }

    /**
     * Reproduces the scenario from issue #76263:
     * - A single stream has a large queue (e.g. 150 MB with 50 MB optimal batch).
     * - Multiple worker threads are available.
     * - DetectStreamToFlush repeatedly returns the same stream because the penalty estimate for
     * just-dispatched (but not yet dequeued) workers is insufficient.
     *
     * Before the fix, this resulted in multiple workers for the same stream in a single cycle.
     * After the fix, only one worker should be dispatched per stream per cycle.
     */
    @Test
    internal fun testRetrieveWorkNeverDispatchesSameStreamTwiceInOneCycle() {
        val flushCallCount = AtomicInteger(0)
        val flushStartedLatch = CountDownLatch(1)

        val realFlusher =
            object : DestinationFlushFunction {
                override val optimalBatchSizeBytes: Long = SIZE_50MB
                override val queueFlushThresholdBytes: Long = SIZE_50MB

                override fun flush(
                    streamDescriptor: StreamDescriptor,
                    stream: Stream<PartialAirbyteMessage>
                ) {
                    flushCallCount.incrementAndGet()
                    flushStartedLatch.countDown()
                }
            }

        // Simulate a large queue for STREAM1 — big enough to trigger multiple flushes
        Mockito.`when`(bufferDequeue.bufferedStreams).thenReturn(setOf(STREAM1))
        Mockito.`when`(bufferDequeue.getQueueSizeBytes(STREAM1)).thenReturn(Optional.of(SIZE_150MB))
        // Return 0 records so close() completes immediately
        Mockito.`when`(bufferDequeue.getQueueSizeInRecords(STREAM1)).thenReturn(Optional.of(0L))
        Mockito.`when`(bufferDequeue.getTimeOfLastRecord(STREAM1))
            .thenReturn(Optional.of(java.time.Instant.now()))
        Mockito.`when`(bufferDequeue.totalGlobalQueueSizeBytes).thenReturn(SIZE_150MB)
        Mockito.`when`(bufferDequeue.maxQueueSizeBytes).thenReturn(SIZE_150MB * 10)

        val emptyBatch = Mockito.mock(MemoryAwareMessageBatch::class.java)
        Mockito.`when`(emptyBatch.data).thenReturn(emptyList())
        Mockito.`when`(emptyBatch.sizeInBytes).thenReturn(0L)
        Mockito.`when`(bufferDequeue.take(any(), any())).thenReturn(emptyBatch)

        val workerPool = Executors.newFixedThreadPool(5)

        val flushWorkers =
            FlushWorkers(
                bufferDequeue,
                realFlusher,
                outputRecordCollector,
                flushFailure,
                stateManager,
                workerPool,
            )

        try {
            flushWorkers.start()

            // Wait for at least one flush to start (supervisor runs every 1s)
            val started = flushStartedLatch.await(5, TimeUnit.SECONDS)
            assertTrue(started, "Expected at least one flush to start within 5 seconds")

            // Give enough time for any additional (erroneous) dispatches to settle
            Thread.sleep(500)

            // The key assertion: only one worker should have been dispatched for
            // STREAM1 in a single scheduling cycle, even though multiple threads
            // were available and the queue was large enough for multiple batches.
            assertEquals(
                1,
                flushCallCount.get(),
                "Expected exactly 1 flush dispatch for STREAM1 per cycle, but got ${flushCallCount.get()}. " +
                    "This indicates the double-dispatch guard is not working."
            )
        } finally {
            flushWorkers.close()
            workerPool.shutdownNow()
        }
    }

    /**
     * Verifies that the double-dispatch guard is scoped to a single scheduling cycle.
     * DetectStreamToFlush uses an internal RunningFlushWorkers instance, so we verify indirectly
     * that the guard does not permanently block a stream — a stream dispatched in cycle N should
     * still be eligible in cycle N+1 (assuming the first worker completed).
     *
     * This test uses two scheduling cycles (each 1 second apart) to verify that STREAM1 is
     * dispatched once per cycle, totalling at least 2 flush calls across the test window.
     */
    @Test
    internal fun testStreamCanBeRedispatchedInSubsequentCycles() {
        val flushCallCount = AtomicInteger(0)
        val secondFlushLatch = CountDownLatch(2)

        val realFlusher =
            object : DestinationFlushFunction {
                override val optimalBatchSizeBytes: Long = SIZE_50MB
                override val queueFlushThresholdBytes: Long = SIZE_50MB

                override fun flush(
                    streamDescriptor: StreamDescriptor,
                    stream: Stream<PartialAirbyteMessage>
                ) {
                    flushCallCount.incrementAndGet()
                    secondFlushLatch.countDown()
                }
            }

        Mockito.`when`(bufferDequeue.bufferedStreams).thenReturn(setOf(STREAM1))
        Mockito.`when`(bufferDequeue.getQueueSizeBytes(STREAM1)).thenReturn(Optional.of(SIZE_150MB))
        Mockito.`when`(bufferDequeue.getQueueSizeInRecords(STREAM1)).thenReturn(Optional.of(0L))
        Mockito.`when`(bufferDequeue.getTimeOfLastRecord(STREAM1))
            .thenReturn(Optional.of(java.time.Instant.now()))
        Mockito.`when`(bufferDequeue.totalGlobalQueueSizeBytes).thenReturn(SIZE_150MB)
        Mockito.`when`(bufferDequeue.maxQueueSizeBytes).thenReturn(SIZE_150MB * 10)

        val emptyBatch = Mockito.mock(MemoryAwareMessageBatch::class.java)
        Mockito.`when`(emptyBatch.data).thenReturn(emptyList())
        Mockito.`when`(emptyBatch.sizeInBytes).thenReturn(0L)
        Mockito.`when`(bufferDequeue.take(any(), any())).thenReturn(emptyBatch)

        val workerPool = Executors.newFixedThreadPool(5)

        val flushWorkers =
            FlushWorkers(
                bufferDequeue,
                realFlusher,
                outputRecordCollector,
                flushFailure,
                stateManager,
                workerPool,
            )

        try {
            flushWorkers.start()

            // Wait for at least two flush calls (across two scheduling cycles, ~2s apart)
            val reachedTwo = secondFlushLatch.await(10, TimeUnit.SECONDS)
            assertTrue(
                reachedTwo,
                "Expected the stream to be re-dispatched in a subsequent cycle (at least 2 flushes), " +
                    "but only saw ${flushCallCount.get()} within the timeout. " +
                    "The double-dispatch guard may be incorrectly persisting across cycles."
            )
        } finally {
            flushWorkers.close()
            workerPool.shutdownNow()
        }
    }
}
