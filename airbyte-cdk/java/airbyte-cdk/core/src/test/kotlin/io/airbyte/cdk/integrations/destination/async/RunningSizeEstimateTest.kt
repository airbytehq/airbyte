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
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito

@SuppressFBWarnings(value = ["BC_IMPOSSIBLE_CAST"])
class RunningSizeEstimateTest {
    private val SIZE_10MB = (10 * 1024 * 1024).toLong()
    private val SIZE_20MB = (20 * 1024 * 1024).toLong()
    private val SIZE_200MB = (200 * 1024 * 1024).toLong()
    private val DESC1: StreamDescriptor = StreamDescriptor().withName("test1")

    private lateinit var flusher: DestinationFlushFunction

    @BeforeEach
    internal fun setup() {
        flusher = Mockito.mock(DestinationFlushFunction::class.java)
        Mockito.`when`(flusher.optimalBatchSizeBytes).thenReturn(SIZE_200MB)
    }

    @Test
    internal fun testEstimateZeroWorkers() {
        val bufferDequeue = Mockito.mock(BufferDequeue::class.java)
        val runningFlushWorkers =
            Mockito.mock(
                RunningFlushWorkers::class.java,
            )
        Mockito.`when`(
                runningFlushWorkers.getSizesOfRunningWorkerBatches(org.mockito.kotlin.any()),
            )
            .thenReturn(
                emptyList(),
            )
        val detect =
            DetectStreamToFlush(bufferDequeue, runningFlushWorkers, AtomicBoolean(false), flusher)
        Assertions.assertEquals(0, detect.estimateSizeOfRunningWorkers(DESC1, SIZE_10MB))
    }

    @Test
    internal fun testEstimateWorkerWithBatch() {
        val bufferDequeue = Mockito.mock(BufferDequeue::class.java)
        val runningFlushWorkers =
            Mockito.mock(
                RunningFlushWorkers::class.java,
            )
        Mockito.`when`(
                runningFlushWorkers.getSizesOfRunningWorkerBatches(org.mockito.kotlin.any()),
            )
            .thenReturn(
                listOf(
                    Optional.of(SIZE_20MB),
                ),
            )
        val detect =
            DetectStreamToFlush(bufferDequeue, runningFlushWorkers, AtomicBoolean(false), flusher)
        Assertions.assertEquals(SIZE_20MB, detect.estimateSizeOfRunningWorkers(DESC1, SIZE_10MB))
    }

    @Test
    internal fun testEstimateWorkerWithoutBatchAndQueueLessThanOptimalSize() {
        val bufferDequeue = Mockito.mock(BufferDequeue::class.java)
        val runningFlushWorkers =
            Mockito.mock(
                RunningFlushWorkers::class.java,
            )
        Mockito.`when`(
                runningFlushWorkers.getSizesOfRunningWorkerBatches(org.mockito.kotlin.any()),
            )
            .thenReturn(
                listOf(
                    Optional.empty(),
                ),
            )
        val detect =
            DetectStreamToFlush(bufferDequeue, runningFlushWorkers, AtomicBoolean(false), flusher)
        Assertions.assertEquals(SIZE_10MB, detect.estimateSizeOfRunningWorkers(DESC1, SIZE_10MB))
    }

    @Test
    internal fun testEstimateWorkerWithoutBatchAndQueueGreaterThanOptimalSize() {
        val bufferDequeue = Mockito.mock(BufferDequeue::class.java)
        val runningFlushWorkers =
            Mockito.mock(
                RunningFlushWorkers::class.java,
            )
        Mockito.`when`(
                runningFlushWorkers.getSizesOfRunningWorkerBatches(org.mockito.kotlin.any()),
            )
            .thenReturn(
                listOf(
                    Optional.empty(),
                ),
            )
        val detect =
            DetectStreamToFlush(bufferDequeue, runningFlushWorkers, AtomicBoolean(false), flusher)
        Assertions.assertEquals(
            SIZE_200MB,
            detect.estimateSizeOfRunningWorkers(DESC1, SIZE_200MB + 1),
        )
    }
}
