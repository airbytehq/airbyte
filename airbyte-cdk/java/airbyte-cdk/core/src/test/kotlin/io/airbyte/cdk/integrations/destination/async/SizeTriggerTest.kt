/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.integrations.destination.async.buffers.BufferDequeue
import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.Optional
import java.util.concurrent.atomic.AtomicBoolean
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito

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
        flusher = Mockito.mock(DestinationFlushFunction::class.java)
        Mockito.`when`(flusher.optimalBatchSizeBytes).thenReturn(SIZE_200MB)
    }

    @Test
    internal fun testSizeTriggerOnEmptyQueue() {
        val bufferDequeue =
            Mockito.mock(
                BufferDequeue::class.java,
            )
        val runningFlushWorkers =
            Mockito.mock(
                RunningFlushWorkers::class.java,
            )
        Mockito.`when`(bufferDequeue.bufferedStreams).thenReturn(setOf(DESC1))
        Mockito.`when`(bufferDequeue.getQueueSizeBytes(DESC1)).thenReturn(Optional.of(0L))
        val detect =
            DetectStreamToFlush(bufferDequeue, runningFlushWorkers, AtomicBoolean(false), flusher)
        assertEquals(false, detect.isSizeTriggered(DESC1, SIZE_10MB).first)
    }

    @Test
    internal fun testSizeTriggerRespectsThreshold() {
        val bufferDequeue =
            Mockito.mock(
                BufferDequeue::class.java,
            )
        val runningFlushWorkers =
            Mockito.mock(
                RunningFlushWorkers::class.java,
            )
        Mockito.`when`(bufferDequeue.bufferedStreams).thenReturn(setOf(DESC1))
        Mockito.`when`(bufferDequeue.getQueueSizeBytes(DESC1)).thenReturn(Optional.of(1L))
        val detect =
            DetectStreamToFlush(bufferDequeue, runningFlushWorkers, AtomicBoolean(false), flusher)
        // if above threshold, triggers
        assertEquals(true, detect.isSizeTriggered(DESC1, 0).first)
        // if below threshold, no trigger
        assertEquals(false, detect.isSizeTriggered(DESC1, SIZE_10MB).first)
    }

    @Test
    internal fun testSizeTriggerRespectsRunningWorkersEstimate() {
        val bufferDequeue =
            Mockito.mock(
                BufferDequeue::class.java,
            )
        val runningFlushWorkers =
            Mockito.mock(
                RunningFlushWorkers::class.java,
            )
        Mockito.`when`(bufferDequeue.bufferedStreams).thenReturn(setOf(DESC1))
        Mockito.`when`(bufferDequeue.getQueueSizeBytes(DESC1)).thenReturn(Optional.of(1L))
        Mockito.`when`(runningFlushWorkers.getSizesOfRunningWorkerBatches(org.mockito.kotlin.any()))
            .thenReturn(emptyList())
            .thenReturn(listOf(Optional.of(SIZE_10MB)))
        val detect =
            DetectStreamToFlush(bufferDequeue, runningFlushWorkers, AtomicBoolean(false), flusher)
        assertEquals(true, detect.isSizeTriggered(DESC1, 0).first)
        assertEquals(false, detect.isSizeTriggered(DESC1, 0).first)
    }
}
