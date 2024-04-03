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
class RunningSizeEstimateTest {
    companion object {
        private const val SIZE_10MB = (10 * 1024 * 1024).toLong()
        private const val SIZE_20MB = (20 * 1024 * 1024).toLong()
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
    internal fun testEstimateZeroWorkers() {
        val bufferDequeue: BufferDequeue = mockk()
        val runningFlushWorkers: RunningFlushWorkers = mockk()

        every { runningFlushWorkers.getSizesOfRunningWorkerBatches(any()) } returns emptyList()

        val detect =
            DetectStreamToFlush(
                bufferDequeue = bufferDequeue,
                runningFlushWorkers = runningFlushWorkers,
                destinationFlushFunction = flusher,
                airbyteFileUtils = AirbyteFileUtils(),
                nowProvider = Optional.of(Clock.systemUTC()),
            )

        assertEquals(0, detect.estimateSizeOfRunningWorkers(DESC1, SIZE_10MB))
    }

    @Test
    internal fun testEstimateWorkerWithBatch() {
        val bufferDequeue: BufferDequeue = mockk()
        val runningFlushWorkers: RunningFlushWorkers = mockk()

        every { runningFlushWorkers.getSizesOfRunningWorkerBatches(any()) } returns
            listOf(Optional.of(SIZE_20MB))

        val detect =
            DetectStreamToFlush(
                bufferDequeue = bufferDequeue,
                runningFlushWorkers = runningFlushWorkers,
                destinationFlushFunction = flusher,
                airbyteFileUtils = AirbyteFileUtils(),
                nowProvider = Optional.of(Clock.systemUTC()),
            )

        assertEquals(SIZE_20MB, detect.estimateSizeOfRunningWorkers(DESC1, SIZE_10MB))
    }

    @Test
    internal fun testEstimateWorkerWithoutBatchAndQueueLessThanOptimalSize() {
        val bufferDequeue: BufferDequeue = mockk()
        val runningFlushWorkers: RunningFlushWorkers = mockk()

        every { runningFlushWorkers.getSizesOfRunningWorkerBatches(any()) } returns
            listOf(Optional.empty())

        val detect =
            DetectStreamToFlush(
                bufferDequeue = bufferDequeue,
                runningFlushWorkers = runningFlushWorkers,
                destinationFlushFunction = flusher,
                airbyteFileUtils = AirbyteFileUtils(),
                nowProvider = Optional.of(Clock.systemUTC()),
            )

        assertEquals(SIZE_10MB, detect.estimateSizeOfRunningWorkers(DESC1, SIZE_10MB))
    }

    @Test
    internal fun testEstimateWorkerWithoutBatchAndQueueGreaterThanOptimalSize() {
        val bufferDequeue: BufferDequeue = mockk()
        val runningFlushWorkers: RunningFlushWorkers = mockk()

        every { runningFlushWorkers.getSizesOfRunningWorkerBatches(any()) } returns
            listOf(Optional.empty())

        val detect =
            DetectStreamToFlush(
                bufferDequeue = bufferDequeue,
                runningFlushWorkers = runningFlushWorkers,
                destinationFlushFunction = flusher,
                airbyteFileUtils = AirbyteFileUtils(),
                nowProvider = Optional.of(Clock.systemUTC()),
            )
        assertEquals(SIZE_200MB, detect.estimateSizeOfRunningWorkers(DESC1, SIZE_200MB + 1))
    }
}
