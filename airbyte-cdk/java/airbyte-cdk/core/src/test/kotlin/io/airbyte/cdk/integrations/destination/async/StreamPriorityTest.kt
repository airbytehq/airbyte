/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.integrations.destination.async.buffers.BufferDequeue
import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.time.Instant
import java.util.Optional
import java.util.concurrent.atomic.AtomicBoolean
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito

@SuppressFBWarnings(value = ["BC_IMPOSSIBLE_CAST"])
class StreamPriorityTest {
    val NOW: Instant = Instant.now()
    val FIVE_MIN_AGO: Instant = NOW.minusSeconds((60 * 5).toLong())
    private val DESC1: StreamDescriptor = StreamDescriptor().withName("test1")
    private val DESC2: StreamDescriptor = StreamDescriptor().withName("test2")
    private val DESCS: Set<StreamDescriptor> = java.util.Set.of(DESC1, DESC2)

    @Test
    internal fun testOrderByPrioritySize() {
        val bufferDequeue =
            Mockito.mock(
                BufferDequeue::class.java,
            )
        val flusher = Mockito.mock(DestinationFlushFunction::class.java)
        val runningFlushWorkers = Mockito.mock(RunningFlushWorkers::class.java)
        Mockito.`when`(
                bufferDequeue.getQueueSizeBytes(DESC1),
            )
            .thenReturn(Optional.of(1L))
            .thenReturn(Optional.of(0L))
        Mockito.`when`(
                bufferDequeue.getQueueSizeBytes(DESC2),
            )
            .thenReturn(Optional.of(0L))
            .thenReturn(Optional.of(1L))
        val detect =
            DetectStreamToFlush(bufferDequeue, runningFlushWorkers, AtomicBoolean(false), flusher)

        Assertions.assertEquals(listOf(DESC1, DESC2), detect.orderStreamsByPriority(DESCS))
        Assertions.assertEquals(listOf(DESC2, DESC1), detect.orderStreamsByPriority(DESCS))
    }

    @Test
    internal fun testOrderByPrioritySecondarySortByTime() {
        val bufferDequeue =
            Mockito.mock(
                BufferDequeue::class.java,
            )
        val flusher = Mockito.mock(DestinationFlushFunction::class.java)
        val runningFlushWorkers = Mockito.mock(RunningFlushWorkers::class.java)
        Mockito.`when`(
                bufferDequeue.getQueueSizeBytes(org.mockito.kotlin.any()),
            )
            .thenReturn(Optional.of(0L))
        Mockito.`when`(
                bufferDequeue.getTimeOfLastRecord(DESC1),
            )
            .thenReturn(Optional.of(FIVE_MIN_AGO))
            .thenReturn(Optional.of(NOW))
        Mockito.`when`(bufferDequeue.getTimeOfLastRecord(DESC2))
            .thenReturn(Optional.of(NOW))
            .thenReturn(Optional.of(FIVE_MIN_AGO))
        val detect =
            DetectStreamToFlush(bufferDequeue, runningFlushWorkers, AtomicBoolean(false), flusher)
        Assertions.assertEquals(listOf(DESC1, DESC2), detect.orderStreamsByPriority(DESCS))
        Assertions.assertEquals(listOf(DESC2, DESC1), detect.orderStreamsByPriority(DESCS))
    }

    @Test
    internal fun testOrderByPriorityTertiarySortByName() {
        val bufferDequeue =
            Mockito.mock(
                BufferDequeue::class.java,
            )
        val flusher = Mockito.mock(DestinationFlushFunction::class.java)
        val runningFlushWorkers = Mockito.mock(RunningFlushWorkers::class.java)
        Mockito.`when`(
                bufferDequeue.getQueueSizeBytes(org.mockito.kotlin.any()),
            )
            .thenReturn(Optional.of(0L))
        Mockito.`when`(
                bufferDequeue.getTimeOfLastRecord(org.mockito.kotlin.any()),
            )
            .thenReturn(Optional.of(NOW))
        val detect =
            DetectStreamToFlush(bufferDequeue, runningFlushWorkers, AtomicBoolean(false), flusher)
        val descs = listOf(Jsons.clone(DESC1), Jsons.clone(DESC2))
        Assertions.assertEquals(
            listOf(
                descs[0],
                descs[1],
            ),
            detect.orderStreamsByPriority(HashSet(descs)),
        )
        descs[0].name = "test3"
        Assertions.assertEquals(
            listOf(
                descs[1],
                descs[0],
            ),
            detect.orderStreamsByPriority(HashSet(descs)),
        )
    }
}
