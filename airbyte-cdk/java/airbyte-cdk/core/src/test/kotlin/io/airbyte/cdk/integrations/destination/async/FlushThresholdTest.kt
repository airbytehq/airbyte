/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import io.airbyte.cdk.integrations.destination.async.buffers.BufferDequeue
import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import java.util.concurrent.atomic.AtomicBoolean
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito

class FlushThresholdTest {
    private val SIZE_10MB = (10 * 1024 * 1024).toLong()

    private lateinit var flusher: DestinationFlushFunction

    @BeforeEach
    internal fun setup() {
        flusher = Mockito.mock(DestinationFlushFunction::class.java)
        Mockito.`when`(flusher.queueFlushThresholdBytes).thenReturn(SIZE_10MB)
    }

    @Test
    internal fun testBaseThreshold() {
        val isClosing = AtomicBoolean(false)
        val bufferDequeue =
            Mockito.mock(
                BufferDequeue::class.java,
            )
        val detect =
            DetectStreamToFlush(
                bufferDequeue,
                Mockito.mock(RunningFlushWorkers::class.java),
                isClosing,
                flusher,
            )
        Assertions.assertEquals(SIZE_10MB, detect.computeQueueThreshold())
    }

    @Test
    internal fun testClosingThreshold() {
        val isClosing = AtomicBoolean(true)
        val bufferDequeue =
            Mockito.mock(
                BufferDequeue::class.java,
            )
        val detect =
            DetectStreamToFlush(
                bufferDequeue,
                Mockito.mock(RunningFlushWorkers::class.java),
                isClosing,
                flusher,
            )
        Assertions.assertEquals(0, detect.computeQueueThreshold())
    }

    @Test
    internal fun testEagerFlushThresholdBelowThreshold() {
        val isClosing = AtomicBoolean(false)
        val bufferDequeue =
            Mockito.mock(
                BufferDequeue::class.java,
            )
        Mockito.`when`(bufferDequeue.totalGlobalQueueSizeBytes).thenReturn(8L)
        Mockito.`when`(bufferDequeue.maxQueueSizeBytes).thenReturn(10L)
        val detect =
            DetectStreamToFlush(
                bufferDequeue,
                Mockito.mock(RunningFlushWorkers::class.java),
                isClosing,
                flusher,
            )
        Assertions.assertEquals(SIZE_10MB, detect.computeQueueThreshold())
    }

    @Test
    internal fun testEagerFlushThresholdAboveThreshold() {
        val isClosing = AtomicBoolean(false)
        val bufferDequeue =
            Mockito.mock(
                BufferDequeue::class.java,
            )
        Mockito.`when`(bufferDequeue.totalGlobalQueueSizeBytes).thenReturn(9L)
        Mockito.`when`(bufferDequeue.maxQueueSizeBytes).thenReturn(10L)
        val detect =
            DetectStreamToFlush(
                bufferDequeue,
                Mockito.mock(RunningFlushWorkers::class.java),
                isClosing,
                flusher,
            )
        Assertions.assertEquals(0, detect.computeQueueThreshold())
    }
}
