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
import java.time.Duration
import java.time.Instant
import java.util.Optional
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

@SuppressFBWarnings(value = ["BC_IMPOSSIBLE_CAST"])
class DetectStreamToFlushTest {
    companion object {
        val NOW: Instant = Instant.now()
        val FIVE_MIN: Duration = Duration.ofMinutes(5)
        private const val SIZE_10MB = (10 * 1024 * 1024).toLong()
        private const val SIZE_200MB = (200 * 1024 * 1024).toLong()
        private val DESC1: StreamDescriptor = StreamDescriptor().withName("test1")
    }

    private lateinit var bufferDequeue: BufferDequeue
    private lateinit var flusher: DestinationFlushFunction
    private lateinit var runningFlushWorkers: RunningFlushWorkers

    @BeforeEach
    internal fun setup() {
        bufferDequeue = mockk()
        flusher = mockk()
        runningFlushWorkers = mockk()

        every { bufferDequeue.getTimeOfLastRecord(any()) } returns Optional.of(NOW)
        every { flusher.optimalBatchSizeBytes } returns SIZE_200MB
        every { runningFlushWorkers.getSizesOfRunningWorkerBatches(any()) } returns
            listOf(Optional.of(0L))
    }

    @Test
    internal fun testGetNextSkipsEmptyStreams() {
        every { bufferDequeue.getBufferedStreams() } returns setOf(DESC1)
        every { bufferDequeue.getQueueSizeBytes(DESC1) } returns Optional.of(0L)
        every { bufferDequeue.getTimeOfLastRecord(DESC1) } returns Optional.of(NOW)

        val detect =
            DetectStreamToFlush(
                bufferDequeue = bufferDequeue,
                runningFlushWorkers = runningFlushWorkers,
                destinationFlushFunction = flusher,
                airbyteFileUtils = AirbyteFileUtils(),
                nowProvider = Optional.of(Clock.systemUTC()),
            )
        assertEquals(Optional.empty<Any>(), detect.getNextStreamToFlush(0))
    }

    @Test
    internal fun testGetNextPicksUpOnSizeTrigger() {
        every { bufferDequeue.getBufferedStreams() } returns setOf(DESC1)
        every { bufferDequeue.getQueueSizeBytes(DESC1) } returns Optional.of(1L)

        val detect =
            DetectStreamToFlush(
                bufferDequeue = bufferDequeue,
                runningFlushWorkers = runningFlushWorkers,
                destinationFlushFunction = flusher,
                airbyteFileUtils = AirbyteFileUtils(),
                nowProvider = Optional.of(Clock.systemUTC()),
            )

        // if above threshold, triggers
        assertEquals(Optional.of(DESC1), detect.getNextStreamToFlush(0))
        // if below threshold, no trigger
        assertEquals(Optional.empty<Any>(), detect.getNextStreamToFlush(1))
    }

    @Test
    internal fun testGetNextAccountsForAlreadyRunningWorkers() {
        every { bufferDequeue.getBufferedStreams() } returns setOf(DESC1)
        every { bufferDequeue.getQueueSizeBytes(DESC1) } returns Optional.of(1L)
        every { runningFlushWorkers.getSizesOfRunningWorkerBatches(any()) } returns
            listOf(Optional.of(SIZE_10MB))

        val detect =
            DetectStreamToFlush(
                bufferDequeue = bufferDequeue,
                runningFlushWorkers = runningFlushWorkers,
                destinationFlushFunction = flusher,
                airbyteFileUtils = AirbyteFileUtils(),
                nowProvider = Optional.of(Clock.systemUTC()),
            )
        assertEquals(Optional.empty<Any>(), detect.getNextStreamToFlush(0))
    }

    @Test
    internal fun testGetNextPicksUpOnTimeTrigger() {
        val mockedNowProvider: Clock = mockk()

        every { bufferDequeue.getBufferedStreams() } returns setOf(DESC1)
        every { bufferDequeue.getQueueSizeBytes(DESC1) } returns Optional.of(1L)
        every { runningFlushWorkers.getSizesOfRunningWorkerBatches(any()) } returns
            listOf(Optional.of(SIZE_10MB))
        // initialize flush time
        every { mockedNowProvider.millis() } returns NOW.toEpochMilli()

        val detect =
            DetectStreamToFlush(
                bufferDequeue = bufferDequeue,
                runningFlushWorkers = runningFlushWorkers,
                destinationFlushFunction = flusher,
                airbyteFileUtils = AirbyteFileUtils(),
                nowProvider = Optional.of(mockedNowProvider),
            )

        assertEquals(Optional.empty<Any>(), detect.getNextStreamToFlush(0))

        // check 5 minutes later
        every { mockedNowProvider.millis() } returns NOW.plus(FIVE_MIN).toEpochMilli()
        assertEquals(Optional.of(DESC1), detect.getNextStreamToFlush(0))

        // just flush once
        assertEquals(Optional.empty<Any>(), detect.getNextStreamToFlush(0))

        // check another 5 minutes later
        every { mockedNowProvider.millis() } returns
            NOW.plus(FIVE_MIN).plus(FIVE_MIN).toEpochMilli()
        assertEquals(Optional.of(DESC1), detect.getNextStreamToFlush(0))
    }
}
