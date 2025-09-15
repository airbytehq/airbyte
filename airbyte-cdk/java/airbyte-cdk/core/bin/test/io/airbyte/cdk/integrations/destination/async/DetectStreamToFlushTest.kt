/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.integrations.destination.async.buffers.BufferDequeue
import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.time.Clock
import java.time.Duration
import java.time.Instant
import java.util.Optional
import java.util.concurrent.atomic.AtomicBoolean
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito

@SuppressFBWarnings(value = ["BC_IMPOSSIBLE_CAST"])
class DetectStreamToFlushTest {
    val NOW: Instant = Instant.now()
    val FIVE_MIN: Duration = Duration.ofMinutes(5)
    private val SIZE_10MB = (10 * 1024 * 1024).toLong()
    private val SIZE_200MB = (200 * 1024 * 1024).toLong()

    private val DESC1: StreamDescriptor = StreamDescriptor().withName("test1")

    private lateinit var flusher: DestinationFlushFunction

    @BeforeEach
    internal fun setup() {
        flusher = Mockito.mock(DestinationFlushFunction::class.java)
        Mockito.`when`(flusher.optimalBatchSizeBytes).thenReturn(SIZE_200MB)
    }

    @Test
    internal fun testGetNextSkipsEmptyStreams() {
        val bufferDequeue =
            Mockito.mock(
                BufferDequeue::class.java,
            )
        Mockito.`when`(bufferDequeue.bufferedStreams).thenReturn(setOf(DESC1))
        Mockito.`when`(bufferDequeue.getQueueSizeBytes(DESC1)).thenReturn(Optional.of(0L))
        val runningFlushWorkers =
            Mockito.mock(
                RunningFlushWorkers::class.java,
            )

        val detect =
            DetectStreamToFlush(
                bufferDequeue,
                runningFlushWorkers,
                AtomicBoolean(false),
                flusher,
                flushOnEveryMessage = false
            )
        Assertions.assertEquals(Optional.empty<Any>(), detect.getNextStreamToFlush(0))
    }

    @Test
    internal fun testGetNextPicksUpOnSizeTrigger() {
        val bufferDequeue =
            Mockito.mock(
                BufferDequeue::class.java,
            )
        Mockito.`when`(bufferDequeue.bufferedStreams).thenReturn(setOf(DESC1))
        Mockito.`when`(bufferDequeue.getQueueSizeBytes(DESC1)).thenReturn(Optional.of(1L))
        val runningFlushWorkers =
            Mockito.mock(
                RunningFlushWorkers::class.java,
            )
        val detect =
            DetectStreamToFlush(
                bufferDequeue,
                runningFlushWorkers,
                AtomicBoolean(false),
                flusher,
                flushOnEveryMessage = false
            )
        // if above threshold, triggers
        Assertions.assertEquals(Optional.of(DESC1), detect.getNextStreamToFlush(0))
        // if below threshold, no trigger
        Assertions.assertEquals(Optional.empty<Any>(), detect.getNextStreamToFlush(1))
    }

    @Test
    internal fun testGetNextAccountsForAlreadyRunningWorkers() {
        val bufferDequeue =
            Mockito.mock(
                BufferDequeue::class.java,
            )
        Mockito.`when`(bufferDequeue.bufferedStreams).thenReturn(setOf(DESC1))
        Mockito.`when`(bufferDequeue.getQueueSizeBytes(DESC1)).thenReturn(Optional.of(1L))
        val runningFlushWorkers =
            Mockito.mock(
                RunningFlushWorkers::class.java,
            )
        Mockito.`when`(
                runningFlushWorkers.getSizesOfRunningWorkerBatches(org.mockito.kotlin.any()),
            )
            .thenReturn(
                listOf(
                    Optional.of(SIZE_10MB),
                ),
            )
        val detect =
            DetectStreamToFlush(
                bufferDequeue,
                runningFlushWorkers,
                AtomicBoolean(false),
                flusher,
                flushOnEveryMessage = false
            )
        Assertions.assertEquals(Optional.empty<Any>(), detect.getNextStreamToFlush(0))
    }

    @Test
    internal fun testFileTransfer() {
        val bufferDequeue =
            Mockito.mock(
                BufferDequeue::class.java,
            )
        Mockito.`when`(bufferDequeue.bufferedStreams).thenReturn(setOf(DESC1))
        Mockito.`when`(bufferDequeue.getQueueSizeBytes(DESC1)).thenReturn(Optional.of(0L))
        val runningFlushWorkers =
            Mockito.mock(
                RunningFlushWorkers::class.java,
            )

        val detect =
            DetectStreamToFlush(
                bufferDequeue,
                runningFlushWorkers,
                AtomicBoolean(false),
                flusher,
                flushOnEveryMessage = true
            )
        Assertions.assertEquals(0, detect.computeQueueThreshold())
        Assertions.assertEquals(Optional.of(DESC1), detect.getNextStreamToFlush(0))
    }

    @Test
    internal fun testGetNextPicksUpOnTimeTrigger() {
        val bufferDequeue =
            Mockito.mock(
                BufferDequeue::class.java,
            )
        Mockito.`when`(bufferDequeue.bufferedStreams).thenReturn(setOf(DESC1))
        Mockito.`when`(bufferDequeue.getQueueSizeBytes(DESC1)).thenReturn(Optional.of(1L))
        val mockedNowProvider = Mockito.mock(Clock::class.java)

        val runningFlushWorkers =
            Mockito.mock(
                RunningFlushWorkers::class.java,
            )
        Mockito.`when`(
                runningFlushWorkers.getSizesOfRunningWorkerBatches(org.mockito.kotlin.any()),
            )
            .thenReturn(
                listOf(
                    Optional.of(SIZE_10MB),
                ),
            )
        val detect =
            DetectStreamToFlush(
                bufferDequeue,
                runningFlushWorkers,
                AtomicBoolean(false),
                flusher,
                mockedNowProvider,
                flushOnEveryMessage = false
            )

        // initialize flush time
        Mockito.`when`(mockedNowProvider.millis()).thenReturn(NOW.toEpochMilli())

        Assertions.assertEquals(Optional.empty<Any>(), detect.getNextStreamToFlush(0))

        // check 5 minutes later
        Mockito.`when`(mockedNowProvider.millis()).thenReturn(NOW.plus(FIVE_MIN).toEpochMilli())

        Assertions.assertEquals(Optional.of(DESC1), detect.getNextStreamToFlush(0))

        // just flush once
        Assertions.assertEquals(Optional.empty<Any>(), detect.getNextStreamToFlush(0))

        // check another 5 minutes later
        Mockito.`when`(mockedNowProvider.millis())
            .thenReturn(NOW.plus(FIVE_MIN).plus(FIVE_MIN).toEpochMilli())
        Assertions.assertEquals(Optional.of(DESC1), detect.getNextStreamToFlush(0))
    }
}
