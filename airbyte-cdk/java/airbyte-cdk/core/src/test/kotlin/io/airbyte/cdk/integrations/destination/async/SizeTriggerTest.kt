/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.integrations.destination.async.buffers.BufferDequeue
import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.mockk.every
import io.mockk.mockk
import java.time.Clock
import java.util.Optional
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

@SuppressFBWarnings(value = ["BC_IMPOSSIBLE_CAST"])
class SizeTriggerTest {
    companion object {
        private const val SIZE_10MB = (10 * 1024 * 1024).toLong()
        private const val SIZE_200MB = (200 * 1024 * 1024).toLong()
        private val DESC1: StreamDescriptor = StreamDescriptor().withName("test1")
    }

    private lateinit var flusher: DestinationFlushFunction

    @BeforeEach
    internal fun setup() {
        flusher = mockk()
        every { flusher.optimalBatchSizeBytes } returns SIZE_200MB
    }

    @Test
    internal fun testSizeTriggerOnEmptyQueue() {
        val bufferDequeue: BufferDequeue = mockk()
        val runningFlushWorkers: RunningFlushWorkers = mockk()

        every { bufferDequeue.getBufferedStreams() } returns setOf(DESC1)
        every { bufferDequeue.getQueueSizeBytes(DESC1) } returns Optional.of(0L)
        every { runningFlushWorkers.getSizesOfRunningWorkerBatches(DESC1) } returns emptyList()

        val detect =
            DetectStreamToFlush(
                bufferDequeue = bufferDequeue,
                runningFlushWorkers = runningFlushWorkers,
                destinationFlushFunction = flusher,
                airbyteFileUtils = AirbyteFileUtils(),
                nowProvider = Optional.of(Clock.systemUTC()),
            )

        assertEquals(false, detect.isSizeTriggered(DESC1, SIZE_10MB).first)
    }

    @Test
    internal fun testSizeTriggerRespectsThreshold() {
        val bufferDequeue: BufferDequeue = mockk()
        val runningFlushWorkers: RunningFlushWorkers = mockk()

        every { bufferDequeue.getBufferedStreams() } returns setOf(DESC1)
        every { bufferDequeue.getQueueSizeBytes(DESC1) } returns Optional.of(1L)
        every { runningFlushWorkers.getSizesOfRunningWorkerBatches(DESC1) } returns emptyList()

        val detect =
            DetectStreamToFlush(
                bufferDequeue = bufferDequeue,
                runningFlushWorkers = runningFlushWorkers,
                destinationFlushFunction = flusher,
                airbyteFileUtils = AirbyteFileUtils(),
                nowProvider = Optional.of(Clock.systemUTC()),
            )

        // if above threshold, triggers
        assertEquals(true, detect.isSizeTriggered(DESC1, 0).first)
        // if below threshold, no trigger
        assertEquals(false, detect.isSizeTriggered(DESC1, SIZE_10MB).first)
    }

    @Test
    internal fun testSizeTriggerRespectsRunningWorkersEstimate() {
        val bufferDequeue: BufferDequeue = mockk()
        val runningFlushWorkers: RunningFlushWorkers = mockk()

        every { bufferDequeue.getBufferedStreams() } returns setOf(DESC1)
        every { bufferDequeue.getQueueSizeBytes(DESC1) } returns Optional.of(1L)
        every { runningFlushWorkers.getSizesOfRunningWorkerBatches(any()) } returns
            emptyList() andThen
            listOf(
                Optional.of(
                    SIZE_10MB,
                ),
            )

        val detect =
            DetectStreamToFlush(
                bufferDequeue = bufferDequeue,
                runningFlushWorkers = runningFlushWorkers,
                destinationFlushFunction = flusher,
                airbyteFileUtils = AirbyteFileUtils(),
                nowProvider = Optional.of(Clock.systemUTC()),
            )

        assertEquals(true, detect.isSizeTriggered(DESC1, 0).first)
        assertEquals(false, detect.isSizeTriggered(DESC1, 0).first)
    }
}
