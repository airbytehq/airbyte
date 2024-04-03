/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import io.airbyte.cdk.integrations.destination.async.buffers.BufferDequeue
import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import io.mockk.every
import io.mockk.mockk
import java.time.Clock
import java.util.Optional
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class FlushThresholdTest {
    companion object {
        private const val SIZE_10MB = (10 * 1024 * 1024).toLong()
    }

    private lateinit var bufferDequeue: BufferDequeue
    private lateinit var flusher: DestinationFlushFunction

    @BeforeEach
    internal fun setup() {
        bufferDequeue = mockk()
        flusher = mockk()

        every { bufferDequeue.getMaxQueueSizeBytes() } returns 10L
        every { bufferDequeue.getTotalGlobalQueueSizeBytes() } returns 0L
        every { flusher.queueFlushThresholdBytes } returns SIZE_10MB
    }

    @Test
    internal fun testBaseThreshold() {
        val runningFlushWorkers: RunningFlushWorkers = mockk()

        val detect =
            DetectStreamToFlush(
                bufferDequeue = bufferDequeue,
                runningFlushWorkers = runningFlushWorkers,
                destinationFlushFunction = flusher,
                airbyteFileUtils = AirbyteFileUtils(),
                nowProvider = Optional.of(Clock.systemUTC()),
            )

        assertEquals(SIZE_10MB, detect.computeQueueThreshold())
    }

    @Test
    internal fun testClosingThreshold() {
        val runningFlushWorkers: RunningFlushWorkers = mockk()

        val detect =
            DetectStreamToFlush(
                bufferDequeue = bufferDequeue,
                runningFlushWorkers = runningFlushWorkers,
                destinationFlushFunction = flusher,
                airbyteFileUtils = AirbyteFileUtils(),
                nowProvider = Optional.of(Clock.systemUTC()),
            )
        detect.flushAllStreams.set(true)

        assertEquals(0, detect.computeQueueThreshold())
    }

    @Test
    internal fun testEagerFlushThresholdBelowThreshold() {
        val runningFlushWorkers: RunningFlushWorkers = mockk()

        val detect =
            DetectStreamToFlush(
                bufferDequeue = bufferDequeue,
                runningFlushWorkers = runningFlushWorkers,
                destinationFlushFunction = flusher,
                airbyteFileUtils = AirbyteFileUtils(),
                nowProvider = Optional.of(Clock.systemUTC()),
            )

        assertEquals(SIZE_10MB, detect.computeQueueThreshold())
    }

    @Test
    internal fun testEagerFlushThresholdAboveThreshold() {
        val runningFlushWorkers: RunningFlushWorkers = mockk()

        every { bufferDequeue.getTotalGlobalQueueSizeBytes() } returns 9L

        val detect =
            DetectStreamToFlush(
                bufferDequeue = bufferDequeue,
                runningFlushWorkers = runningFlushWorkers,
                destinationFlushFunction = flusher,
                airbyteFileUtils = AirbyteFileUtils(),
                nowProvider = Optional.of(Clock.systemUTC()),
            )

        assertEquals(0, detect.computeQueueThreshold())
    }
}
