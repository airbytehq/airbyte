/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.integrations.destination.async.buffers.BufferDequeue
import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.mockk.every
import io.mockk.mockk
import java.time.Clock
import java.time.Instant
import java.util.Optional
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

@SuppressFBWarnings(value = ["BC_IMPOSSIBLE_CAST"])
class StreamPriorityTest {
    companion object {
        private val NOW: Instant = Instant.now()
        private val FIVE_MIN_AGO: Instant = NOW.minusSeconds((60 * 5).toLong())
        private val DESC1: StreamDescriptor = StreamDescriptor().withName("test1")
        private val DESC2: StreamDescriptor = StreamDescriptor().withName("test2")
        private val DESCS: Set<StreamDescriptor> = setOf(DESC1, DESC2)
    }

    @Test
    internal fun testOrderByPrioritySize() {
        val bufferDequeue: BufferDequeue = mockk()
        val flusher: DestinationFlushFunction = mockk()
        val runningFlushWorkers: RunningFlushWorkers = mockk()

        every { bufferDequeue.getQueueSizeBytes(DESC1) } returns
            Optional.of(1L) andThen
            Optional.of(0L)
        every { bufferDequeue.getQueueSizeBytes(DESC2) } returns
            Optional.of(0L) andThen
            Optional.of(1L)
        every { bufferDequeue.getTimeOfLastRecord(any()) } returns Optional.of(NOW)

        val detect =
            DetectStreamToFlush(
                bufferDequeue = bufferDequeue,
                runningFlushWorkers = runningFlushWorkers,
                destinationFlushFunction = flusher,
                airbyteFileUtils = AirbyteFileUtils(),
                nowProvider = Optional.of(Clock.systemUTC()),
            )

        assertEquals(listOf(DESC1, DESC2), detect.orderStreamsByPriority(DESCS))
        assertEquals(listOf(DESC2, DESC1), detect.orderStreamsByPriority(DESCS))
    }

    @Test
    internal fun testOrderByPrioritySecondarySortByTime() {
        val bufferDequeue: BufferDequeue = mockk()
        val flusher: DestinationFlushFunction = mockk()
        val runningFlushWorkers: RunningFlushWorkers = mockk()

        every { bufferDequeue.getQueueSizeBytes(any()) } returns Optional.of(0L)
        every { bufferDequeue.getTimeOfLastRecord(DESC1) } returns
            Optional.of(FIVE_MIN_AGO) andThen
            Optional.of(NOW)
        every { bufferDequeue.getTimeOfLastRecord(DESC2) } returns
            Optional.of(NOW) andThen
            Optional.of(FIVE_MIN_AGO)

        val detect =
            DetectStreamToFlush(
                bufferDequeue = bufferDequeue,
                runningFlushWorkers = runningFlushWorkers,
                destinationFlushFunction = flusher,
                airbyteFileUtils = AirbyteFileUtils(),
                nowProvider = Optional.of(Clock.systemUTC()),
            )

        assertEquals(listOf(DESC1, DESC2), detect.orderStreamsByPriority(DESCS))
        assertEquals(listOf(DESC2, DESC1), detect.orderStreamsByPriority(DESCS))
    }

    @Test
    internal fun testOrderByPriorityTertiarySortByName() {
        val bufferDequeue: BufferDequeue = mockk()
        val flusher: DestinationFlushFunction = mockk()
        val runningFlushWorkers: RunningFlushWorkers = mockk()

        every { bufferDequeue.getQueueSizeBytes(any()) } returns Optional.of(0L)
        every { bufferDequeue.getTimeOfLastRecord(any()) } returns Optional.of(NOW)

        val detect =
            DetectStreamToFlush(
                bufferDequeue = bufferDequeue,
                runningFlushWorkers = runningFlushWorkers,
                destinationFlushFunction = flusher,
                airbyteFileUtils = AirbyteFileUtils(),
                nowProvider = Optional.of(Clock.systemUTC()),
            )

        val descs = listOf(Jsons.clone(DESC1), Jsons.clone(DESC2))
        assertEquals(
            listOf(
                descs[0],
                descs[1],
            ),
            detect.orderStreamsByPriority(HashSet(descs)),
        )
        descs[0].name = "test3"
        assertEquals(
            listOf(
                descs[1],
                descs[0],
            ),
            detect.orderStreamsByPriority(HashSet(descs)),
        )
    }
}
